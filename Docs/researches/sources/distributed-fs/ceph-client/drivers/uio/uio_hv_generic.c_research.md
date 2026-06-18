# sources/distributed-fs/ceph-client/drivers/uio/uio_hv_generic.c

## Purpose
`uio_hv_generic.c` is a generic UIO driver for Hyper-V VMBus devices that are manually bound by dynamic ID. It exposes VMBus ring buffers, interrupt/monitor pages, and for network devices send/receive GPADL buffers to userspace, while translating VMBus channel callbacks into UIO events.

## Important APIs, Types, And Functions
Private state is `struct hv_uio_private_data`, embedding `struct uio_info`, the `hv_device`, an open refcount, receive/send buffers, GPADL descriptors, and map names. Key functions are `hv_uio_probe()`, `hv_uio_remove()`, `hv_uio_open()`, `hv_uio_release()`, `hv_uio_irqcontrol()`, `hv_uio_channel_cb()`, `hv_uio_rescind()`, `hv_uio_new_channel()`, `hv_uio_ring_mmap_prepare()`, and `hv_uio_cleanup()`.

## Control Flow And State
Probe allocates primary ring pages sized from the channel or 2 MiB default, sets channel read mode to ISR, fills UIO info with custom IRQ, open/release/irqcontrol callbacks, maps the TX/RX rings as `UIO_MEM_IOVA`, maps Hyper-V interrupt and monitor pages as logical memory, and for `HV_NIC` allocates large receive and send buffers, establishes GPADLs, and exposes them as virtual UIO maps named with GPADL handles. It registers UIO, creates ring sysfs compatibility files, and stores driver data.

Open increments a refcount; the first open installs rescind and subchannel callbacks and connects the primary ring. Release disconnects the primary ring on last close. VMBus events call `uio_event_notify()`. `irqcontrol` updates interrupt masks on the primary and all subchannels and signals the host when enabling on non-monitor channels. A rescind clears `info.irq`, notifies userspace so reads fail, and unregisters the VMBus device. Remove unregisters UIO, tears down GPADLs/buffers, removes ring sysfs, and frees rings.

## Dependencies And Integration Points
The driver depends on Hyper-V VMBus internals, UIO core, vmalloc, network device IDs for `HV_NIC`, GPADL setup/teardown, and dynamic VMBus driver IDs. It intentionally has no static ID table; userspace/admin scripts bind devices through sysfs.

## Risks And Edge Cases
The driver exposes low-level VMBus communication to userspace and can displace normal kernel drivers. Ring sysfs creation in probe is retained for compatibility despite race concerns. Buffer cleanup must respect decrypted GPADL state. Subchannel creation failures may leave only the primary channel usable. Rescind handling intentionally unregisters the device to keep VMBus offer state correct.

## Test Signals
Test dynamic ID bind/unbind, primary open/close refcounting, subchannel creation and ring sysfs mmap, UIO event delivery from primary and subchannels, irqcontrol masking/unmasking, NIC send/receive GPADL map naming and teardown, rescind behavior with blocked readers, and cleanup after partial GPADL allocation failures.
