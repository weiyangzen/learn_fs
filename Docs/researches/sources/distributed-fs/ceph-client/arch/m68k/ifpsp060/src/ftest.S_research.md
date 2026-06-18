# sources/distributed-fs/ceph-client/arch/m68k/ifpsp060/src/ftest.S

## Purpose
`ftest.S` is a self-checking Motorola 68060 FPSP validation harness. It exercises floating-point unimplemented-instruction handling, unsupported FP effective-address/data formats, non-maskable overflow/underflow behavior, and enabled exception cases for SNAN, OPERR, overflow, underflow, divide-by-zero, and inexact. It is not production exception handling code; it is a diagnostic entry table plus test cases that prove the FPSP restores integer registers, floating-point registers, FP control registers, condition codes, and `fpiar` as expected after each emulated or trapped FP operation.

## Important APIs, Types, And Functions
The branch table at `TESTTOP` exposes `_060TESTS_`, `_060TESTS_unimp`, and `_060TESTS_enable`, each followed by a reserved `short 0x0000` slot. `_060TESTS_` runs effective-address, unsupported-format, non-maskable overflow, and non-maskable underflow tests. `_060TESTS_unimp` runs the unimplemented FP instruction group. `_060TESTS_enable` enables specific FPCR exception bits and runs enabled exception tests.

The local stack frame uses fixed negative offsets from `%a6`: `SREGS`, `IREGS`, `IFPREGS`, `SFPREGS`, `IFPCREGS`, `SFPCREGS`, `ICCR`, `SCCR`, `TESTCTR`, and `DATA`. These model initial and saved integer/FP/FPC register images. `DEF_REGS`, `DEF_FPREGS`, and `DEF_FPCREGS` provide deterministic defaults. `chkregs` and `chkfpregs` compare expected versus observed snapshots; `error` returns the current `TESTCTR` in `%d1`; `chk_test` prints `passed` or the failing test number with `failed`.

The test labels are grouped by behavior: `unimp_0` through `unimp_5` cover `fsin`, `ftan`, `fmovcr`, `fscc`, `fdbcc`, and `ftrapcc`; `effadd_0`, `effadd_1`, `fmovml_0` through `fmovml_3`, and `fmovmx_0` through `fmovmx_2` cover immediate packed/extended operands and FP control/register multi-moves; `unsupp_0` through `unsupp_2` cover unnormalized, denormalized, and packed decimal formats. The exception groups are single-case routines with labels such as `ovfl_0_pc`, `snan_0_pc`, and `dz_0_pc`, whose addresses are written into expected `fpiar` slots.

## Control Flow
Each top-level runner links a 384-byte frame, saves general and FP registers, prints a start string through `_print_str`, clears `TESTCTR` for each category, calls the category routine, and delegates pass/fail reporting to `chk_test`. Each individual test repeats the same pattern: seed all registers with defaults, capture the initial register images into `IREGS`/`IFPREGS`/`IFPCREGS`, load operands into `DATA` or FP registers, clear or set condition/FPCR state, execute the instruction under test at a named `_pc` label, snapshot the post-instruction machine state into `SREGS`/`SFPREGS`/`SFPCREGS`, patch the expected image with the exact result and expected FPSR/FPIAR values, then call `chkregs` and `chkfpregs`.

The harness returns `%d0 = 0` on success. On the first mismatch, `chkregs` or `chkfpregs` returns nonzero, `error` copies `TESTCTR` into `%d1`, and the caller prints the failing ordinal. The print stubs do not implement I/O directly: `_print_str` and `_print_num` read callout displacements from `TESTTOP - 0x80` and tail-call via `rtd`, so the embedding environment supplies the actual output hooks.

## State And Persistence
All test state is stack-frame-local except the callout table used by printing. The code intentionally mutates real CPU state while testing, but restores caller-visible general and FP registers at the end of each top-level runner using `movm.l` and `fmovm.x`. No disk, heap, or kernel state is persisted by this file. The observed state that matters is condition code, data/address register contents, FP register triples, FPCR/FPSR/FPIAR, and the test counter.

## Dependencies And Integration Points
The file depends on a 68060-capable assembler dialect with Motorola syntax, FP instructions, `fmovm`, packed/extended FP constants, and `rtd`. It assumes the Motorola 68060 FPSP exception package is installed so the unimplemented and exception-generating instructions return to the next instruction with FPSP-updated state. It integrates with an external test harness through the `TESTTOP` branch table and the two print callouts placed before `TESTTOP` in the linked image.

## Risks
The tests are exact-register-image checks, so they are sensitive to assembler encoding, FPSP revision, CPU/FPU mode, exception-vector setup, and whether the host preserves `fpiar` addresses exactly. The test frame offsets and `movm` masks are tightly coupled; accidental local-frame changes can silently compare the wrong words. Several cases depend on enabled FPCR exception bits and specific FPSR bit patterns, so running on a different 68k-family FPU or under an emulator with incomplete 68060 FPSP behavior can produce false failures. The print callout addressing is also non-obvious and can break if the branch table placement changes.

## Test Signals
The main signal is the printed category result and, on failure, the one-based `TESTCTR` ordinal. More granular debugging comes from the named `_pc` labels and expected image patches immediately after each instruction. Useful coverage signals include: unimplemented FP op return values and `fpiar`, unsupported operand/data-format normalization, FPCR-enabled trap behavior, non-maskable overflow/underflow, dynamic FP register masks, and exact preservation of unrelated integer and FP registers.
