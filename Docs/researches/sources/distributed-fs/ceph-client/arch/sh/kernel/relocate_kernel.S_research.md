# sources/distributed-fs/ceph-client/arch/sh/kernel/relocate_kernel.S

Purpose: assembly relocation engine copied to the kexec control page to move/swap pages and branch to a new kernel.

Important APIs and control flow: `relocate_new_kernel` saves caller, special, and banked registers onto a control-page stack; calls `swap_pages`; stores stack pointer; jumps to the new kernel start; and, for kexec jump return, restores pages and all saved registers. `swap_pages` walks the generic kexec indirection list, tracks destination/indirection/source commands, and swaps 16-byte chunks for each page so both normal kexec and kexec jump use one mechanism. `relocate_new_kernel_size` exports the copy size.

State, dependencies, and risks: state is the control-page stack, indirection list, and page contents being swapped. Dependencies include generic kexec indirection flag encoding, `PAGE_SIZE`, banked-register bit, and `machine_kexec()` address conversion. Risks are catastrophic if page-list commands are malformed, bank selection is not restored, or source/destination overlap assumptions fail. Test signals are kexec boot, kexec jump round-trip, register preservation checks, and large multi-segment images.
