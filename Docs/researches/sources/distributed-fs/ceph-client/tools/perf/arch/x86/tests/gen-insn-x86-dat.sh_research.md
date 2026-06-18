# sources/distributed-fs/ceph-client/tools/perf/arch/x86/tests/gen-insn-x86-dat.sh

## Purpose
This shell script regenerates x86 instruction decoder fixture data from `insn-x86-dat-src.c`. It builds the fixture as both 64-bit and 32-bit objects, disassembles them with objdump, and filters the disassembly through `gen-insn-x86-dat.awk`.

## Important Commands and Behavior
The script uses `set -e`, rejects non-`x86_64` hosts, changes to its own directory, and installs an EXIT trap warning that a newer binutils may be required if generation fails. It then compiles `insn-x86-dat-src.c`, objdumps it through the AWK converter into `insn-x86-dat-64.c`, removes the object, repeats with `gcc -g -c -m32` into `insn-x86-dat-32.c`, clears the trap, and asks the user to inspect `git diff`.

## Control Flow
Generation is sequential and fail-fast. Any failing compiler, objdump, awk, or cleanup command exits the script because of `set -e`; the trap then emits the binutils hint. The 64-bit fixture is generated before the 32-bit fixture.

## State and Persistence
The script overwrites `insn-x86-dat-64.c` and `insn-x86-dat-32.c` in place and temporarily creates `insn-x86-dat-src.o`. It does not commit results or update indexes.

## Dependencies and Integration Points
It depends on an x86_64 host, GCC with 32-bit compilation support, binutils `objdump`, AWK, and the source annotations understood by `gen-insn-x86-dat.awk`. The generated files are included by `insn-x86.c` when extra tests are enabled.

## Risks and Edge Cases
The script is intentionally host/toolchain-sensitive. Missing 32-bit GCC support, older binutils that cannot decode newer instructions, or objdump formatting changes can fail generation or silently alter fixtures. Because outputs are overwritten before final success, a failure after the first pass can leave one generated file changed and the other stale unless the user reviews the diff.

## Test Signals
Success prints both compile phases and `Done (use git diff to see the changes)`. Downstream validation is a clean build and passing x86 instruction decoder tests with the regenerated data.
