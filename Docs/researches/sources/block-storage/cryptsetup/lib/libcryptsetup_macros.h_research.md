# File Research: sources/block-storage/cryptsetup/lib/libcryptsetup_macros.h

This header defines common internal constants and generic macros for libcryptsetup.

Key macros:
- Casting/helper macros: `CONST_CAST`, `VOIDP_CAST`, `UNUSED`, `ARRAY_SIZE`, `BITFIELD_SIZE`.
- Ownership helpers: `MOVE_REF` transfers a pointer-like reference and nulls the source; `FREE_AND_NULL` frees and nulls.
- Utility expression: `AT_LEAST`.
- Sector/alignment constants: `SECTOR_SHIFT`, `SECTOR_SIZE`, `SHIFT_4K`, `MAX_SECTOR_SIZE`, `ROUND_SECTOR`.
- Alignment checks: `MISALIGNED`, `MISALIGNED_4K`, `MISALIGNED_512`, `NOTPOW2`.
- Default alignment constants: `DEFAULT_DISK_ALIGNMENT` and `DEFAULT_MEM_ALIGNMENT`.
- Device-mapper naming constants: `DM_UUID_LEN`, `DM_NAME_LEN`, `DM_BY_ID_PREFIX`, `DM_UUID_PREFIX`, and matching prefix lengths.
- OPAL constant: `OPAL_PSID_LEN`.
- LUKS constants: `LUKS_STRIPES` defaults to 4000; `LUKS2_OBJECTS_MAX` defaults to 32.

Filesystem/block-storage relevance:
- Sector and alignment macros are used across cryptsetup when validating block offsets, keyslot storage sizes, and device-mapper table geometry.
- DM UUID/name constants define the naming limits and prefixes used by active mapped block devices.
- `LUKS_STRIPES` is the fixed anti-forensic stripe count used by LUKS1 key material splitting.
