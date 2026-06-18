# sources/distributed-fs/ceph-client/tools/arch/arm64/tools/Makefile

## Purpose
Build fragment that generates arm64 tools system-register definitions.

## Important APIs, Types, and Functions
Defines `top_srcdir`, includes `tools/scripts/Makefile.include`, sets `AWK`, `MKDIR`, `RM`, locates `arch/arm64/tools/sysreg` and `gen-sysreg.awk`, and builds `$(OUTPUT)arch/arm64/include/generated/asm/sysreg-defs.h`.

## Control Flow, State, and Persistence
The default target depends on the generated header. The rule creates the output directory and pipes the sysreg table through AWK. `clean` removes the generated arm64 include directory.

## Dependencies and Integration Points
Integrated by tools builds before including `asm/sysreg.h`. It depends on kernel source layout, `OUTPUT`, AWK, and the arm64 sysreg generator/table.

## Risks and Test Signals
Risks include incorrect `top_srcdir` inference when invoked from unusual directories, stale generated files, and AWK/generator errors propagating into register encodings. Test signals are `make -C tools/arch/arm64/tools`, clean/regenerate idempotence, and consumers finding `asm/sysreg-defs.h`.
