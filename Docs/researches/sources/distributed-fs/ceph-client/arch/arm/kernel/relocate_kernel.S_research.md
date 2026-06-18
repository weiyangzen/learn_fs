# sources/distributed-fs/ceph-client/arch/arm/kernel/relocate_kernel.S

Purpose: contains the relocation trampoline copied to the kexec control page to move the next kernel's segments into place and branch to its entry.

Important APIs/types/functions: `relocate_new_kernel` and `relocate_new_kernel_size` are consumed by `machine_kexec.c`. The code interprets `struct kexec_relocate_data` values placed after the copied code.

Control flow: after soft restart jumps to the idmapped control page, the trampoline walks the kexec indirection page list, copies or clears pages according to control flags, sets ARM boot registers including machine type and r2 DTB/ATAGS pointer, and branches to the new kernel start address.

State and persistence: operates on physical pages and kexec control data; it is terminal for the old kernel.

Dependencies and integration: exact data layout must match `asm/kexec-internal.h` and `machine_kexec`. Runs with minimal MMU/cache assumptions.

Risks: any copy/order bug destroys the next kernel image or old memory before completion; register boot ABI must be exact. Test signals include successful kexec on DT and legacy ATAGS systems, crashdump boots, and relocation with multiple segments.
