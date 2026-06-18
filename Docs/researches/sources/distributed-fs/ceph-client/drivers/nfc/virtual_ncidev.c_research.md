# sources/distributed-fs/ceph-client/drivers/nfc/virtual_ncidev.c

## Purpose

This file implements a virtual NCI device exposed as a misc character device named `virtual_nci`. It is a simulation/testing bridge between user space and the kernel NFC NCI core: kernel NCI outbound frames become readable bytes on the misc device, and user-space writes are injected back into the NCI receive path.

## Important APIs, types, and functions

`struct virtual_nci_dev` stores the allocated `struct nci_dev`, a mutex, a single pending outbound `send_buff`, a wait queue, and a running flag. The NCI controller ops are `virtual_nci_open()`, `virtual_nci_close()`, and `virtual_nci_send()`. Character-device operations are `virtual_ncidev_open()`, `virtual_ncidev_close()`, `virtual_ncidev_read()`, `virtual_ncidev_write()`, and `virtual_ncidev_ioctl()`.

The only ioctl is `IOCTL_GET_NCIDEV_IDX`, which copies the associated `nfc_dev->idx` to user space. Registration is through `module_misc_device(miscdev)`.

## Control flow and state behavior

Opening `/dev/virtual_nci` allocates a private virtual device, allocates an NCI device with broad virtual protocol masks, initializes synchronization, stores the private data in the file, and registers the NCI device. NCI core open sets `running = true`; close frees any pending send buffer and clears running.

When the NCI core sends a frame, `virtual_nci_send()` takes the mutex, rejects the send if a previous frame is still pending or the device is not running, copies the SKB into `send_buff`, wakes readers, and consumes the original SKB. User-space reads block until `send_buff` is available, copy out up to `count` bytes, pull consumed bytes from the SKB, and free it when empty. User-space writes allocate an SKB, copy input bytes into it, and call `nci_recv_frame()` to inject it into the NFC core.

## Dependencies and integration points

The file depends on the NFC NCI core (`nci_allocate_device`, `nci_register_device`, `nci_recv_frame`), miscdevice infrastructure, user-copy helpers, mutexes, wait queues, and SKBs. It has no hardware dependencies and uses mode `0600`, limiting the device node to privileged or owner access.

## Risks and edge cases

The send path allows only one pending outbound SKB; if user space does not read promptly, subsequent NCI sends fail and drop their SKBs. `virtual_nci_send()` returns `-1` instead of a conventional negative errno. The read wait condition checks `send_buff` without explicitly considering device close, so blocked reads depend on file lifecycle and wakeups from send. `virtual_ncidev_close()` unregisters/free NCI state but does not explicitly free `send_buff` unless NCI close already ran. The code uses `kzalloc_obj(*vdev)`, which is a local macro/helper expectation in this source tree and should be verified against the kernel baseline.

## Test signals

Tests should open the device, obtain the NCI index via ioctl, bring the NCI device up, verify outbound NCI frames become readable in partial and full reads, verify writes are delivered to `nci_recv_frame()`, exercise close while buffers are pending, attempt concurrent readers/writers, and confirm send rejection when `running` is false or `send_buff` is occupied.
