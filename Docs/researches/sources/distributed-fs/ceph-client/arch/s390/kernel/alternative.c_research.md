# sources/distributed-fs/ceph-client/arch/s390/kernel/alternative.c

## Purpose
Applies s390 runtime instruction alternatives based on CPU facilities, machine features, and speculation-control state. It patches kernel text after feature discovery so generic instruction sites can use faster or safer variants.

## Important APIs, Types, And Functions
`__apply_alternatives(struct alt_instr *start, struct alt_instr *end, unsigned int ctx)` is the main entry. `struct alt_debug` stores boot-preserved masks controlling debug dumps. `alternative_dump()` formats old and replacement bytes when debug bits are set.

## Control Flow
The function scans an `alt_instr` table in order, filters by context, decides whether replacement is active for `ALT_TYPE_FACILITY`, `ALT_TYPE_FEATURE`, or `ALT_TYPE_SPEC`, computes old and replacement instruction addresses from table-relative offsets, optionally logs the patch, and writes replacement bytes with `s390_kernel_write`.

## State And Persistence
Patching mutates live kernel text. Boot-preserved `machine_features` and `alt_debug` keep feature/debug state across early phases.

## Dependencies And Integration Points
Depends on alternative metadata, facility and machine-feature probes, no-spec branch state, text patching, absolute lowcore helpers, and boot sections. Entry assembly uses these alternatives heavily.

## Risks And Edge Cases
Scan order matters because later alternatives can overwrite earlier replacements. Incorrect instruction length, context masks, or feature tests can patch partial instructions. Text patching must synchronize with instruction fetch and respect early-boot address translation.

## Test Signals
Signals include boot tests across facility combinations, `debug-alternative` byte dumps, objtool/build checks of alternative records, runtime tests for no-spec toggles, and crash-free execution of entry paths using alternative macros.
