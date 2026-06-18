# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/runtime.h

## Purpose
Declares the central firmware runtime object shared by iwlwifi opmodes. It binds a transport, parsed firmware image, paging state, shared-memory layout, dump workers, UEFI/BIOS regulatory caches, timestamp/debug state, and runtime operations.

## Important APIs, Types, and Functions
Important types are `iwl_fw_runtime_ops`, `iwl_fwrt_shared_mem_cfg`, `iwl_fwrt_dump_data`, `iwl_fwrt_wk_data`, `iwl_txf_iter_data`, and `iwl_fw_runtime`. Public lifecycle/control functions include `iwl_fw_runtime_init`, `iwl_fw_runtime_free`, `iwl_fw_runtime_suspend`, `iwl_fw_runtime_resume`, `iwl_fw_set_current_image`, `iwl_init_paging`, `iwl_free_fw_paging`, `iwl_get_shared_mem_conf`, `iwl_set_soc_latency`, and `iwl_configure_rxq`.

## Control Flow
The header describes runtime state; implementation code initializes it before firmware interaction, updates `cur_fw_img` as images change, queries shared memory after alive, allocates paging, and frees timers/workers during teardown. `iwl_fw_runtime_free()` cancels dump workers and debug timers.

## State and Persistence Behavior
Most fields are in-memory caches derived from firmware, UEFI/ACPI, or module configuration. Paging DMA blocks, shared-memory FIFO sizes, DSM values, SAR/GEO/PPAG tables, and debug worker state persist for the lifetime of the active firmware runtime.

## Dependencies and Integration Points
Depends on `iwl-config.h`, `iwl-trans.h`, firmware image/debug/paging/power APIs, NVM utilities, ACPI helpers, and regulatory contracts. It is consumed by MVM/MLD runtime, debug collection, paging, RX queue setup, and regulatory command code.

## Risks
Teardown ordering is sensitive: delayed dump workers and periodic debug timers must be stopped before transport memory disappears. Many cached arrays mirror firmware/BIOS maxima, so table parsers must respect the declared bounds.

## Test Signals
Firmware runtime init/free across normal load, failed load, suspend/resume, D3 debug, paging allocation/free, shared-memory command parsing, debug dump worker cancellation, EFI/ACPI regulatory table population, and no-EFI builds are key signals.
