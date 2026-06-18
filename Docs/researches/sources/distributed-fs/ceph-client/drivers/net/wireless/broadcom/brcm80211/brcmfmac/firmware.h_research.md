# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/firmware.h

Purpose: Declares firmware mapping macros, request item types, request structures, and firmware loading APIs for bus-specific probe/upload code.

Important APIs/types/functions: Defines optional flag, firmware name/path limits, default path, max board types, `struct brcmf_firmware_mapping`, `BRCMF_FW_DEF`, `BRCMF_FW_CLM_DEF`, `BRCMF_FW_ENTRY`, `enum brcmf_fw_type`, `struct brcmf_fw_item`, `struct brcmf_fw_request`, and `struct brcmf_fw_name`.

Control flow: Bus code declares mapping tables, allocates a request, fills metadata such as board types and item flags/types, then calls async firmware loading.

State and persistence behavior: Request structures hold firmware references or allocated NVRAM data until consumed/freed.

Dependencies and integration points: Uses Linux firmware API and module firmware metadata; connects chip detection to linux-firmware naming.

Risks: Path length can truncate. Revmask matching requires chiprev below 32. Optional flags must be correct to avoid aborting probe on intentionally absent files.

Test signals: Firmware aliases, revmask matching, path construction/truncation, optional item handling, and callback behavior.
