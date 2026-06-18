# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/ucode_loader.h

Purpose: Defines the brcmsmac firmware-loader data structure and loader/free helper prototypes.

Important APIs/types: `struct brcms_ucode` holds pointers for D11 initval tables (`struct d11init *`), little-endian ucode blobs, ucode blob byte sizes, and BOM major/minor buffers. The header declares high-level `brcms_ucode_data_init/free()` plus lower-level `brcms_ucode_init_buf()`, `brcms_ucode_init_uint()`, `brcms_ucode_free_buf()`, and `brcms_check_firmwares()`. `MIN_FW_SIZE`, `MAX_FW_SIZE`, and `UCODE_LOADER_API_VER` define loader constraints/versioning.

Control flow and state: No executable flow in the header. The struct persists firmware buffer ownership for the lifetime of the driver instance or hardware object that owns it.

Dependencies and integration: Includes `types.h` for forward declarations and integer types. Integrates with Linux firmware loading and D11 initialization code that consumes initvals and ucode arrays. Risks include pointer ownership ambiguity, size type mismatch across blobs, firmware size constants becoming stale, and callers forgetting cleanup after partial initialization. Test signals include firmware request tests, version/size checks, init path success, failure cleanup, and endian correctness when writing ucode to hardware.
