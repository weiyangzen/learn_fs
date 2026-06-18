# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/platform.h

## Purpose
`platform.h` defines the HFI1 platform configuration table schema, field IDs, packed scratch-register bit layouts, link/cable tuning encodings, masks, and public platform/tuning APIs used by `platform.c` and related link code.

## Important APIs, Types, And Functions
The header enumerates platform table types (system, port, RX preset, TX preset, QSFP attenuation, variable settings) and per-table field IDs. `struct platform_config` stores a raw binary image; `struct platform_config_data` and `struct platform_config_cache` provide parsed table/metadata references. It defines encodings for QSFP power classes, port types, link speed/width support, VL capability, MTU capability, timeout values, and tuning method. It declares `get_platform_config()`, `free_platform_config()`, `get_port_type()`, `set_qsfp_tx()`, and `tune_serdes()`.

## Control Flow
The constants describe how platform-table records and metadata are decoded and how integrated-platform scratch registers pack port type, attenuation, QSFP power, TX presets, RX presets, bitmap version, and checksum. Consumers read fields by table/record/field ID and translate them into link policy and tuning commands.

## State And Persistence
The header does not own state, but it defines the in-memory representations for raw and parsed platform config plus the persistent meaning of BIOS/EPROM/firmware table data. Scratch-register fields act as firmware-provided boot-time platform state for integrated systems.

## Dependencies And Integration Points
It integrates platform parsing with HFI1 device/port data, QSFP policy, 8051 tuning, OPA link capabilities, and firmware/EPROM data sources. The bit masks must match hardware scratch-register and platform binary format definitions.

## Risks
Field IDs and masks are ABI-like contracts with platform firmware and table generators; drift will cause wrong tuning without compiler errors. Some encodings are subsets rather than exhaustive OPA capabilities. The scratch checksum/version constants must remain aligned with BIOS producers.

## Test Signals
Validate table parsing against known binaries, scratch-register decoding for HFI0/HFI1, mask/shift round trips, all enum boundary values, unknown/reserved table types, and compatibility with platform firmware revisions.
