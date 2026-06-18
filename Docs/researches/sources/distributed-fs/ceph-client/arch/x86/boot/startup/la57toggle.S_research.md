# sources/distributed-fs/ceph-client/arch/x86/boot/startup/la57toggle.S

Purpose: template trampoline code copied below 4 GiB to toggle CR4.LA57 while temporarily leaving long mode.

Important APIs and state: exports `trampoline_32bit_src` and data `trampoline_ljmp_imm_offset`. The code size is bounded by `.org trampoline_32bit_src + TRAMPOLINE_32BIT_CODE_SIZE`.

Control flow: 64-bit entry saves callee-saved registers and upper RSP bits, far-returns to 32-bit compatibility code, disables paging, loads CR3 from `%edi`, ensures EFER.LME is set, toggles CR4.LA57, re-enables paging, and far-jumps back to the relocated 64-bit return label. On return it reconstructs RSP and restores registers.

Dependencies and integration: copied and patched by compressed `pgtable_64.c`. It uses kernel segment selectors, MSR_EFER, CR0/CR4 flags, and the low-memory temporary page table.

Risks and test signals: stack address truncation, incorrect far-jump relocation, or code-size overflow will break LA57 switching. Test 4-to-5 and 5-to-4 transitions, high stack addresses, TDX guests where unnecessary EFER writes are avoided, and build-time code-size assertion.
