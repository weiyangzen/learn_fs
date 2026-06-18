# sources/distributed-fs/ceph-client/arch/parisc/kernel/inventory.c

## Purpose

`inventory.c` discovers PA-RISC firmware type, physical memory ranges, and platform devices. It supports three inventory families: PAT, SYSTEM_MAP, and older Snake/PDC_MEM_MAP machines.

## Important APIs, Types, And Functions

Global firmware classification is stored in `pdc_type __ro_after_init`. PAT systems also fill `parisc_cell_num`, `parisc_cell_loc`, and `parisc_pat_pdc_cap`.

`setup_pdc()` probes firmware type. It tries `pdc_system_map_find_mods()`, then 64-bit PAT `pdc_pat_cell_get_number()`, then legacy bus-ID matching through `pdc_model_info()`. Unsupported types panic.

Memory setup helpers include `set_pmem_entry()`, `pagezero_memconfig()`, 64-bit `pat_memconfig()`, and `sprockets_memconfig()`. Device inventory helpers include `pat_query_module()`, `pat_inventory()`, `legacy_create_device()`, `snake_inventory()`, `add_system_map_addresses()`, and `system_map_inventory()`.

Public init entry points are `do_memory_inventory()` and `do_device_inventory()`.

## Control Flow

`setup_pdc()` determines which later paths run. `do_memory_inventory()` switches on `pdc_type`: PAT uses PAT address maps, SYSTEM_MAP uses the newer PDC memory table with page-zero fallback, and Snake uses page-zero memory. It validates that at least one range exists and that the first starts at PFN 0, otherwise it warns and falls back to page zero.

`do_device_inventory()` initializes the PA-RISC bus and switches on `pdc_type`. PAT inventory loops over cell modules and calls `pat_query_module()` until firmware stops returning modules. SYSTEM_MAP inventory scans module indices up to 255, allocates and registers `parisc_device` objects, then appends additional addresses when reported. Snake inventory synthesizes module paths over legacy module/function ranges and uses `PDC_MEM_MAP_HPA`.

For QEMU with firmware config sysfs enabled, the device inventory reads a SeaBIOS-provided base from `PAGE0->pad0` and registers a `fw_cfg` platform device if present.

## State And Persistence Behavior

The file populates global memory range tables (`pmem_ranges`, `npmem_ranges`), registers `parisc_device` objects, initializes the PA bus, and sets TLB serialization policy on some 64-bit SMP machines. These are boot-time state changes that persist for the running kernel.

## Dependencies And Integration Points

It depends heavily on PDC wrappers from `firmware.c`, PAT definitions, memory zone globals, PA device allocation and registration, central bus walking, platform devices, QEMU `fw_cfg`, and TLB flush policy.

## Risks

Firmware return data is diverse and hardware-specific. Range alignment errors intentionally panic in `set_pmem_entry()`. PAT address-map filtering can exclude memory if usage/type checks are wrong. SYSTEM_MAP scanning has fixed bounds and ignores nonterminal transient errors. Legacy Snake probing can register incomplete device sets if module path assumptions change. Device registration must handle allocation failures without leaking partially initialized firmware objects.

## Test Signals

Signals include boot logs showing correct PDC type, nonzero and correctly bounded memory ranges, expected devices in "Found devices" output, QEMU `fw_cfg` platform-device registration when available, no fallback warnings on known-good firmware, and correct behavior across PAT, SYSTEM_MAP, and legacy Snake machines.
