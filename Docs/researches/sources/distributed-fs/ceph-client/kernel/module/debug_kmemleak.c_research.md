# sources/distributed-fs/ceph-client/kernel/module/debug_kmemleak.c

## Purpose
Provides kmemleak integration for loaded modules. It prevents kmemleak from scanning module memory ranges that are writable but not executable and are not the primary data or init-data allocations.

## Important APIs, Types, And Functions
Defines `kmemleak_load_module(const struct module *mod, const struct load_info *info)`. It iterates all module memory types with `for_each_mod_mem_type` and calls `kmemleak_no_scan` for selected allocations.

## Control Flow
After a module has been allocated and moved into final memory, `layout_and_allocate` calls `kmemleak_load_module`. The helper skips `MOD_DATA`, `MOD_INIT_DATA`, and ROX memory, marking the remaining writable non-executable module regions as no-scan.

## State And Persistence
It changes kmemleak metadata for module allocation bases. No module loader state is owned by this file.

## Dependencies And Integration Points
Depends on `linux/kmemleak.h`, `struct module`, module memory type iteration, and `internal.h`. It is compiled only with `CONFIG_DEBUG_KMEMLEAK`.

## Risks And Edge Cases
Incorrect classification can hide real leaks or cause false positives by scanning memory that contains non-pointer data. It relies on `mod->mem[type].is_rox` and memory type assignment already being correct.

## Test Signals
Kmemleak-enabled module load/unload tests should show fewer false positives without suppressing leaks in normal module data. Build coverage with and without `CONFIG_DEBUG_KMEMLEAK` validates the inline stub contract.
