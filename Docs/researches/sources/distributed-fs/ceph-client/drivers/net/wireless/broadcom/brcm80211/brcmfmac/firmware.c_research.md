# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/firmware.c

Purpose: Allocates firmware requests, asynchronously loads firmware/NVRAM items with board-specific fallback, obtains NVRAM from files/bcm47xx/EFI, normalizes NVRAM text into firmware token format, and frees request resources.

Important APIs/types/functions: `brcmf_fw_alloc_request()`, `brcmf_fw_get_firmwares()`, and `brcmf_fw_nvram_free()`. Internal parser states process key/value/comment text, multi-device v1/v2 NVRAM filtering, default boardrev insertion, platform MAC replacement, EFI ccode fixups, and final token/rounding.

Control flow: Allocation maps chip/revision to firmware basename and fills paths, honoring global alternate path. Async load first tries board-specific first-item paths, then canonical. Completion processes each item sequentially: binary items store firmware; NVRAM items strip file/bcm47xx/EFI data. Mandatory failure frees the request and calls callback with error.

State and persistence behavior: Request context and NVRAM output are heap allocated. Binary firmware references are held until released. No persistent files are written.

Dependencies and integration points: Uses Linux firmware_class, EFI, bcm47xx NVRAM, platform MAC lookup, common global firmware path, chip naming, and bus mapping tables.

Risks: Async ownership is subtle. Board-specific fallback spans up to eight board types. NVRAM parser truncates very large inputs, strips invalid keys and `RAW1`, and can return empty output when multi-device domain/bus does not match. EFI ccode rewriting is targeted.

Test signals: Known/unknown chip mapping, alternative path with/without slash, board-specific fallback, optional vs mandatory NVRAM, bcm47xx/EFI fallback, multi-device NVRAM, platform MAC replacement, default boardrev, partial-failure cleanup.
