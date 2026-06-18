<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/sdt.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/sdt.h

## Purpose
This public-domain SystemTap static probe header defines `STAP_PROBE*`, `DTRACE_PROBE*`, and assembly probe macros that emit NOP probe sites plus `.note.stapsdt` metadata describing provider, probe name, semaphore, and argument locations.

## Important APIs, Types, and Functions
Public macros include `STAP_PROBE`, `STAP_PROBE1` through `STAP_PROBE12`, optional `STAP_PROBEV`, `STAP_PROBE_ASM`, `STAP_PROBE_ASM_TEMPLATE`, `STAP_PROBE_ASM_OPERANDS`, and DTrace-compatible aliases. Internal macros format argument size/sign/type, choose constraints (`STAP_SDT_ARG_CONSTRAINT`), emit `.note.stapsdt`, emit `.stapsdt.base`, and optionally include semaphore addresses.

## Control Flow
For C/C++, `STAP_PROBEn` expands to inline assembly that references optional semaphores, emits a probe NOP and note section, then emits the base section. For assembler use, `_SDT_PROBE` emits similar assembly directly. Argument handling computes signedness and size via C++ templates or C builtins and encodes operand templates selected by architecture-specific macros.

## State and Persistence
No runtime mutable state is required unless `_SDT_HAS_SEMAPHORES` is defined, in which case semaphore symbols are referenced. The persistent artifact is ELF note metadata and probe-site NOP instructions in compiled objects.

## Dependencies and Integration Points
It includes `sdt-config.h` and integrates with SystemTap, GDB, and DTrace-compatible tooling that reads `.note.stapsdt`. It depends on GNU inline assembly features, assembler section support, compiler constraints, and architecture-specific register naming behavior.

## Risks
The macros are compiler/assembler-sensitive. Operand constraints can fail for complex argument lists, register alias notes may require consumer heuristics, and incorrect autogroup support can break C++ COMDAT scenarios. C99 support is needed for variadic assembly probe helpers.

## Test Signals
Compilation of probe users, presence of `.note.stapsdt` and `.stapsdt.base` sections, and consumer tools discovering provider/probe/argument metadata are the expected signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/sdt.h -->
