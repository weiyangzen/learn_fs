# sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx_sds.c

Purpose: this file reads and writes shared data structures for adapter configuration. It imports BIOS/OCM metadata, flash manufacturing/user settings, SAS addresses, PHY parameters, and exposes flash programming helpers.

Important APIs/types/functions: exported functions are `asd_read_ocm()`, `asd_read_flash()`, `asd_verify_flash_seg()`, `asd_write_flash_seg()`, `asd_chk_write_status()`, `asd_erase_nv_sector()`, and `asd_check_flash_type()`. Internal structures include OCM directory entries, BIOS CHIM metadata, flash directory entries, manufacturing sectors, CTRL-A phy settings, and linked-list elements. Internal processing functions include `asd_read_ocm_seg()`, `asd_read_ocm_dir()`, `asd_get_bios_chim()`, `asd_hwi_check_ocm_access()`, `asd_flash_getid()`, `asd_find_flash_dir()`, `asd_process_ms()`, `asd_ms_get_phy_params()`, and `asd_process_ctrl_a_user()`.

Control flow and state: probe-time HWI code calls `asd_read_ocm()` and `asd_read_flash()`. OCM access verifies BIOS initialization, optionally initializes a default OCM directory, reads BIOS CHIM data, and records BIOS/UE metadata in `hw_prof`. Flash reading resets and identifies flash, locates the Adaptec flash directory, validates revision, extracts the manufacturing sector, copies adapter SAS address and PCBA serial, applies manufacturing PHY states, then applies CTRL-A per-phy SAS address/link-rate/user flags. Flash write helpers identify the flash command method, erase affected sectors, program byte-by-byte, poll DQ toggle bits, reset, and allow explicit verification.

Persistence behavior: read paths populate `asd_ha->hw_prof` and allocated UE/manufacturing data. Write/erase paths permanently mutate adapter flash sectors. Default paths synthesize configuration when manufacturing or CTRL-A sections are missing but do not persist defaults unless flash write APIs are invoked by higher layers.

Dependencies and integration points: depends on PCI config space, MMIO register helpers, flash BAR from PCI config, OCM accessors, `aic94xx_sds.h` flash constants, manufacturing structure definitions from other aic94xx headers, and HWI probe sequencing.

Risks: flash writes are destructive and hardware-specific; bad method detection, sector math, or timeout handling can corrupt firmware/config. Some checksum failures are logged but not fatal. Linked-list parsing trusts offsets after minimal validation. Default PHY data may mask missing flash content but can change port exposure.

Test signals: probe on boards with initialized and uninitialized OCM, valid/invalid flash directories, missing manufacturing or CTRL-A sections, supported flash IDs for method A/B, flash verify mismatch, erase/write timeout, and SAS address/link-rate propagation into phy descriptors. Hardware-backed tests are required for write paths.
