<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/module_symbol.h -->
# sources/distributed-fs/ceph-client/include/linux/module_symbol.h

## Purpose
`module_symbol.h` defines small symbol metadata helpers shared by module and symbol tooling.

## Important APIs, Types, and Functions
It defines `enum ksym_flags` with `KSYM_FLAG_GPL_ONLY` and `is_mapping_symbol()`, which filters ELF mapping symbols starting with `.L`, `L0`, or `$`.

## Control Flow and State
Symbol consumers call `is_mapping_symbol()` while walking ELF or kallsyms data to skip local mapping artifacts that should not be treated as real exported/kernel symbols.

## State and Persistence Behavior
No runtime state is owned here. Flags are encoded alongside symbol metadata.

## Dependencies and Integration Points
It integrates with module symbol export handling, kallsyms, modpost, and architecture ELF symbol conventions.

## Risks
Over-filtering can hide legitimate symbols; under-filtering pollutes kallsyms/export processing with mapping markers. GPL flag semantics must match export enforcement.

## Test Signals
Build modules on architectures that emit mapping symbols, inspect kallsyms/export lists, and verify GPL-only symbol checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/module_symbol.h -->
