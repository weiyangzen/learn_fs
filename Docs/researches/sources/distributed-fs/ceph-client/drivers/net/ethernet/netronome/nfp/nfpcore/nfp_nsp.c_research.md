# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_nsp.c

Purpose: Implements the NFP Service Processor command protocol for firmware loading, flash writing, Ethernet table access, sensor/identify queries, HWInfo operations, version strings, media data, and module EEPROM reads.

Important APIs/types/functions: `struct nfp_nsp` holds CPP, locked NSP resource, ABI version, and Ethernet config staging state. `struct nfp_nsp_command_arg` and `_buf_arg` describe commands. Public APIs include `nfp_nsp_open/close/wait`, reset/MAC/FW commands, HWInfo lookup/set, firmware-loaded query, versions parsing, module EEPROM, media reads, and lower-level Ethernet table read/write functions.

Control flow: `nfp_nsp_open()` acquires `NFP_RESOURCE_NSP` and validates magic/ABI/busy state. `__nfp_nsp_command()` writes buffer and command registers, waits for command start to clear, waits for status busy to clear, extracts return option/result, and maps NSP errors to negative errno. Buffer commands use the default NSP buffer when large enough, otherwise DMA/SG descriptors when supported. Firmware load and flash write wrap buffer commands with command-specific options and timeouts.

State and persistence: The NSP resource lock serializes command access. Device registers and default buffers hold transient command state. Firmware load/flash/HWInfo/ETH control commands may change persistent device or flash configuration depending on command. `state->entries`, `idx`, and `modified` stage Ethernet table edits for `nfp_nsp_eth.c`.

Dependencies/integration: Depends on CPP scalar/bulk access, resource locking, DMA mapping, firmware blobs, and ABI feature tests in `nfp_nsp.h`. Used by Ethernet port discovery/configuration, hwmon, firmware management, and NIC probe flows.

Risks: DMA buffer alignment and SG capability handling are hardware/firmware-sensitive. Long flash writes have large timeout windows. Buffer zeroing and size caps protect firmware ABI but need tests. ABI minor checks gate optional features. This source snapshot has a few duplicated/truncated-looking lines, so compile validation is essential.

Test signals: NSP open on supported/unsupported ABI, NOOP wait, default-buffer and DMA-buffer commands, firmware load result messages, flash write timeout behavior, HWInfo null termination, version-string bounds, EEPROM partial-read errors, and concurrent NSP resource serialization.
