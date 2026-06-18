<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/Makefile -->
# sources/distributed-fs/ceph-client/drivers/nvmem/Makefile

## Purpose
Maps NVMEM Kconfig symbols to built-in or module objects and aggregates multi-object modules for the framework core, layout bus, and individual provider drivers.

## Important APIs, Types, And Functions
Build targets include `nvmem_core.o` from `core.o`, `nvmem_layouts.o` from `layouts.o`, unconditional descent into `layouts/`, and per-provider module aliases such as `nvmem-an8855-efuse.o`, `nvmem-apple-efuses.o`, `apple_nvmem_spmi.o`, `nvmem-bcm-ocotp.o`, `nvmem_brcm_nvram.o`, i.MX modules, and many other SoC drivers.

## Control Flow
Kbuild evaluates `obj-$(CONFIG_...)` lines and then uses `foo-y := file.o` assignments to assemble module names from source files. Layout subdirectory objects are built only when their own Kconfig symbols select them.

## State And Persistence
No runtime state. The file defines build artifacts and therefore module names and object inclusion.

## Dependencies And Integration Points
Must stay synchronized with `drivers/nvmem/Kconfig`, `drivers/nvmem/layouts/Makefile`, and source filenames. It also reflects naming conventions used by module loading and distribution packaging.

## Risks
Mismatched object names break builds or produce unexpected module filenames. Because several object names use hyphen/underscore variants, renames are easy to get wrong. Unconditional `obj-y += layouts/` is safe only because the subdirectory Makefile is symbol-gated.

## Test Signals
Build all listed NVMEM symbols as modules and built-ins, verify `modinfo` names for selected providers, and run `make W=1` to catch stale or missing source mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/Makefile -->
