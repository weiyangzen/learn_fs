# sources/distributed-fs/ceph-client/include/linux/mtd/spinand.h

## Purpose

Defines the SPI NAND core contract, including spi-mem operation templates, status/config bits, manufacturer/device tables, on-die ECC, OTP support, bus-interface selection, operation variants, and `struct spinand_device`.

## Important APIs, Types, and Functions

Key exports are `SPINAND_*_OP` spi-mem templates, feature/status macros, ID/read-ID types, manufacturer tables, `spinand_op_variants`, `spinand_ecc_info`, OTP operation structs, `spinand_info` macros, `spinand_mem_ops`, `spinand_device`, conversion helpers, match/init, register/config/write-enable/select/wait/read/write helpers, OTP helpers, and MTD OTP setup.

Source-visible symbols include structs: `struct spinand_op;`, `struct spinand_device;`, `struct spinand_id`, `struct spinand_devid`, `struct spinand_manufacturer_ops`, `struct spinand_manufacturer`, `struct spinand_op_variants`, `struct spinand_ecc_info`, `struct spinand_ondie_ecc_conf`, `struct spinand_otp_layout`, `struct spinand_fact_otp_ops`, `struct otp_info *buf, size_t *retlen);`; enums: `enum spinand_readid_method`, `enum spinand_bus_interface`, `enum spinand_bus_interface iface);`, `enum spinand_bus_interface bus_iface;`, `enum spinand_readid_method rdid_method);`; typedefs: none visible in this header; prototypes: `return container_of(mtd_to_nanddev(mtd), struct spinand_device, base);`, `return nanddev_to_mtd(&spinand->base);`, `return container_of(nand, struct spinand_device, base);`, `int spinand_upd_cfg(struct spinand_device *spinand, u8 mask, u8 val);`, `int spinand_read_reg_op(struct spinand_device *spinand, u8 reg, u8 *val);`, `int spinand_write_reg_op(struct spinand_device *spinand, u8 reg, u8 val);`, `int spinand_write_enable_op(struct spinand_device *spinand);`, `int spinand_select_target(struct spinand_device *spinand, unsigned int target);`, `size_t spinand_otp_page_size(struct spinand_device *spinand);`, `size_t spinand_fact_otp_size(struct spinand_device *spinand);`, `size_t spinand_user_otp_size(struct spinand_device *spinand);`, `int spinand_set_mtd_otp_ops(struct spinand_device *spinand);`; representative macros: `__LINUX_MTD_SPINAND_H`, `SPINAND_RESET_1S_0_0_OP`, `SPINAND_WR_EN_1S_0_0_OP`, `SPINAND_WR_DIS_1S_0_0_OP`, `SPINAND_READID_1S_1S_1S_OP`, `SPINAND_SET_FEATURE_1S_1S_1S_OP`, `SPINAND_GET_FEATURE_1S_1S_1S_OP`, `SPINAND_BLK_ERASE_1S_1S_0_OP`, `SPINAND_PAGE_READ_1S_1S_0_OP`, `SPINAND_PAGE_READ_FROM_CACHE_1S_1S_1S_OP`, `SPINAND_PAGE_READ_FROM_CACHE_FAST_1S_1S_1S_OP`, `SPINAND_PAGE_READ_FROM_CACHE_3A_1S_1S_1S_OP`, `SPINAND_PAGE_READ_FROM_CACHE_FAST_3A_1S_1S_1S_OP`, `SPINAND_PAGE_READ_FROM_CACHE_1S_1D_1D_OP`, `SPINAND_PAGE_READ_FROM_CACHE_1S_1S_2S_OP`, `SPINAND_PAGE_READ_FROM_CACHE_3A_1S_1S_2S_OP`.

## Control Flow

The SPI NAND core matches a read ID against manufacturer tables, selects the best read/write/update cache operation variants supported by the SPI memory controller, issues page-read/program-exec/block-erase sequences, polls status, applies on-die ECC status translation, and delegates generic NAND page requests through `nand_device`.

## State and Persistence Behavior

Runtime state includes embedded generic NAND device, SPI memory handle, mutex, read ID, flags, SSDR/ODTR operation templates, current bus interface, dirmaps, current target, ECC info, per-die config cache, data/OOB/scratch DMA-safe buffers, manufacturer/private data, chip configuration hooks, continuous-read capability, OTP descriptors, and read-retry hooks.

## Dependencies and Integration Points

It depends on MTD core, generic NAND core, SPI and SPI memory APIs, vendor manufacturer drivers, and optional on-die ECC/OTP implementations.

Direct includes observed in the source are: `#include <linux/mutex.h>`, `#include <linux/bitops.h>`, `#include <linux/device.h>`, `#include <linux/mtd/mtd.h>`, `#include <linux/mtd/nand.h>`, `#include <linux/spi/spi.h>`, `#include <linux/spi/spi-mem.h>`.

## Risks and Edge Cases

Operation variant selection must respect controller bus-width/DTR support. Config cache must stay coherent per die. Status ECC translation and raw-access flags affect MTD error semantics and user-visible raw/OOB reads.

## Test Signals

Manufacturer ID matching, read-ID method variants, SSDR/ODTR operation selection, config register update, target selection, wait timeouts, ECC status mapping, continuous read enable/disable, OTP read/write/lock, and page read/write across OOB modes.

Source read signal: 905 lines, 30951 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
