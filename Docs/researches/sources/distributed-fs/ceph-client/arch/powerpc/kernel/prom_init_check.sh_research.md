# sources/distributed-fs/ceph-client/arch/powerpc/kernel/prom_init_check.sh

## Purpose
This build-time shell validator protects `prom_init.o` from accidentally referencing ordinary kernel symbols or storing data in sections that are unsafe for early Open Firmware execution.

## Important APIs, Types, And Functions
The script accepts `NM` and `OBJ` as positional arguments. `has_renamed_memintrinsics()` checks Kconfig for KASAN configurations where memory intrinsic names are prefixed. `WHITELIST` enumerates permitted undefined symbols such as relocation helpers, low-memory CPU hold labels, `__start`, minimal memory functions, banner/logo/display hooks, and `relocate`. `check_section()` uses `objdump -h -j` to require `.data`, `.bss`, and `.init.data` to be empty in the object.

## Control Flow
The script derives allowed memory-function names from `KCONFIG_CONFIG`, iterates undefined symbols from `$NM -u "$OBJ"`, strips leading function-descriptor dots, optionally logs each symbol when verbose, matches against the whitelist, separately accepts compiler register save/restore helpers, and emits errors for anything else. It then checks forbidden sections and exits with accumulated error status.

## State And Persistence
No persistent repository state is changed. `ERROR` is process-local and controls the exit code.

## Dependencies And Integration Points
It is intended for the PowerPC kernel build and depends on `nm`, `objdump`, `awk`, `grep`, `KCONFIG_CONFIG`, and `KBUILD_VERBOSE`. It directly enforces the isolation assumptions of `prom_init.c`.

## Risks
The whitelist must evolve with real early-boot dependencies; too broad a whitelist weakens isolation, while missing legitimate compiler helper names breaks valid builds. Numeric section-size parsing assumes `objdump` format and shell arithmetic can interpret the hexadecimal section size.

## Test Signals
A passing build shows no forbidden undefined symbols and empty forbidden sections. Negative tests are easy: add a normal kernel call or initialized global to `prom_init.c` and verify the script fails with a clear diagnostic.
