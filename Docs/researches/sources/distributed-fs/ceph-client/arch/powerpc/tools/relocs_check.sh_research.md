# sources/distributed-fs/ceph-client/arch/powerpc/tools/relocs_check.sh

## Purpose
This wrapper filters the generic kernel relocation checker for PowerPC, warning only on relocations that are suspicious for PowerPC kernel images.

## Important APIs, Types, And Functions
It expects objdump, nm, and vmlinux arguments, calls `${srctree}/scripts/relocs_check.sh "$@"`, removes allowed relocation names with fixed-string word grep, counts remaining lines, and prints a warning plus the bad relocation list.

## Control Flow
If too few arguments are supplied, it exits with usage. Otherwise it runs the generic checker, filters allowed PPC32/PPC64 relocation types, exits zero when none remain, or prints the count and entries. It does not force a nonzero exit for warnings after printing.

## State And Persistence
No state is persisted; all data flows through command substitution and stdout.

## Dependencies And Integration Points
It depends on `${srctree}`, the generic relocation checker, grep, wc, and shell command substitution. It is part of post-link architecture validation.

## Risks
Because warnings do not necessarily fail the build, downstream policy must decide severity. The whitelist must track legitimate relocation types; missing entries create noisy warnings, while overly broad entries hide real boot-time relocation hazards.

## Test Signals
Clean builds produce no output and zero exit. Introducing an unsupported relocation should produce `WARNING: N bad relocations` followed by the generic checker lines.
