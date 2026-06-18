<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/mtd/mtd-abi.h -->
# sources/distributed-fs/ceph-client/include/uapi/mtd/mtd-abi.h

## Purpose
Defines the primary userspace ABI for Linux Memory Technology Devices: erase, OOB, ECC, OTP, bad-block, lock, read/write, and file-mode ioctl structures and command numbers.

## Important APIs, Types, and Functions
Read coverage: 342 lines and 11879 bytes. Visible type families include struct erase_info_user, struct erase_info_user64, struct mtd_oob_buf, struct mtd_oob_buf64, struct mtd_write_req, struct mtd_read_req_ecc_stats, struct mtd_read_req, struct mtd_info_user, struct region_info_user, struct otp_info, struct nand_oobinfo, struct nand_oobfree, struct nand_ecclayout_user, struct mtd_ecc_stats, enum mtd_file_modes. Important macros/constants include __MTD_ABI_H__, MTD_ABSENT, MTD_RAM, MTD_ROM, MTD_NORFLASH, MTD_NANDFLASH, MTD_DATAFLASH, MTD_UBIVOLUME, MTD_MLCNANDFLASH, MTD_WRITEABLE, MTD_BIT_WRITEABLE, MTD_NO_ERASE, MTD_POWERUP_LOCK, MTD_SLC_ON_MLC_EMULATION, MTD_CAP_ROM, MTD_CAP_RAM, MTD_CAP_NORFLASH, MTD_CAP_NANDFLASH, MTD_CAP_NVRAM, MTD_NANDECC_OFF, MTD_NANDECC_PLACE, MTD_NANDECC_AUTOPLACE, MTD_NANDECC_PLACEONLY, MTD_NANDECC_AUTOPL_USR, MTD_OTP_OFF, MTD_OTP_FACTORY, MTD_OTP_USER, MEMGETINFO, ... (+26 more). Explicit ioctl-style command names include MEMGETINFO, MEMERASE, MEMWRITEOOB, MEMREADOOB, MEMLOCK, MEMUNLOCK, MEMGETREGIONCOUNT, MEMGETREGIONINFO, MEMGETOOBSEL, MEMGETBADBLOCK, MEMSETBADBLOCK, OTPSELECT, OTPGETREGIONCOUNT, OTPGETREGIONINFO, OTPLOCK, ECCGETLAYOUT, ECCGETSTATS, MTDFILEMODE, MEMERASE64, MEMWRITEOOB64, MEMREADOOB64, MEMISLOCKED, MEMWRITE, OTPERASE, MEMREAD.

## Control Flow
Userspace opens an MTD character device, queries geometry with `MEMGETINFO`, optionally queries region/OOB/ECC layout, erases regions, performs data or OOB reads/writes, marks or queries bad blocks, changes lock/OTP state, or selects raw/OOB/place/ECC file modes. Newer flows use 64-bit erase/OOB structures and `MEMREAD`/`MEMWRITE` request structures for mode-aware I/O and ECC statistics.

## State and Persistence Behavior
The header stores no runtime state, but the ioctls mutate persistent flash content, bad-block tables, OTP regions, lock state, and ECC/OOB placement. `mtd_info_user` and related structures snapshot kernel device geometry and capability flags for userspace.

## Dependencies and Integration Points
It depends on ioctl numbering, Linux integer and loff_t types, and legacy NAND OOB layout definitions. It integrates with MTD char devices, NAND/NOR flash drivers, UBI attachment, flash filesystems, and flash-management tools. Direct includes are #include <linux/types.h>.

## Risks and Edge Cases
Compatibility risks include legacy 32-bit offsets versus 64-bit offsets, variable OOB layouts, raw mode bypassing ECC, irreversible OTP locking, bad-block marking, and ABI-preserved deprecated fields. Incorrect bounds checks can erase or write outside intended flash regions.

## Test Signals
Run MTD char-device ioctl tests on nandsim/mtdram and real devices, cover 32-bit compat ioctls, OOB and raw modes, ECC statistics, OTP lock/erase behavior, bad-block operations, and UBI attach after erase/write cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/mtd/mtd-abi.h -->
