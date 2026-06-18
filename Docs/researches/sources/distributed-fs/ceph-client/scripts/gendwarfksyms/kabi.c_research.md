# sources/distributed-fs/ceph-client/scripts/gendwarfksyms/kabi.c

## Purpose
`kabi.c` reads and serves stable kABI rule metadata emitted into ELF section `.discard.gendwarfksyms.kabi_rules`.

## Important APIs, Types, and Functions
Rules are versioned four-field records: version, type, target, value. Supported tags are `declonly`, `enumerator_ignore`, `enumerator_value`, `byte_size`, and `type_string`. Public query APIs include `kabi_is_declonly()`, `kabi_is_enumerator_ignored()`, `kabi_get_enumerator_value()`, `kabi_get_byte_size()`, `kabi_get_type_string()`, and `kabi_free()`.

## Control Flow
`kabi_read_rules()` returns immediately unless `--stable` is enabled. It opens the ELF, finds the rule section, validates size/null termination/version/type fields, copies target/value strings into a hash map, and leaves queries to lookup by type and target.

## State and Persistence Behavior
The rule map is global process state until `kabi_free()`. Rules from multiple files can accumulate during a run.

## Dependencies and Integration Points
`dwarf.c` uses declaration, enumerator, and byte-size rules while rendering. `types.c` uses type-string overrides during type expansion/versioning.

## Risks and Test Signals
Malformed rule sections are fatal. Duplicate rules are not explicitly rejected, so lookup order can matter. Numeric values are decimal-only via `strtoul()`. Test missing section, bad version, every rule type, duplicate rules, and examples from `kabi_ex.h`.
