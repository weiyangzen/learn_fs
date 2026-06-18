# sources/distributed-fs/ceph-client/drivers/pci/hotplug/cpqphp_nvram.h

## Purpose
Provides the compile-time interface for optional Compaq NVRAM support. It either declares the real NVRAM load/store functions or supplies no-op inline stubs when NVRAM support is disabled.

## Important APIs, Types, and Functions
The API is `compaq_nvram_init(void __iomem *rom_start)`, `compaq_nvram_load(void __iomem *rom_start, struct controller *ctrl)`, and `compaq_nvram_store(void __iomem *rom_start)`. Without `CONFIG_HOTPLUG_PCI_COMPAQ_NVRAM`, init is empty and load/store return success.

## Control Flow
`cpqphp_core.c` calls these hooks unconditionally. The header makes that code independent of the Kconfig option: disabled builds proceed with ROM/HRT resource discovery and skip persistent resource overlay/store, while enabled builds link to `cpqphp_nvram.c`.

## State and Persistence Behavior
The header itself has no state. Its build-time branch determines whether resource-list persistence exists at all. In disabled builds, no durable state is read or written and store reports success.

## Dependencies and Integration Points
Depends on `struct controller` from `cpqphp.h` being visible to callers and on `void __iomem *` ROM mappings supplied by the core. It is included by both `cpqphp_core.c` and `cpqphp_pci.c`, though persistence is implemented only in the C file.

## Risks
The no-op stubs make persistence failures impossible to distinguish from intentionally disabled support. Callers must not assume persisted resources were loaded just because `compaq_nvram_load()` returns zero in disabled builds.

## Test Signals
Compile both Kconfig paths, verify no unresolved symbols when disabled, verify real symbols are linked when enabled, and check that resource discovery still works when persistence is absent.
