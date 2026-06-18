# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/fw_inc.c

## Purpose
`fw_inc.c` implements firmware and board-file verification, parsing, and download. It validates firmware containers, extracts capabilities and board metadata during a parse-only pass, writes data/fill/direct/gateway records to device memory during a load pass, and loads board files either at firmware-provided addresses or through the older firmware-file path.

## Important APIs, Types, And Functions
`wil_fw_verify()` checks dword alignment, header presence, file length, signature, format version, and CRC. `wil_fw_process()` iterates records and dispatches through `wil_fw_handlers[]`. Comment handlers parse capabilities (`fw_handle_capabilities()`), board-file entries (`fw_handle_brd_file()`), and cfg80211 concurrency limits (`fw_handle_concurrency()`). Load handlers include `fw_handle_data()`, `fw_handle_fill()`, `fw_handle_direct_write()`, `fw_handle_gateway_data()`, and `fw_handle_gateway_data4()`. Public entry points are `wil_request_firmware()`, `wil_request_board()`, and `wil_fw_verify_file_exists()`.

## Control Flow
`wil_request_firmware()` requests a firmware blob, clears previous board metadata, then loops over concatenated firmware sections. Each section is verified and processed either in parse mode or load mode. Parse mode only handles metadata records and file headers; load mode performs MMIO writes. Board loading first verifies the board file, then `wil_brd_process()` skips the header and writes each data record to the corresponding address/limit gathered from firmware metadata.

## State And Persistence
The parser mutates `wil->fw_capabilities`, `wil->fw_version`, `wil->brd_info`, `wil->num_of_brd_entries`, and device memory. It releases and reallocates board metadata per firmware request. Firmware bytes are not retained after `release_firmware()`.

## Dependencies And Integration Points
It depends on the Linux firmware loader, CRC32, WMI address translation (`wmi_buffer_block()`), 32-bit MMIO copy/fill helpers from `main.c` and `fw.c`, cfg80211 combination construction, and hardware firmware mappings. `main.c` uses it in reset/up paths; `pcie_bus.c` uses parse-only firmware requests to discover capabilities before the full load.

## Risks
This is a trust boundary for firmware files. Incorrect bounds checks can turn malformed firmware into MMIO corruption. Gateway writes poll with a fixed timeout and fail the load on busy hardware. Board-file processing assumes records match firmware-provided metadata order. Unknown record types fail the load, so format evolution requires synchronized driver support.

## Test Signals
Use synthetic firmware files to cover CRC mismatch, concatenated valid sections, malformed record lengths, direct-write masks, fill alignment failures, gateway timeout, metadata-only parse, board files with too many records, and valid Talyn/Sparrow firmware plus board combinations.
