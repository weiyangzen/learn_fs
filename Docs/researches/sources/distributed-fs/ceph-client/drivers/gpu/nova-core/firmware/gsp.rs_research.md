# sources/distributed-fs/ceph-client/drivers/gpu/nova-core/firmware/gsp.rs

## Purpose

`firmware/gsp.rs` loads the main GSP firmware ELF, maps it through a three-level radix page table for the GSP bootloader, maps matching signatures, and loads the RISC-V bootloader firmware.

## Important APIs, Types, And Functions

`GspFirmware` owns SG tables for firmware, level2, level1, a coherent level0 table, firmware size, signatures, and `RiscvFirmware` bootloader. `GspFirmware::new()` constructs all pieces. `radix3_dma_handle()` returns the level0 DMA address. `map_into_lvl()` emits little-endian DMA page entries for SG mappings.

## Control Flow

`new()` requests `gsp`, extracts the `.fwimage` ELF section, copies it into a `VVec`, maps it as SG to the device, builds level2 entries pointing to firmware pages, builds level1 entries pointing to level2 pages, and stores the first level1 DMA address in a coherent level0 page. It selects the signature ELF section by architecture/chipset, maps it coherently, requests `bootloader`, and parses it as `RiscvFirmware`.

## State And Persistence Behavior

Pinned `GspFirmware` keeps all mapped SG and coherent objects alive through GSP boot. The GSP boot metadata references the level0 radix table, firmware size, signature DMA address, and bootloader DMA address. Firmware data is read-only from the driver after construction.

## Dependencies And Integration Points

It depends on firmware request helpers, the temporary ELF section parser, DMA SG tables, coherent allocations, `Chipset`/`Architecture`, `RiscvFirmware`, and GSP page constants. `FbLayout` and `GspFwWprMeta` consume its sizes and DMA handles.

## Risks And Test Signals

Risks include ELF section name drift, SG entry page rounding, endian assumptions for page-table entries, firmware/signature architecture mapping, and lifetime requirements for mapped tables. Test by loading all supported chipset firmware variants, verifying radix3 tables with multi-entry SG mappings, missing section failures, bootloader parse failures, and successful Booter consumption of WPR metadata.
