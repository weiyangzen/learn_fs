# sources/distributed-fs/ceph-client/drivers/bluetooth/btqca.c

## Purpose
Provides shared Qualcomm/Atheros Bluetooth setup helpers, primarily for UART and SMD transports. It reads controller version/build metadata, chooses and downloads rampatch and NVM files, edits NVM TLVs for baudrate/sleep/BD address, handles SoC-specific firmware naming and fallbacks, disables logging where needed, performs HCI reset, and exposes BD address and pre-shutdown vendor commands.

## Important APIs, Types, And Functions
- `qca_read_soc_version`, `qca_uart_setup`, `qca_set_bdaddr_rome`, `qca_set_bdaddr`, and `qca_send_pre_shutdown_cmd` are exported transport-facing APIs.
- `qca_tlv_check_data`, `qca_tlv_send_segment`, `qca_download_firmware`, and `qca_inject_cmd_complete_event` validate, mutate, segment, download, and complete patch/NVM transfers.
- `qca_read_fw_build_info`, `qca_read_fw_board_id`, `qca_get_nvm_name_by_board`, `qca_send_patch_config_cmd`, `qca_disable_soc_logging`, and `qca_check_bdaddr` implement SoC-specific setup details.
- `qca_filename_has_extension` and `qca_get_alt_nvm_file` implement board-specific NVM fallback to `.bin`.

## Control Flow
UART setup computes a combined SoC version and ROM-derived firmware suffix, optionally sends WCN6750 patch config, selects a rampatch filename from SoC type or caller override, downloads it, waits briefly, optionally reads board ID, selects an NVM filename from caller override, board ID, ROM version, SoC variant, or legacy fallback, downloads it, disables logging on newer chips, sets Microsoft vendor opcode for WCN399x/WCN6750-class chips, sends HCI reset, reads firmware build info for selected chips, and checks whether a default NVM BD address should trigger the BDADDR property quirk. Firmware download requests the file, copies it into mutable vmalloc memory, validates TLV/ELF metadata, updates NVM tags, sends 243-byte max EDL segments, and injects a command-complete event when the controller skips ordinary completion events.

## State And Persistence
`struct qca_fw_config` is the main transient setup state: firmware type/name, user baudrate, download event-skip mode, and BD address extracted from NVM. Controller state persists after setup through downloaded firmware/NVM, disabled logging, HCI reset, and vendor opcode settings on `hdev`. Firmware blobs are copied to mutable memory only for the duration of TLV patching and download.

## Dependencies And Integration Points
Depends on HCI sync command APIs, firmware loading, vmalloc, Bluetooth address helpers, and definitions in `btqca.h`. It integrates with QCA UART transports, Qualcomm SMD BD address setting through Rome NVM access, Linux firmware naming conventions under `qca/`, HCI quirks for BD address properties, and Microsoft vendor extension opcode setup.

## Risks And Edge Cases
Event format differs by SoC generation: WCN3991+ often returns command-complete payloads where older chips use vendor events. Download mode can skip intermediate completions, requiring the injected command-complete path to avoid HCI command timeout noise. TLV parsing mutates NVM data in place and must bounds-check nested/enclosed TLV sets. Firmware naming has many SoC/board/manufacturer variants; wrong board ID fallback can silently load a generic NVM. `qca_tlv_send_segment` logs TLV response `result` but does not currently convert a nonzero result into `err`, so a controller-side segment error may not fail setup.

## Test Signals
Test version-read paths for pre-WCN3991 and WCN3991+ chips, rampatch/NVM naming for every `qca_btsoc_type`, WCN6750 mbn-to-tlv fallback, WCN6855 legacy filename fallback, board-specific NVM and `.bin` fallback, malformed TLV lengths/tags, skipped-event firmware download with injected command complete, logging-disable failures, HCI reset failures, build-info parsing, and BDADDR quirk detection when public address matches NVM address.
