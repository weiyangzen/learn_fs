# sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_main.c

## Purpose

`uverbs_main.c` registers and manages the userspace verbs character devices (`/dev/infiniband/uverbsN`). It owns module initialization, RDMA client attach/remove, uverbs file open/close, the legacy write command path, ioctl dispatch hookup, completion and async event file operations, mmap delegation and revocation, sysfs attributes, and device disassociation behavior.

## Important APIs, Types, and Functions

- `ib_uverbs_init()` and `ib_uverbs_cleanup()` register fixed/dynamic char-device ranges, the `infiniband_verbs` class, the ABI sysfs attribute, and the RDMA `ib_client`.
- `ib_uverbs_add_one()` creates one `ib_uverbs_device` for an RDMA device with `alloc_ucontext`, assigns a minor number, builds its UAPI, initializes the cdev, and exposes the device node.
- `ib_uverbs_remove_one()` removes the cdev and either waits for clients or disassociates hardware resources immediately when the provider supports `disassociate_ucontext`.
- `ib_uverbs_open()` allocates `ib_uverbs_file`, checks network namespace access, handles module ownership when needed, initializes uobject and mmap tracking, and links the file into the device list.
- `ib_uverbs_close()` destroys all ufile hardware resources and drops the file kref.
- `ib_uverbs_write()` implements the legacy `write()` ABI and extended write ABI, including header validation, `ib_udata` construction, method lookup, and NEW uobject finalization.
- Event helpers (`ib_uverbs_event_read()`, poll/fasync wrappers, `ib_uverbs_comp_handler()`, `ib_uverbs_async_handler()`, and object-specific event handlers) deliver CQ and async events through anon-inode/event FDs.
- Mmap helpers (`ib_uverbs_mmap()`, `rdma_umap_open()`, `rdma_umap_close()`, `rdma_umap_fault()`, `uverbs_user_mmap_disassociate()`, `rdma_user_mmap_disassociate()`) delegate provider mmap and revoke mappings during teardown/reset.

## Control Flow

At module load, the driver reserves major/minor ranges, registers the class, and registers as an RDMA client. When an eligible RDMA device appears, `ib_uverbs_add_one()` creates `ib_uverbs_device`, builds its ioctl/write API with `uverbs_alloc_api()`, attaches a cdev, and stores it as RDMA client data. Opening the device pins the uverbs device, validates namespace permissions, optionally pins the provider module, initializes per-file lists/locks, and sets up the file's uobject IDR.

Legacy writes flow through header copy, method lookup in `uapi->write_methods`, `verify_hdr()`, SRCU locking, `ib_udata` setup for core/provider buffers, handler invocation, and uobject finalization. Ioctls are delegated to `ib_uverbs_ioctl()` in `uverbs_ioctl.c`.

Provider removal first deletes the cdev. If the provider can disassociate ucontexts, the code blocks future driver methods, destroys per-file hardware resources, nulls provider UAPI pointers, and lets open file descriptors survive as error-returning handles. Otherwise, it waits until all open files close before freeing the uverbs device.

## State and Persistence Behavior

Persistent kernel state includes registered char-device numbers, class/sysfs state, one `ib_uverbs_device` per RDMA device, per-open `ib_uverbs_file`, uobject lists/IDRs, event queues, mmap tracking entries, xrcd tree state, and reference counts. Events are queued in memory until read, cleared on object/file release, or closed with `is_closed`. Mmap revocation replaces device mappings with zero pages or SIGBUS behavior after disassociation.

## Dependencies and Integration Points

This file integrates with the RDMA core client model (`ib_register_client`), provider `ib_device_ops`, `uverbs_uapi.c` for API construction/disassociation, `uverbs_ioctl.c` for ioctl dispatch, `rdma_core` for uobject teardown, and standard type files for event file operations and release helpers. It also exposes netlink device info through `ib_uverbs_get_nl_info()`, including ABI version and optional driver ID.

## Risks and Edge Cases

Important risks are open/remove races, provider module lifetime, ucontext visibility under SRCU, mmap lock ordering, event queue closure races, and cleanup of all per-file uobjects during forced removal. The code uses SRCU, krefs/refcounts, list mutexes, `hw_destroy_rwsem`, `disassociation_lock`, `umap_lock`, and explicit completion waits to manage those races. Compatibility risk exists in the legacy write header validator, including the special old `DESTROY_CQ` size workaround.

## Test Signals

Test signals include device open/close under provider removal, namespace access rejection, write ABI size validation, extended write response pointer validation, async/completion event read/poll/fasync behavior, mmap clone/close/disassociate paths, userspace access after disassociation returning `-EIO`, module unload with open files, and sysfs/netlink ABI reporting.
