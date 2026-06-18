
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/x86-5lvl.c

Purpose: supports enabling or disabling x86 5-level paging during EFI stub boot by preparing a 32-bit trampoline and switching CR3/CR4 state before kernel entry.

Important APIs/types/functions: exports global `efi_no5lvl`, `efi_setup_5level_paging()`, and `efi_5level_switch()`. Uses external trampoline symbols `trampoline_32bit_src` and `trampoline_ljmp_imm_offset`.

Control flow: setup only runs on 64-bit firmware with CPUID LA57 support. It allocates two 32-bit-addressable pages, copies the trampoline, pads it, fixes the absolute long-jump target, and adjusts memory protections. The switch function compares desired LA57 state with current CR4, builds or selects a 32-bit-addressable root page table, loads a small GDT, and invokes the trampoline.

State and persistence behavior: static `la57_toggle` points to allocated trampoline code and adjacent page table memory. `efi_no5lvl` is set by command-line parsing.

Dependencies and integration points: depends on CPUID, x86 GDT/CR3/CR4 helpers, EFI low memory allocation, memory protection adjustment, and x86 stub final handoff.

Risks and test signals: the trampoline and root page table must be below 4 GiB, the LJMP fixup must be correct, and toggling LA57 is only valid from 32-bit mode with paging disabled. Test signals include LA57-capable and non-capable machines, `no5lvl`, firmware already in LA57, high root table copy, and successful kernel entry after toggle.
