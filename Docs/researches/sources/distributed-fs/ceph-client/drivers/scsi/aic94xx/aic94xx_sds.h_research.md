# sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx_sds.h

Purpose: this header provides the public flash/SDS constants and prototypes used by aic94xx code that reads adapter configuration or updates flash.

Important APIs/types/functions: it defines flash programming methods (`FLASH_METHOD_UNKNOWN`, `FLASH_METHOD_A`, `FLASH_METHOD_B`), manufacturer/device IDs, DQ status-bit masks, erase/write poll delays, sector size/mask, error/status codes, and firmware image header structures (`controller_id`, `image_info`, `bios_file_header`). Function prototypes expose `asd_verify_flash_seg()`, `asd_write_flash_seg()`, `asd_chk_write_status()`, `asd_check_flash_type()`, and `asd_erase_nv_sector()`.

Control flow and state: no control flow is implemented here. `aic94xx_sds.c` uses these constants to detect flash command-set style, program/erase flash sectors, and return stable status codes. The `bios_file_header` and image descriptors describe BIOS image files rather than in-kernel runtime state.

Persistence behavior: constants in this header gate persistent flash operations. Callers using the write/erase prototypes can mutate NVRAM/flash content, while verify/status helpers only observe.

Dependencies and integration points: references `struct asd_ha_struct` by pointer without defining it, so it is intended for internal aic94xx compilation units. It aligns with flash BAR/profile fields in `asd_ha->hw_prof.flash` and with SDS parsing in `aic94xx_sds.c`.

Risks: numeric status codes are not `errno` values, so callers must not blindly mix them with negative Linux errors. Flash ID aliases overlap among vendors; method selection must be kept in sync with the implementation. Header structures lack endian annotations for image fields, requiring caller discipline when parsing external files.

Test signals: compile users of all prototypes, flash type detection for supported IDs, sector erase/write/verify loops, and user-facing error propagation for every `FAIL_*` value.
