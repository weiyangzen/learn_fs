# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/ucode_loader.c

Purpose: Initializes and frees the firmware/initval data bundle used by brcmsmac D11 cores.

Important APIs: `brcms_ucode_data_init()` first calls `brcms_check_firmwares()`, then sequentially loads each named firmware/initval buffer or size field into `struct brcms_ucode`: LCN0/1/2 24-bit init values, N0 16-bit init values, MIMO and LCN ucode blobs/sizes, and BOM version buffers. `brcms_ucode_data_free()` frees all buffer fields that were loaded.

Control flow and state: Initialization uses a chained `rc = rc < 0 ? rc : next_load(...)` pattern, stopping on first error. It mutates the caller-provided `brcms_ucode` struct by storing pointers and sizes. Freeing is unconditional for pointer fields; size-only fields are not freed.

Dependencies and integration: Includes `defs.h`, `types.h`, and `ucode_loader.h`. The enum indexes are an implicit contract with lower-level firmware request functions. Risks include partial initialization requiring the caller to invoke free on failure to avoid leaks, enum/order mismatch with firmware name tables, no zeroing in this function, and firmware availability at probe time. Test signals include missing/short firmware files, all firmware variants present, partial failure cleanup, probe/remove cycles, and firmware size validation.
