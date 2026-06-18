# sources/distributed-fs/ceph-client/drivers/edac/cpc925_edac.c

## Purpose
This file implements EDAC support for the IBM CPC925 bridge and memory controller. It covers three error domains: the memory controller as an EDAC MC, CPU/processor-interface errors as an EDAC device, and HyperTransport link errors as another EDAC device. All reporting is polling-based.

## Important APIs, Types, And Functions
`struct cpc925_mc_pdata` stores MMIO base, total memory, controller name, and EDAC index. `struct cpc925_dev_info` describes the synthetic EDAC devices that share the memory-controller MMIO base. `cpc925_devs[]` defines CPU and HT-link devices with init/exit/check callbacks.

Important memory-controller functions include `cpc925_probe()`, `cpc925_remove()`, `cpc925_init_csrows()`, `cpc925_mc_init()`, `cpc925_mc_check()`, `cpc925_mc_get_pfn()`, `cpc925_mc_find_channel()`, and `cpc925_get_sdram_scrub_rate()`. Device-side functions include `cpc925_add_edac_devices()`, `cpc925_del_edac_devices()`, `cpc925_cpu_check()`, and `cpc925_htlink_check()`.

## Control Flow
`cpc925_edac_init()` sets polling mode and registers a platform driver. Probe opens a devres group, obtains and maps MMIO, derives channel count from `MBCR`, allocates a chip-select/channel EDAC topology, initializes DIMM/csrow data from OF memory and CPC925 bank registers, enables ECC exception and check bits, registers the memory controller, and then creates synthetic platform devices for CPU and HT-link EDAC devices.

Polling `cpc925_mc_check()` reads the clear-on-read `APIEXCP` register, exits if no ECC exception is present, reads syndrome and address registers, reconstructs PFN/offset from rank/row/bank/column fields, and reports CE or UE through `edac_mc_handle_error()`. CPU polling reads processor-interface exception bits, filters absent CPU interfaces, dumps relevant registers, and reports a UE. HT polling reads bridge/link/error registers, clears write-one-to-clear bits, may initiate secondary bus reset for chain failure, and reports a CE.

## State And Persistence
Hardware exception bits and counters are the source of truth. `cpc925_cpu_mask_disabled()` caches absent-CPU mask in a static variable after inspecting OF CPU nodes. The driver intentionally does not disable memory-controller or CPU error-detection bits on exit because comments warn that re-enabling them on module reload can trigger machine-check exceptions. EDAC core counters persist while devices are registered.

## Dependencies And Integration Points
The driver depends on OF memory and CPU nodes, platform resources, raw MMIO accessors, EDAC MC APIs, EDAC device APIs, and EDAC sysfs. Synthetic platform devices are registered because CPU and HT-link error domains do not have separate firmware nodes.

## Risks
PFN reconstruction is complex and mode-specific, so address attribution is a risk. `APIEXCP` is clear-on-read; multiple polling consumers or careless debug reads could lose state. Some exit callbacks deliberately leave hardware detection enabled, so tests that expect full hardware rollback will be misleading. Error-domain devices share the same MMIO region with the MC, so removal order matters and is correctly handled by deleting EDAC devices before the MC.

## Test Signals
Coverage should include populated and empty bank boundary parsing, single/dual channel configuration, CE/UE exception decoding, CPU-node mask calculation, HT write-one-to-clear behavior, scrub-rate reads, and remove order. Hardware error injection or controlled register emulation is needed to validate the clear-on-read and PFN reconstruction paths.
