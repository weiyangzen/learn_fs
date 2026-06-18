# sources/distributed-fs/ceph-client/kernel/module/version.c

## Purpose
Implements module symbol version compatibility checks for `CONFIG_MODVERSIONS`, including traditional `__versions` records and extended CRC/name sections.

## Important APIs, Types, And Functions
Defines `check_version`, `check_modstruct_version`, `same_magic`, `modversion_ext_start`, `modversion_ext_advance`, and exported marker function `module_layout`.

## Control Flow
For each resolved symbol, `check_version` compares the exporting symbol CRC against either extended version entries or traditional `struct modversion_info` records. Missing CRCs from exporters are allowed; missing versions in the importing module can force-load only when configured. `check_modstruct_version` specifically validates `module_layout`. `same_magic` ignores the leading kernel version when CRCs are present.

## State And Persistence
No persistent state is owned here. It reads version sections cached in `load_info.index` and influences whether the module load continues or taints through forced loading.

## Dependencies And Integration Points
Depends on `find_symbol`, module force-load policy, ksymtab CRCs, modpost-generated version sections, and vermagic checks in `main.c`.

## Risks And Edge Cases
Extended version CRC and name sections must remain paired and aligned by `main.c` validation. Missing symbol versions are tolerated for broken toolchains, but mismatched CRCs reject the module. Forcing versionless modules weakens ABI safety and taints the kernel.

## Test Signals
Load modules with matching, mismatched, missing, and extended modversions; verify `module_layout` mismatch rejection, `--force` behavior, warnings for missing entries, and vermagic comparison when CRCs are present.
