# sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx_seq.h

Purpose: this header defines the firmware-file ABI and exported sequencer lifecycle functions for aic94xx.

Important APIs/types/functions: constants include `CSEQ_NUM_VECS`, `LSEQ_NUM_VECS`, `SAS_RAZOR_SEQUENCER_FW_FILE`, and required firmware major version. `struct sequencer_file_header` describes the little-endian firmware header: checksum, major/minor, printable version, CSEQ/LSEQ vector tables, CSEQ/LSEQ code blobs, mode-2 task address, and idle-loop addresses. Kernel prototypes expose `asd_init_seqs()`, `asd_start_seqs()`, `asd_release_firmware()`, and `asd_update_port_links()`.

Control flow and state: no flow is implemented here. `aic94xx_seq.c` reads this header layout directly from `request_firmware()` data, validates sizes and version, and uses the parsed offsets to populate static firmware globals before downloading microcode.

Persistence behavior: none directly. The header defines how firmware bytes become persistent in hardware instruction RAM during driver initialization and how DDB 0 link-state updates are exposed to other files.

Dependencies and integration points: requires `struct asd_ha_struct` and `struct asd_phy` declarations from the internal aic94xx environment when `__KERNEL__` is defined. The firmware file name is also declared with `MODULE_FIRMWARE()` in `aic94xx_seq.c`.

Risks: all quantities are noted as little-endian; any parser changes must retain conversions. Table-size constants must match the firmware image. The major version constant is a hard compatibility gate.

Test signals: firmware header parsing, checksum validation, vector count validation, major-version mismatch handling, and callers compiling against the lifecycle prototypes.
