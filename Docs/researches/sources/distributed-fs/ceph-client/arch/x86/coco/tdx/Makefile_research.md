# sources/distributed-fs/ceph-client/arch/x86/coco/tdx/Makefile

## Purpose
Build manifest for x86 Intel TDX guest support under `arch/x86/coco/tdx`.

## Important APIs, Types, And Functions
No runtime APIs are defined here. The manifest unconditionally adds `debug.o`, `tdcall.o`, `tdx.o`, and `tdx-shared.o` to `obj-y` when the directory is selected by the surrounding kernel build.

## Control Flow And State
The Makefile has no control flow beyond kbuild object composition. It keeps assembly TDCALL wrappers, shared memory acceptance/hypercall code, debug attribute printing, and main TDX guest logic in one linked unit.

## Dependencies And Integration
Depends on parent Kconfig/build selection for TDX guest code and on each listed object compiling with matching symbols: `tdx.o` consumes `__tdcall*` and `tdx_accept_memory()`, while debug helpers are called during TDX announcement.

## Risks And Test Signals
Risks are omitted objects causing unresolved symbols or dead TDX functionality. Signals are allyesconfig/allmodconfig x86 builds and TDX guest boot reaching `tdx_early_init()` and attribute reporting.
