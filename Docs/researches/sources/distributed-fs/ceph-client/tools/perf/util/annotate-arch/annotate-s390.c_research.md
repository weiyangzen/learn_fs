# sources/distributed-fs/ceph-client/tools/perf/util/annotate-arch/annotate-s390.c

## Purpose
Implements s390 architecture annotate support. It classifies jumps/calls/returns, parses s390 call targets, handles PC-relative load/store-like operands as move operations, and parses s390 CPU id strings for architecture metadata.

## Important APIs, Types, and Functions
`arch__new_s390()` allocates the `s390` descriptor, optionally parses `cpuid`, installs `s390__associate_ins_ops()`, and sets objdump comments to `#`.
`s390_call__parse()` parses call operands of the form `...,addr <name>`, records target address/name, and resolves the target symbol through thread maps.
`s390_mov__parse()` splits source and target around a comma, captures raw operands, parses target address and symbol name, and uses `mov__scnprintf()`.
`s390__associate_ins_ops()` classifies generic jump mnemonics containing `j`, `bct*`, or `br*`, overrides `bras`, `brasl`, and `basr` as calls, `br` as return, and relative load/store mnemonics as move operations.
`s390__cpuid_parse()` extracts the family from IBM-formatted cpuid strings.

## Control Flow
Mnemonic association starts broad for jumps, then applies overrides for calls, returns, and relative load/store instructions. Call parsing maps objdump addresses to memory addresses and validates symbol resolution round-trips. Move parsing prepares source/target fields so common move rendering can show address and symbol information.

## State and Persistence
The architecture descriptor records family/model metadata. Per-instruction parsing allocates strings for operand fields and symbol names; failure paths free partially allocated operands. No disk state is involved.

## Dependencies and Integration Points
Depends on common map, maps, thread, symbol, annotate, and annotate-data infrastructure. Integrated with common call/jump/move rendering and with architecture discovery via cpuid.

## Risks
The broad `strchr(name, 'j')` jump classification can catch non-control-flow mnemonics containing `j`. `s390_mov__parse()` requires symbol-delimited target text and will fail for address-only operands. `arch__new_s390()` returns `NULL` on bad cpuid after allocating `arch`, which risks a small leak on initialization failure.

## Test Signals
Use s390 disassembly with `brasl`, `basr`, `br`, `bct*`, `j*`, and `lgrl`/`strl` forms. Include valid and invalid cpuid strings and verify symbol target resolution.
