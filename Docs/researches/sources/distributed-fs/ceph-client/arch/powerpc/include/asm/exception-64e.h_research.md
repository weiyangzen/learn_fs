## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/exception-64e.h

Purpose: defines Book3E 64-bit exception save-area offsets, TLB-miss prolog/epilog assembly macros, IVOR setup, and return-from-interrupt macros.

Important APIs/types/functions: PACA offsets such as `EX_R1` and `EX_TLB_*`, `START_EXCEPTION()`, `TLB_MISS_PROLOG`, `TLB_MISS_RESTORE()`, `TLB_MISS_EPILOG_SUCCESS`, error epilogs, `interrupt_base_book3e`, `SET_IVOR()`, `RFI_TO_KERNEL`, and `RFI_TO_USER`.

Control flow: TLB miss prolog saves scratch registers, CR, SRR0/SRR1, and PACA state into a reentrant PACA exception frame, advances the frame pointer for nested misses, and restores on success or error. IVOR setup writes exception vector offsets from `interrupt_base_book3e`.

State and persistence: uses PACA exception save areas and SPRG scratch registers. It manipulates SRR0/SRR1 and IVOR SPRs, all critical processor state.

Dependencies and integration: consumed by Book3E exception assembly, PACA layout, TLB miss handlers, and low-level interrupt return code.

Risks and test signals: reentrancy and SPRG usage are extremely sensitive; leaked user-readable SPRGs or wrong save offsets can corrupt nested exceptions. Test signals include Book3E boot, TLB miss stress, nested machine-check/critical interrupt scenarios, vector setup validation, and syscall/interrupt return tests.
