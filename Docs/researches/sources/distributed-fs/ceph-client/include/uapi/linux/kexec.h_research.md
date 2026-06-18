# sources/distributed-fs/ceph-client/include/uapi/linux/kexec.h

## Purpose
`kexec.h` defines flags, architecture identifiers, segment limits, and userspace segment layout for the `kexec_load` and `kexec_file_load` system calls.

## Important APIs, Types, and Functions
Flags include crash load, preserve context, update ELF core header, crash hotplug support, file unload, file crash load, no initramfs, debug, no CMA, and force DTB. `KEXEC_ARCH_*` constants encode target architecture in high bits masked by `KEXEC_ARCH_MASK`. `KEXEC_SEGMENT_MAX` is 16. In userspace, `struct kexec_segment` contains user buffer pointer/size and destination memory pointer/size.

## Control Flow
Userspace loads kernel images and optional initramfs/segments into reserved memory, optionally for crash kernels. On reboot or panic, the kernel jumps to the prepared image.

## State and Persistence
Loaded kexec image state persists in kernel memory until unloaded, replaced, executed, or rebooted. Crash-kernel state may interact with reserved memory and elfcorehdr updates.

## Dependencies and Integration Points
It includes `<linux/types.h>`. Integration points include kexec-tools, crash dump infrastructure, architecture boot code, memory reservation, and secure/kernel image verification paths.

## Risks and Test Signals
Tests should cover flag validation, architecture mismatch rejection, segment overlap/bounds checking, max segment count, crash hotplug updates, unload behavior, and pointer-size compatibility for `kexec_segment`.
