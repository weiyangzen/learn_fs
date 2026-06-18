
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/fpu.S

## Purpose
Provides assembly helper routines that execute PowerPC floating-point instructions in kernel context for KVM paired-single/FPU emulation. The helpers load caller-provided FPSCR/CR and operands, execute one native FPU instruction, store the result, and return updated FPSCR/CR state.

## Important APIs, Types, And Functions
The file generates many exported symbols through macros: single-precision `fps_*` helpers, double-precision `fpd_*` helpers, comparison helpers that update CR, and conversion helpers `kvm_cvt_fd` and `kvm_cvt_df`. Local helpers `fpd_load_none`, `fpd_load_one`, `fpd_load_two`, `fpd_load_three`, and `fpd_return` consolidate double-precision setup/teardown.

## Control Flow
Single-precision macros load FPSCR from `r3`, operands from `r5`/`r6`/`r7`, run the instruction, store the single result at `r4`, save FPSCR back to `r3`, and return. Double-precision macros save LR, branch to the appropriate load helper, execute the instruction with record form where needed, and branch to `fpd_return`, which saves result, FPSCR, and CR. Comparison macros load CR explicitly and only update FPSCR/CR outputs. Conversion helpers directly use `lfs`/`stfd` and `lfd`/`stfs`.

## State And Persistence
No persistent state is allocated. The visible state is entirely through memory pointers passed in registers for FPSCR, CR, results, and operands. The code uses FPR0-FPR3 and GPR scratch registers according to the PowerPC ABI expectations of its callers.

## Dependencies And Integration Points
Depends on PowerPC assembly macros, linkage definitions, FPU instructions, FPSCR manipulation via `MTFSF_L`, and KVM FPU emulation callers elsewhere in the PowerPC KVM tree. It is build-time architecture-specific and not directly called from userspace.

## Risks
Calling convention mismatches are high impact because the interface is raw register/pointer based. The helpers assume kernel code has enabled and protected FPU use before entry. Record-form double operations update CR, so wrong CR pointer handling would corrupt guest-visible condition state. Host endianness and alignment assumptions are inherited from native load/store instructions.

## Test Signals
Coverage should come from paired-single/FPU emulation tests comparing guest results and FPSCR/CR side effects against hardware. Build tests catch symbol/linkage regressions. Runtime stress should include exceptional FPSCR conditions, comparisons, fused multiply-add variants, and conversion helpers.
