<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/errata/sifive/errata_cip_453.S -->
# sources/distributed-fs/ceph-client/arch/riscv/errata/sifive/errata_cip_453.S

## Purpose
Provides replacement trap handlers for SiFive CIP-453 bad-address sign extension.

## Important APIs, Types, And Functions
`ADD_SIGN_EXT` loads `PT_BADADDR`, checks bit 0x26, sign-extends from bit 0x27 when needed, and stores it back. Entry points are `sifive_cip_453_page_fault_trp` and `sifive_cip_453_insn_fault_trp`.

## Control Flow
Each handler fixes the bad address in pt_regs, then jumps to `do_page_fault` or `do_trap_unknown` for page faults depending on MMU, or to `do_trap_insn_fault` for instruction faults.

## State And Persistence
Persistent state is the corrected `PT_BADADDR` field in the exception frame before the generic trap handler sees it.

## Dependencies And Integration Points
Integrated with SiFive alternative patching, trap entry code, asm offsets, and generic fault handlers.

## Risks And Edge Cases
Register clobbering and sign-extension bit positions are critical. The jump target differs with MMU config.

## Test Signals
Signals are fault tests on affected cores showing correctly sign-extended bad addresses and normal generic fault handling afterward.

Source read size: 38 lines, 835 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/errata/sifive/errata_cip_453.S -->
