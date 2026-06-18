# sources/distributed-fs/ceph-client/kernel/kexec.c

## Purpose
Implements the legacy `kexec_load` syscall path. It loads a replacement kernel image or crash kernel from userspace segments, prepares architecture-specific state, installs it as the active kexec image, or unloads an existing image.

## Important APIs, Types, and Functions
Main functions are `kimage_alloc_init`, `do_kexec_load`, `kexec_load_check`, `SYSCALL_DEFINE4(kexec_load)`, and the compat syscall. It manipulates global `kexec_image` and `kexec_crash_image`, calls `machine_kexec_prepare`, `machine_kexec_post_load`, `kimage_load_segment`, `kimage_terminate`, and crash-memory helpers.

## Control Flow
Syscall entry checks permissions, LSM/IMA/lockdown policy, flag validity, segment count, and architecture bits. It copies userspace segment descriptors, serializes with `kexec_trylock`, handles unload when `nr_segments == 0`, frees any old crash image if needed, allocates and validates a `kimage`, allocates control/swap pages, prepares the machine, copies vmcoreinfo, loads segments, terminates the image, runs post-load hooks, and atomically exchanges the installed image pointer.

## State and Persistence
Loaded images persist in memory through global pointers until replaced, unloaded, executed, or freed. Crash kernels may occupy protected reserved crash memory. No disk state is written; userspace must handle filesystem sync/unmount before rebooting into kexec.

## Dependencies and Integration Points
Depends on capabilities, `kexec_load_permitted`, LSM `security_kernel_load_data`, lockdown, usercopy helpers, crash dump/hotplug support, architecture kexec hooks, vmcoreinfo, and internal kimage allocation/loading routines.

## Risks
This is a high-impact syscall: it can replace the running kernel. Segment validation, architecture matching, crash reserved-memory bounds, and lockdown checks must be correct. Error paths must free partially allocated control pages/images and re-protect crash memory when needed.

## Test Signals
Expected errors include `-EPERM`, `-EINVAL`, `-ENOMEM`, `-EBUSY`, `-EADDRNOTAVAIL`, and architecture hook failures. Functional validation comes from kexec/kdump tests that load, unload, crash-load, and boot into prepared images.
