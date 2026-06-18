# sources/distributed-fs/ceph-client/arch/powerpc/mm/ptdump/Makefile

## Purpose
This Makefile selects the PowerPC page-table dump objects built for each MMU family and debugfs configuration.

## Important APIs, Types, And Functions
There are no C APIs here. Build outputs include the common `ptdump.o`, flag-table providers such as `shared.o`, `8xx.o`, and `book3s64.o`, plus debugfs-only helpers `bats.o`, `segment_regs.o`, and `hashpagetable.o`.

## Control Flow
`obj-y += ptdump.o` always includes the main walker. Configuration conditions then choose exactly one appropriate `pg_level` provider for 44x, 8xx, e500, Book3S32, or Book3S64. When `CONFIG_PTDUMP_DEBUGFS` is enabled, Book3S32 gets BAT and segment-register dumpers, and 64S hash MMU gets the hash page-table dumper.

## State And Persistence
The file controls build composition only. Its effect persists in the linked kernel image through selected object files.

## Dependencies And Integration Points
It integrates Kconfig symbols with the ptdump subsystem and must avoid duplicate `pg_level` definitions while ensuring `ptdump.o` always has one provider for the target architecture.

## Risks And Test Signals
Risks include missing a flag provider for a configuration, linking multiple `pg_level` definitions, or exposing debugfs files on unsupported MMUs. Test signals are allyesconfig/allmodconfig style PowerPC builds across 8xx, e500, 44x, Book3S32, Book3S64 radix, and Book3S64 hash.
