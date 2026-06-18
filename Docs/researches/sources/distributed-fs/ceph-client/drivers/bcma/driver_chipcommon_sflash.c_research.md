# sources/distributed-fs/ceph-client/drivers/bcma/driver_chipcommon_sflash.c

Purpose: this file detects and describes ChipCommon-attached serial flash devices and prepares a BCMA serial flash platform device.

Important APIs, types, and functions: it defines static resource `bcma_sflash_resource`, global platform device `bcma_sflash_dev`, flash descriptor type `struct bcma_sflash_tbl_e`, lookup tables for ST/M25P, SST, and Atmel flashes, command helper `bcma_sflash_cmd`, and init function `bcma_sflash_init`.

Control flow: `bcma_sflash_init` switches on flash capability type. For ST serial flash it issues deep-powerdown/release-ID commands, reads manufacturer/device IDs from `FLASHDATA`, and looks up SST or ST tables. It rejects unsupported ID `0x13` and unknown IDs. For Atmel serial flash it reads status ID bits and looks up the Atmel table. On success it fills `cc->sflash` block size, block count, total size, and present flag; logs the detected flash; sets the static resource end based on size; and stores platform data for later device registration.

State and persistence: state persists in `cc->sflash` and static platform-device/resource fields. The command helper changes ChipCommon flash control/address registers.

Dependencies and integration points: it uses BCMA ChipCommon register accessors, platform device infrastructure, static flash geometry tables, and later MTD/platform code that consumes `bcma_sflash_dev`.

Risks: unsupported flash IDs return `-ENOTSUPP`, so newer flash parts need table updates. `bcma_sflash_cmd` only logs timeout and returns void, so callers may proceed after a command timeout with invalid data. Static global platform device state limits multi-instance support. Resource end is computed from start plus size and should be checked against resource conventions.

Test signals: boot logs should identify flash name, size, block size, and block count. MTD registration and partition probing validate that the prepared platform data is consumed correctly.
