# sources/distributed-fs/ceph-client/fs/pstore/Makefile

## Purpose
The Makefile maps pstore Kconfig symbols to built objects and modules.

## Important APIs, types, and functions
It builds `pstore.o` from `inode.o` and `platform.o`, conditionally adds `ftrace.o` and `pmsg.o`, builds `ramoops.o` from `ram.o` and `ram_core.o`, `pstore_zone.o` from `zone.o`, and `pstore_blk.o` from `blk.o`.

## Control flow
The kernel build system includes objects according to `CONFIG_PSTORE*` symbols. Frontend objects are linked into the generic pstore module, while RAM, zone, and block backends remain separate objects/modules.

## State and persistence
No runtime state exists here; it defines build composition and therefore which persistence mechanisms can exist at runtime.

## Dependencies and integration points
It integrates Kbuild, pstore core, frontend options, and backend modules.

## Risks and test signals
Risks are missing object inclusion for a selected feature or link errors when optional stubs and real implementations diverge. Test signals are allmodconfig, builtin-only pstore, modular ramoops, modular pstore_blk, and configurations with ftrace or pmsg disabled.
