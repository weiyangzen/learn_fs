# sources/distributed-fs/ceph-client/drivers/hv/mshv_root_main.c

## Purpose

`mshv_root_main.c` implements the `/dev/mshv` misc device and core root-partition VMM ABI. It creates partitions and VPs, runs VPs under Hyper-V or root scheduling, maps guest memory, handles VP state ioctls, passes audited hypercalls through to Hyper-V, and tears everything down.

## Important APIs, Types, and Functions

- File operations for the device, partition fds, and VP fds implement `MSHV_CREATE_PARTITION`, partition ioctls, VP ioctls, mmap, and release.
- `mshv_ioctl_create_partition()` validates feature/isolation flags, creates a Hyper-V partition, initializes locks/lists/SRCU/eventfd state, hashes the partition, and returns an anon fd.
- `mshv_partition_ioctl_create_vp()` creates a VP, maps intercept/register/GHCB pages, maps stats pages, creates debugfs, and returns an anon VP fd.
- `mshv_vp_ioctl_run_vp()` runs a VP, handles GPA intercepts internally for movable memory, and returns intercept messages to userspace.
- Memory ioctls map/unmap pinned RAM, movable RAM, or MMIO through `mshv_regions.c` and Hyper-V calls.
- Partition release drains eventfds/SRCU, drops refs, and `destroy_partition()` finalizes Hyper-V state, unmaps VPs/regions, withdraws deposited memory, deletes the partition, and frees routing tables.
- Module init registers `/dev/mshv`, initializes SynIC, VMM caps, scheduler buffers, debugfs, irqfd workqueue, partition hash, and the MSHV ISR handler.

## Control Flow

Users open `/dev/mshv`, create a partition fd, initialize the partition, register guest memory, create VPs, set routing/eventfds, and call `MSHV_RUN_VP` on VP fds. Hypervisor-scheduler mode resumes VP execution by clearing suspend registers and waits for SynIC kicks. Root-scheduler mode dispatches VPs directly with per-CPU input/output pages, handles guest-mode pending work, blocked dispatch state, explicit/intercept suspend, and injected vectors. GPA intercepts for movable regions are resolved in-kernel and the run loop continues; unhandled intercepts are copied to userspace.

## State and Persistence Behavior

`mshv_root` holds global VMM caps and partition hash. Partitions are refcounted and persist while fds/VPs reference them. VPs store mapped Hyper-V state pages and wait queues. Memory regions persist in a partition hlist. Async hypercall completion is per partition. Root scheduler buffers are per CPU. Module init state persists until module exit.

## Dependencies and Integration Points

The file integrates all MSHV subsystems: common register/property calls, root hypercall wrappers, regions, IRQ routing, eventfd, SynIC, debugfs, tracepoints, Linux anon inodes, miscdevice, cpuhp, reboot/panic context, guest-mode work, and UAPI `linux/mshv.h`.

## Risks and Edge Cases

The async hypercall guard appears inverted: `mshv_init_async_handler()` rejects when `completion_done()` is true, but a newly initialized completion starts done, so this path deserves review. VP creation error handling can jump to `free_vp` without setting `ret = -ENOMEM` after `kzalloc_obj(*vp)` failure. Root scheduler paths depend on stats counters to detect blocked dispatch threads. Partition teardown must drain root-scheduler VP signals before removing the RCU hash. Passthrough hypercalls are limited by allowlists but still copy arbitrary one-page input/output buffers from userspace.

## Test Signals

End-to-end tests should cover create/init/destroy partition, VP create/run/mmap/state get/set, memory map/unmap for pinned/movable/MMIO, GPA intercept resolution, irqfd/ioeventfd ioctls, MSI routing, passthrough hypercall allow/deny, root and non-root scheduler paths, debugfs lifecycle, module init failure unwinding, and concurrent fd release while SynIC messages arrive.
