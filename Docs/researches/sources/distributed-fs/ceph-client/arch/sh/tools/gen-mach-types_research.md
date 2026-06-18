<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/tools/gen-mach-types -->
# sources/distributed-fs/ceph-client/arch/sh/tools/gen-mach-types

## Purpose
This awk script generates the SH machine-type header from a two-column machine/config table.

## Important APIs, Types, and Functions
The script stores machine names in `mach[]` and corresponding Kconfig symbols in `config[]`. It emits `MACH_<name>` macros gated by `CONFIG_<symbol>` and convenience `mach_is_<lowercase>()` predicates.

## Control Flow
Comments and blank lines are skipped. Two-field rows are accumulated, then the `END` block writes a guarded C header with generated comments, `MACH_*` definitions, and predicate macros.

## State and Persistence Behavior
State exists only inside the awk process. The generated header is the persistent build artifact.

## Dependencies and Integration Points
It is invoked by `arch/sh/tools/Makefile` and depends on the format of `arch/sh/tools/mach-types`. Generated macros are included by SH platform code until per-board `sh_machtype` assignment replaces legacy placeholders.

## Risks
Rows with unexpected field counts are silently ignored, and machine names are inserted directly into macro names. Input naming mistakes therefore become missing or malformed compile-time predicates.

## Test Signals
Regenerate `include/generated/machtypes.h` from known input and inspect `CONFIG_*` gates, `MACH_*` values, lowercase predicate names, and header guards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/tools/gen-mach-types -->
