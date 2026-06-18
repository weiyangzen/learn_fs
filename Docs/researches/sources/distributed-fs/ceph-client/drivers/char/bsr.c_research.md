# sources/distributed-fs/ceph-client/drivers/char/bsr.c

## Purpose

`bsr.c` is the IBM POWER Barrier Synchronization Register character driver. It discovers Open Firmware `ibm,bsr` nodes, creates one character device per BSR register/window, exposes size/stride/length attributes, and lets userspace `mmap()` cache-inhibited BSR hardware for fast synchronization.

## Important APIs, Types, And Functions

- `struct bsr_dev` stores physical address, mapped length, BSR byte size, stride, type/index, minor, cdev, device, and list node.
- Sysfs attributes: `bsr_size`, `bsr_stride`, and `bsr_length`.
- File operations: `bsr_open()` stores the selected `bsr_dev` in `private_data`; `bsr_mmap()` maps the hardware region noncached.
- Discovery/lifecycle: `bsr_add_node()`, `bsr_create_devs()`, `bsr_cleanup_devs()`, `bsr_init()`, and `bsr_exit()`.
- Global registries: `bsr_devs`, `total_bsr_devs`, `bsr_types[]`, `bsr_major`, and class `bsr_class`.

## Control Flow

Init finds the first `ibm,bsr` node, registers class `bsr`, allocates up to `BSR_MAX_DEVS` character minors, then iterates compatible nodes. For each node, `bsr_add_node()` reads matching `ibm,lock-stride` and `ibm,#lock-bytes` arrays, maps each `reg` resource to a `bsr_dev`, normalizes lengths between 4 KB and `PAGE_SIZE` down to 4 KB for sysfs, classifies by byte size, creates a cdev, and creates `/dev`/sysfs device names like `bsr8_0`. `mmap()` sets noncached page protection and maps either a 4 KB PFN for small regions or the full requested region if within `bsr_len`.

## State And Persistence Behavior

Persistent software state is the list of created BSR devices, allocated minors, class devices, and sysfs attributes. Hardware state is not owned by the driver; userspace writes directly to mapped BSR bytes. The driver does not serialize userspace access after mmap and does not persist data beyond device nodes.

## Dependencies And Integration Points

Dependencies include Open Firmware node/resource APIs, char device registration, sysfs device classes, noncached page protections, `remap_4k_pfn()`, and `io_remap_pfn_range()`. It integrates with IBM POWER firmware descriptions and userspace synchronization libraries that understand single-byte BSR writes and required `sync` barriers.

## Risks And Edge Cases

The hardware requires only single-byte writes, but the mmap interface cannot enforce access width; misuse can violate hardware rules. `BSR_MAX_DEVS` is fixed at 32, but `total_bsr_devs` is incremented by each node's property count without an explicit cap before `MKDEV()`/`cdev_add()`. Error cleanup removes all devices if any later node fails. `bsr_create_devs()` uses `of_find_compatible_node()` iteratively and must manage node references carefully. For 64 KB page kernels, regions larger than 4 KB but smaller than `PAGE_SIZE` are advertised as 4 KB and mapped through `remap_4k_pfn()`.

## Test Signals

Boot on POWER hardware or device-tree tests with `ibm,bsr` nodes. Verify character devices and sysfs attributes match `reg`, `ibm,lock-stride`, and `ibm,#lock-bytes`; mmap a 4 KB and larger region; confirm noncached mapping; and run a userspace synchronization loop using byte writes and full sync barriers. Static checks should validate minor overflow against `BSR_MAX_DEVS` and cleanup on partial failures.
