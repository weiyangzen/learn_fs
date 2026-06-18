<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sym53c8xx_2/sym_fw.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/sym53c8xx_2/sym_fw.c

## Purpose
`sym_fw.c` instantiates, selects, patches, sets up, and relocates the Symbios SCRIPTS firmware templates. It includes firmware template headers under different symbol names, builds offset tables, fills runtime-generated scatter-gather script slots, computes bus-address tables, chooses firmware by chip features, and binds script operands to physical/MMIO addresses.

## Important APIs, Types, And Functions
Externally important functions are `sym_find_firmware()` and `sym_fw_bind_script()`. Internal setup/patch functions include `sym_fw1_patch()`, `sym_fw2_patch()`, `sym_fw_fill_data()`, `sym_fw_setup_bus_addresses()`, `sym_fw1_setup()`, and `sym_fw2_setup()`. Static firmware descriptors `sym_fw1` and `sym_fw2` are built with `SYM_FW_ENTRY()`, with firmware #1 present when `SYM_CONF_GENERIC_SUPPORT` is enabled and firmware #2 always present.

## Control Flow
At compile time the file includes `sym_fw1.h` and `sym_fw2.h` with macro-renamed script objects, then initializes offset tables through `SYM_GEN_FW_A/B/Z`. At runtime, `sym_find_firmware()` returns the load/store firmware for chips with `FE_LDSTR`, otherwise the generic firmware for older chips that do not require prefetch, phase-mismatch, or DAC features.

Firmware setup fills `data_in` and `data_out` script arrays for `SYM_CONF_MAX_SG` entries using `SCR_CHMOV_TBL` and offsets into `struct sym_dsb`, then builds host-side script label bus-address tables from base DMA addresses and offset tables. Patch functions remove LED instructions when unsupported, optionally remove IARB hints, patch queue and target-table bus addresses, remove 64-bit DMA dirty-map logic when DAC is unavailable, remove C1010-only reselection or workaround paths when not applicable, and patch phase-mismatch mini-script addresses.

`sym_fw_bind_script()` walks a script dword stream, converts opcodes to script endian, checks illegal zero opcodes, turns `SCR_DATA_ZERO` placeholders into zero, determines how many operands require relocation based on opcode class, removes `SCR_NO_FLUSH` when prefetch is unsupported, adjusts MOVE/CHMOV forms for non-wide chips, and relocates register, script A/B label, and host-control-block references to actual bus/MMIO addresses.

## State And Persistence Behavior
The file mutates per-adapter in-memory script copies through setup, patch, and bind. Persistent device state is not stored. Script templates are static; runtime state is derived from `struct sym_hcb` DMA/MMIO base addresses, feature flags, queue bus addresses, target table address, PCI device ID/revision, and clock.

## Dependencies And Integration Points
It depends on `sym_glue.h`, `sym_fw.h`, `sym_fw1.h`, `sym_fw2.h`, `sym_defs.h` opcodes, `struct sym_hcb`, `struct sym_data`, PCI IDs, feature flags, endian conversion via `cpu_to_scr()`, and debug/panic helpers. It is the bridge between C host data structures and the SCRIPTS processor code executed by the controller.

## Risks
Risks include mismatched script struct lengths versus initializer contents, incorrect relocation classification, stale patch offsets, feature detection mistakes causing unsupported script instructions, and panic on unexpected relocation tags. Firmware patching writes directly into script copies, so label offsets and struct fields must stay synchronized across headers and generated tables.

## Test Signals
Test firmware selection for `FE_LDSTR`, generic fallback, and unsupported combinations; bind scripts with and without `FE_PFEN`, `FE_WIDE`, `FE_DAC`, `FE_C10`, and C1010 revision workarounds; validate generated bus-address tables; enable `DEBUG_SCRIPT`; run hardware I/O with wide and narrow devices; exercise reselection, phase mismatch, negotiation, abort, and data-overrun paths; and build after any firmware template length change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sym53c8xx_2/sym_fw.c -->
