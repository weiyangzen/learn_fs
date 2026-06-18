# sources/distributed-fs/ceph-client/tools/testing/nvdimm/Kbuild

## Purpose
This `Kbuild` file builds the nvdimm test module stack by combining real driver sources with local test overrides. It enables link-time wrapping of kernel APIs so nvdimm, pmem, dax, and ACPI NFIT drivers can run against synthetic resources instead of real platform firmware or physical persistent memory.

## Important APIs, Types, And Functions
The file is build metadata rather than C code. Important declarations are the `ldflags-y += --wrap=...` lines for ioremap, memremap, resource request/release, ACPI evaluate calls, and `devm_memremap_pages`; source roots `DRIVERS`, `NVDIMM_SRC`, `ACPI_SRC`, and `DAX_SRC`; and module object lists such as `nfit-y`, `nd_pmem-y`, `device_dax-y`, `dax_pmem-y`, and `libnvdimm-y`.

## Control Flow
At build time, kbuild conditionally assembles modules based on configuration symbols. For example, `nfit-y` includes real ACPI NFIT core/intel code plus `acpi_nfit_test.o` and `config_check.o`, while `libnvdimm-y` includes real libnvdimm core objects plus `libnvdimm_test.o`. `obj-m += test/` delegates to the nested test module directory.

## State And Persistence
No runtime state is defined here. The persistent effect is the module composition and linker wrapping strategy encoded in build artifacts.

## Dependencies And Integration Points
This file integrates directly with in-tree kernel driver sources under `drivers/nvdimm`, `drivers/acpi/nfit`, and `drivers/dax`. It depends on the wrapper implementations in `test/iomap.c` and local watermark files to prove test-linked modules are loaded.

## Risks
The build is highly sensitive to internal driver object names and symbol signatures. New driver files, renamed functions, or changed wrapped API prototypes can silently omit behavior or fail module linking. The `KBUILD_CFLAGS` filtering removes missing-prototype/declaration warnings, which is practical for wrapping but can hide drift.

## Test Signals
Successful module build verifies that target config symbols are module-compatible and that wrapped symbols resolve. Runtime watermark calls and `config_check.o` provide additional signals that test modules, not base-tree modules, are active.
