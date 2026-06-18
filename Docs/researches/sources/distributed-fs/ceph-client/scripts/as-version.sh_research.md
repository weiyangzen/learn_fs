# sources/distributed-fs/ceph-client/scripts/as-version.sh

## Purpose
`as-version.sh` identifies the assembler backend and prints a canonical numeric version while enforcing the kernel minimum binutils version.

## APIs, Types, And Functions
Functions are `get_canonical_version()` and `check_integrated_as()`. The script executes the compiler/assembler command with `-Wa,--version -c -x assembler-with-cpp /dev/null -o /dev/null`, calls `scripts/min-tool-version.sh`, and prints `GNU <canonical>` or `LLVM 0`.

## Control Flow
If `-fintegrated-as` is present, the script reports LLVM integrated assembler and exits without a version check. Otherwise it captures the first assembler version line, recognizes GNU assembler, trims distribution suffixes, converts versions to `major*10000 + minor*100 + patch`, compares against the minimum, and exits with diagnostics if too old.

## State And Persistence
No state is persisted. Output is consumed by kbuild.

## Dependencies And Integration Points
It depends on shell, compiler assembler passthrough behavior, GNU assembler version output, and `min-tool-version.sh`. It integrates with compiler capability checks.

## Risks And Test Signals
Risks include changed version banner formats or unusual wrapper arguments. Test signals are expected `GNU 2xxxx` output for binutils, `LLVM 0` with `-fintegrated-as`, and failure on intentionally too-old versions.
