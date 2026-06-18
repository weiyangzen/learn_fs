# sources/distributed-fs/ceph-client/arch/m68k/ifpsp060/src/itest.S

## Purpose

`itest.S` is a Motorola M68060 integer support package validation harness. It executes a fixed sequence of 68060 integer-instruction conformance tests and reports per-suite pass/fail text through externally supplied print vectors. The tested instruction families are 64-bit multiply, 64-bit divide, `cmp2`/`chk2`, `movep`, effective-address forms, `cas`, and `cas2`.

The file is not Ceph-specific logic despite living below `sources/distributed-fs/ceph-client`; it is imported architecture support-package assembly from Motorola's 1994 M68060 software package. Its behavioral value is as low-level CPU/assembler validation data for m68k/68060 instruction behavior, especially register side effects and condition-code outcomes.

## Important Entry Points and Routines

- `TESTTOP` is the file-level entry label. It immediately branches to `_060TESTS_`.
- `_060TESTS_` is the main test driver. It allocates a 160-byte stack frame, saves registers with `movm.l`, prints the start banner, runs each suite, calls `chk_test`, restores registers, and returns.
- `chk_test` interprets suite return state. A zero `%d0` prints `passed`; nonzero `%d0` prints the failing subtest number from `%d1` and then `failed`.
- `mulul_0` through `mulul_8` validate unsigned and signed long multiply forms, including 64-bit result pairs such as `%d2:%d3`, same-register destination forms, zero operands, high-bit operands, and sign-extension cases.
- `divul_0` through `divul_10` validate `divu.l` and `divs.l` forms. The first case has its actual divide body commented out, but still increments the subtest counter before falling through.
- `cmp2_1` through `cmp2_30` validate byte, word, and long `cmp2`/`chk2` outcomes across unsigned and signed bounds, data-register and address-register comparands, and expected condition-code states.
- `movp_0` through `movp_17` validate `movp.w` and `movp.l` loads and stores against byte-strided memory, positive and negative displacements, `%d0` and `%d7` destinations/sources, memory-neighbor preservation, and condition-code preservation.
- `ea_0` through `ea_143` validate effective-address encodings by applying them as source operands to `mulu.l`. The cases cover address indirect, postincrement, predecrement, displacement, immediate, PC-relative, indexed, suppressed base/index notation, memory-indirect preindexed/postindexed forms, and special handling when `%a6` or `%a7` is temporarily used as an address or index register.
- `cas0` through `cas5` validate `cas.w` and `cas.l` compare-and-swap behavior on matching and nonmatching memory, including unaligned local offsets and expected update of compare/update registers.
- `cas20` through `cas214` validate `cas2.l` and `cas2.w` two-location compare-and-swap behavior for both full-match and partial-mismatch cases across aligned and unaligned local operands.
- `chkregs` compares captured expected register state at `IREGS(%a6)` with observed state at `SREGS(%a6)`, then compares expected `ICCR(%a6)` to captured `SCCR(%a6)`.
- `error` packages a failure result by copying `TESTCTR(%a6)` to `%d1` and setting `%d0` to `1`.
- `_print_str` and `_print_num` are local dispatch shims. They load function offsets from memory before `TESTTOP`, synthesize callable addresses relative to `TESTTOP - 0x80`, pass the caller's original argument in `%d0`, and return with `rtd &0x4`.

## Control Flow

The driver follows a repeated suite contract:

1. Clear `TESTCTR(%a6)`.
2. Print the suite name string.
3. Branch to the first label in the suite.
4. Each numbered subtest increments `TESTCTR`, initializes registers and scratch memory, captures the intended pre-instruction register image into `IREGS`, executes one target instruction, captures post-instruction registers into `SREGS`, patches `IREGS` for expected side effects, and calls `chkregs`.
5. Any mismatch branches to `error`, which returns `%d0 = 1` and `%d1 = failing subtest number`.
6. If all cases fall through successfully, the suite copies `TESTCTR` to `%d1`, clears `%d0`, and returns.
7. `_060TESTS_` calls `chk_test`, which prints `passed` or the failing test number plus `failed`.

The suites are chained by fall-through between numbered labels rather than by a table. There is no loop over test descriptors; the sequence is encoded directly in assembly. This makes subtest numbering dependent on physical label order and on commented-out bodies that still increment `TESTCTR`.

## State and Persistence Behavior

All test state is transient and stack-frame-local under `%a6`:

- `SREGS` at `-64` stores the observed post-instruction register snapshot.
- `IREGS` at `-128` stores the expected post-instruction register snapshot, initialized from the pre-instruction register state and then patched for expected changes.
- `SCCR` and `ICCR` store observed and expected condition-code words.
- `TESTCTR` stores the current suite's subtest number.
- `EAMEM`, `EASTORE`, and `DATA` are small scratch slots used as instruction operands, pointer storage, and byte/word/long test memory.

The file has no persistent storage, heap allocation, global mutable data segment, or OS-visible side effect other than printing. Some effective-address cases store temporary data in inline code-adjacent labels such as `ea_8_mem`, `ea_55_data`, and `ea_68_mem` through `ea_88_mem`, but those are constant embedded operands rather than long-lived runtime state.

The driver saves and restores a register set around the whole run. Individual subtests deliberately overwrite many data and address registers with `DEF_REGS` before exercising an instruction. Cases that repurpose `%a6` or `%a7` first save the original frame or stack pointer in another register and restore it before calling `chkregs`.

## Dependencies and Integration Points

- Requires a Motorola m68k assembler syntax that accepts directives and forms used here: `set`, `string`, `align 0x4`, `%dN`/`%aN` registers, `&` immediates, `%cc`, `movm.l`, `rtd`, and 68020+/68060 full-extension effective-address syntax such as `([bd,An,Xn],od)`, `%zpc`, `%za4`, and `%zd4`.
- Requires execution on, or faithful emulation of, a CPU that implements the tested 68060 integer instruction subset and condition-code behavior.
- Depends on external print-vector layout before `TESTTOP`. `_print_str` reads an offset at `(TESTTOP - 0x80 + 0)` and `_print_num` reads an offset at `(TESTTOP - 0x80 + 4)`, then calls through the computed trampoline address. The surrounding test loader must provide these slots.
- Integrates with the broader 68060 software package as an instruction-set validation test, not as a reusable library. Callers consume only `_060TESTS_`/`TESTTOP` execution and text output.

## Risks and Edge Cases

- Several numbered cases increment `TESTCTR` but have the meaningful body commented out: notably `divul_0`, `ea_5`, `ea_6`, `ea_78`, `ea_101`, and `ea_115`. They become pass-through counted tests, so reported subtest numbers do not all correspond to executed instruction checks.
- The effective-address suite is highly assembler-dependent. Syntax such as `%zpc`, zero-suppressed base/index registers, memory-indirect brackets, and size-qualified displacements may not assemble under generic GNU m68k syntax without compatibility support.
- `ea_129` does not reload `DEF_REGS` before its instruction, unlike most neighboring effective-address tests. That means its expected register snapshot depends on the register state left by previous code, and it is more fragile if test order is changed.
- Some effective-address tests temporarily assign `%a6` and `%a7`. Any edit that introduces calls, stack use, or frame-relative accesses while these registers are repurposed can corrupt the harness.
- The register comparison loop uses `mov.l &14,%d0` followed by `dbra`, comparing 15 longwords. This covers the `movm.l &0x7fff` snapshots but deliberately omits one register from the full 16-register model when the mask excludes it.
- The code assumes condition-code preservation or mutation exactly as captured in `ICCR`/`SCCR`; emulator differences, CPU errata, or assembler rewriting can surface as false failures.
- The inline print shims rely on a non-obvious loader ABI and `rtd`, so moving `TESTTOP` or changing the prefix vector layout breaks reporting even if tests still execute.

## Test Signals

Expected runtime output begins with `Testing 68060 ISP started:` and then prints one line-like status per suite label: `64-bit multiply`, `64-bit divide`, `cmp2,chk2`, `movep`, `Effective addresses`, `cas`, and `cas2`. For each suite, success prints `passed`; failure prints the failing subtest number followed by `failed`.

Useful validation signals are:

- All suites return `%d0 = 0`.
- On success, `%d1` equals the suite's final `TESTCTR`, which also indicates how many numbered cases were traversed.
- On failure, `%d1` identifies the failing numbered label within the active suite.
- `chkregs` returning nonzero means either a general/address register snapshot mismatch or a condition-code mismatch.
- Direct memory assertions in `movp_*` and `cas*` can fail before `chkregs`, so a failing subtest number may indicate an explicit memory-content check rather than only a register comparison failure.
