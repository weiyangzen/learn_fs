# sources/distributed-fs/ceph-client/include/linux/kexec.h

## Purpose
Declares the kexec and crash-kexec core interfaces for loading a replacement kernel image, arranging relocation/control pages, preserving crash dump metadata, and entering the new kernel without firmware reboot.

## Important APIs, Types, And Functions
Common constants define kimage entry flag bits and legal syscall flags. Under `CONFIG_KEXEC_CORE`, important types include `kimage_entry_t`, `struct kexec_segment`, optional compat segment, file-mode `struct purgatory_info`, `struct kexec_file_ops`, `struct kexec_buf`, optional ELF info, and `struct kimage`. APIs include image probing/loading cleanup, purgatory loading/symbol access, buffer placement, relocation hooks, ELF loading, `machine_kexec*()`, `kernel_kexec()`, control page allocation, crash image globals, permission checks, boot-phys translation helpers, crash reserved range freeing, debug printing, and segment map/unmap.

## Control Flow
Userspace loads segments through kexec syscalls or file-mode loaders. The kernel validates architecture limits, optionally verifies signatures, locates memory holes for buffers, loads purgatory, builds segment/control lists, and later `kernel_kexec()` invokes machine-specific transition code. Crash kernels use reserved memory and crash notes/vmcore metadata.

## State And Persistence
`struct kimage` stores entry lists, segments, CMA pages, control/destination/unusable page lists, flags, file buffers, purgatory info, hotplug metadata, IMA buffer, kexec handover fields, ELF headers, and dm-crypt key buffer metadata. Loaded images persist in memory until executed or unloaded.

## Dependencies And Integration Points
Depends on architecture kexec definitions, vmcore/crash reservation, IO/physical address helpers, UAPI flags, verification, highmem, modules, ioport resources, ELF, CMA, IMA, crash hotplug, and optional signature verification. Integrates with panic/crash dump, reboot paths, security lockdown, and architecture relocation code.

## Risks
Segment placement must avoid reserved/excluded ranges and obey source/destination/control memory limits. Signature and permission checks are security boundaries. Crash kernels rely on reserved memory not being overwritten. Architecture relocation hooks may reject unsupported REL/RELA formats.

## Test Signals
Signals include kexec load/execute tests, kexec_file_load with signatures, crash kernel boot and vmcore capture, memory hole placement tests, hotplug update tests, IMA buffer preservation, purgatory symbol relocation, flag validation, and disabled-core stub builds.
