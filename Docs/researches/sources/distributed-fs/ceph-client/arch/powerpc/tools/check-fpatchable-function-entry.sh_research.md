# sources/distributed-fs/ceph-client/arch/powerpc/tools/check-fpatchable-function-entry.sh

## Purpose
This shell probe verifies that the compiler supports `-fpatchable-function-entry=2` for ppc64 ELFv2 and emits patchable entries in the layout expected by PowerPC ftrace.

## Important APIs, Types, And Functions
The script receives the compiler command as `$*`, forces `-m64 -mabi=elfv2`, compiles small C snippets to assembly, and uses `grep` plus `awk` to check for `__patchable_function_entries` and two `nop` instructions after `.localentry`.

## Control Flow
With `set -e`, any failed compile or missing pattern exits nonzero. The first compile checks that the option exists and emits the metadata section. The second compile checks code placement by splitting assembly records on semicolons and finding a function whose local entry is followed by two NOPs.

## State And Persistence
The script is stateless and writes no files; it streams source to the compiler and assembly to filters.

## Dependencies And Integration Points
It depends on bash, the configured compiler, assembler output syntax, `grep`, and `awk`. It is intended for Kconfig/build feature detection for PowerPC ftrace patching.

## Risks
The probe is intentionally ppc64 ELFv2-specific and should not be used for other ABIs. Assembly formatting differences across compilers can create false negatives. Passing the compiler through `$*` preserves simple command use but can be fragile with unusual quoting.

## Test Signals
A zero exit status means the toolchain supports the expected patchable-function-entry format. Nonzero status should disable the dependent ftrace feature or fail the capability check.
