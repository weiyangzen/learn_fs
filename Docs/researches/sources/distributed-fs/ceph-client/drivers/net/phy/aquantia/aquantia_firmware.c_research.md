# sources/distributed-fs/ceph-client/drivers/net/phy/aquantia/aquantia_firmware.c

## Purpose
Loads Aquantia firmware into PHY DRAM and IRAM when no firmware is already running. Firmware can come from an NVMEM cell or from a filesystem firmware file named by device property.

## Important APIs, Types, and Functions
Important helpers include `aqr_fw_validate_get`, endian-safe readers `aqr_fw_get_be16`, `aqr_fw_get_le16`, `aqr_fw_get_le24`, memory loader `aqr_fw_load_memory`, boot parser `aqr_fw_boot`, source-specific loaders `aqr_firmware_load_nvmem` and `aqr_firmware_load_fs`, and exported `aqr_firmware_load`. `struct aqr_fw_header` describes the packed offsets/sizes for IRAM and DRAM sections.

## Control Flow and State
`aqr_firmware_load` first calls `aqr_wait_reset_complete`; if firmware appears to be running, it returns without loading. On timeout, it tries the `firmware` NVMEM cell, allowing probe defer or success, then falls back to `firmware-name` and `request_firmware`. `aqr_fw_boot` validates the file CRC, primary offset, section header bounds, word alignment, DRAM/IRAM bounds, and version string. It stalls the embedded processor, writes DRAM and IRAM through mailbox registers with running CRC verification, clears reset/low-power state, pulses UP reset, and releases the processor.

## Dependencies and Integration Points
Depends on `crc_itu_t`, firmware loader APIs, NVMEM consumer APIs, unaligned access helpers, Aquantia mailbox register definitions from `aquantia.h`, and `aqr_wait_reset_complete` from the main module. Device tree or firmware-node data supplies `firmware-name` or an NVMEM cell named `firmware`.

## Risks and Test Signals
Risks include accepting malformed firmware, integer/bounds mistakes in section parsing, mailbox writes without error checking on every setup write, CRC mismatch from endianness assumptions, and assuming a timeout means no firmware is running. Test signals include booting with already-loaded firmware, NVMEM and filesystem firmware paths, invalid CRC and malformed offset tests, mailbox CRC mismatch injection, and confirmation that the PHY reports a firmware ID after load.
