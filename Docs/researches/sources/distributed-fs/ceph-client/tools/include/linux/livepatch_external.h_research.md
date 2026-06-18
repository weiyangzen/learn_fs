<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/livepatch_external.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/livepatch_external.h

## Purpose
This header defines the external livepatch ELF metadata structures consumed by tooling.

## APIs And Flow
It provides constants such as `KLP_RELA_PREFIX`, `KLP_SYM_PREFIX`, and `KLP_SYMPOS_MAX`, and structures `klp_module_reloc`, `klp_object_relocs`, `klp_section_relocs`, and symbol-position metadata used by livepatch relocation processing. There is no executable flow; it is an ABI description for parsing or emitting sections.

## State, Dependencies, Risks, Tests
State is persistent in compiled ELF objects and livepatch metadata sections. Dependencies are fixed-width integer types and ELF/livepatch tools that interpret these records. Risks include ABI drift with kernel livepatch consumers, incorrect symbol position handling for duplicate names, and malformed relocation counts. Tests should parse representative livepatch objects, validate section names and relocation arrays, and compare structure sizes with the kernel header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/livepatch_external.h -->
