# sources/distributed-fs/ceph-client/drivers/edac/i10nm_base.c

## Purpose
This is the Intel 10nm server memory-controller EDAC driver for Ice Lake/Tremont, Sapphire/Emerald Rapids, Granite Rapids, and related server CPUs. It discovers socket/IMC PCI resources, maps DDR/HBM memory-controller MMIO windows, registers EDAC memory controllers through `skx_common`, optionally decodes errors from MCA banks, and manages retry-read error log reporting.

## Important APIs and Functions
Resource configuration is encoded in `struct res_config` instances `i10nm_cfg0`, `i10nm_cfg1`, `spr_cfg`, and `gnr_cfg`. Retry-read logging is controlled by `reg_rrl` tables and helpers `enable_rrl()`, `enable_rrls_ddr()`, `enable_rrls_hbm()`, `enable_retry_rd_err_log()`, and `show_retry_rd_err_log()`. Discovery helpers include `pci_get_dev_wrapper()`, `i10nm_get_imc_num()`, `i10nm_check_2lm()`, `get_ddr_munit()`, `i10nm_get_ddr_munits()`, and `i10nm_get_hbm_munits()`. Error decoding uses `i10nm_mc_decode_available()` and `i10nm_mc_decode()`. `i10nm_get_dimm_config()` fills EDAC DIMM metadata.

## Control Flow
Module init rejects GHES-owned systems, conflicting EDAC owners, hypervisors, and unsupported CPUs. It selects a CPU resource config, obtains memory bounds, builds socket bus mappings, adjusts Granite Rapids IMC count when needed, detects 2-level memory, maps DDR and optional HBM munits, registers each present IMC with EDAC, obtains ADXL support, registers the MCE decode chain, sets debug hooks, and configures optional retry-read log handling. Exit reverses retry-read control, debug, MCE notifier, ADXL, and `skx_remove()`.

## State and Persistence
Static state includes `i10nm_edac_list`, selected `res_cfg`, module parameters `retry_rd_err_log` and `decoding_via_mca`, and `mem_cfg_2lm`. Per-socket/per-IMC state lives in `skx_dev` and `skx_imc` structures from `skx_common`, including PCI references, MMIO mappings, channel sizes, and saved retry-log controls.

## Dependencies and Integration
The driver is tightly integrated with `skx_common.h`, x86 CPU matching, PCI config space, MCE notifier chains, Intel-family IDs, ADXL decoding, EDAC core registration, and optional debug hooks.

## Risks
Hardware topology discovery is complex and generation-specific. Granite Rapids mutates the selected resource config based on runtime channel count and rebuilds bus mappings. MCA decoding is disabled for 2LM and DDRT cases. Retry-read log mode `2` actively changes hardware control bits and must restore them on exit. Many PCI/MMIO reads assume valid mapped resources after discovery.

## Test Signals
Signals include probe rejection under GHES/hypervisor/conflicting owner, correct IMC/channel/DIMM enumeration for each CPU family, CE/UE decoding from MCEs, retry-read log output/clearing in configured modes, HBM detection on SPR, and clean unmap/reference release through `skx_remove()`.
