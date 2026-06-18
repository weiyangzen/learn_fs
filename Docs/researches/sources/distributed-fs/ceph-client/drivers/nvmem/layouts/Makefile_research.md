<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/layouts/Makefile -->
# sources/distributed-fs/ceph-client/drivers/nvmem/layouts/Makefile

## Purpose
Maps layout Kconfig symbols to parser module objects.

## Important APIs, Types, And Functions
Build mappings are `CONFIG_NVMEM_LAYOUT_SL28_VPD -> sl28vpd.o`, `CONFIG_NVMEM_LAYOUT_ONIE_TLV -> onie-tlv.o`, and `CONFIG_NVMEM_LAYOUT_U_BOOT_ENV -> u-boot-env.o`.

## Control Flow
Kbuild descends into the directory from the parent Makefile, then includes only objects whose symbols are enabled.

## State And Persistence
No runtime state; it determines module/built-in object inclusion.

## Dependencies And Integration Points
Must stay synchronized with `layouts/Kconfig` and layout source files.

## Risks
Stale object names or missing entries cause selected layout drivers not to build. The simple mapping makes regressions easy to spot in allmodconfig.

## Test Signals
Build each layout as module and built-in, run `make M=drivers/nvmem/layouts`, and verify resulting module names match Kconfig expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/layouts/Makefile -->
