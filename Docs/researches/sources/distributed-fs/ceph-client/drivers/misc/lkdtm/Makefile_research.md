# sources/distributed-fs/ceph-client/drivers/misc/lkdtm/Makefile

## Purpose
The LKDTM Makefile builds the Linux Kernel Dump Test Module object set and applies special build rules needed for specific tests.

## Important APIs, types, and functions
`obj-$(CONFIG_LKDTM) += lkdtm.o` creates the composite module. Component objects include `core.o`, `bugs.o`, `heap.o`, `perms.o`, `refcount.o`, `rodata_objcopy.o`, `usercopy.o`, `kstack_erase.o`, `cfi.o`, `fortify.o`, and optional `powerpc.o`. Special flags disable KASAN for `stackleak.o`, remove LTO/rethunk/CFI flags from `rodata.o`, and use objcopy to rename `.noinstr.text` into `.rodata` for rodata tests.

## Control flow
Kbuild assembles `lkdtm.o` from the listed objects when LKDTM is enabled. The custom target builds `rodata_objcopy.o` from `rodata.o` through `if_changed,objcopy`.

## State and persistence
No runtime state exists. Build-time state controls whether LKDTM tests are instrumented or deliberately uninstrumented in ways required by the test cases.

## Dependencies and integration points
The file integrates LKDTM with Kbuild, compiler instrumentation flags, objcopy, and architecture-specific optional sources. It ensures CFI and rodata tests can exercise intended mitigation boundaries.

## Risks
Incorrect instrumentation flags can invalidate LKDTM results: tests may fail to trigger or be blocked by unrelated compiler transformations. Missing component objects would hide crash types from `core.o` registration.

## Test signals
Build tests should verify LKDTM links with `CONFIG_LKDTM`, the objcopy rule runs, `rodata_objcopy.o` has the expected section rename, and CFI/LTO flag removal is reflected in compile commands.
