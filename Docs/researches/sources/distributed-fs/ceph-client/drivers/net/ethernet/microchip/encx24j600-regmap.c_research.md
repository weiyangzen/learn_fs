# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/encx24j600-regmap.c

## Purpose

`encx24j600-regmap.c` provides regmap bus glue for Microchip ENCX24J600-family SPI Ethernet devices. It translates Linux regmap reads/writes/update-bits calls into banked SFR commands, unbanked commands, single-byte SPI commands, and indirect PHY MII accesses.

## Important APIs, Types, And Functions

The exported GPL symbols are `regmap_encx24j600_spi_write`, `regmap_encx24j600_spi_read`, and `devm_regmap_init_encx24j600`. They operate on `struct encx24j600_context`, supplied by `encx24j600_hw.h`, which contains the SPI device, bank cache, mutex, and regmap pointers.

Core helpers include `encx24j600_switch_bank`, `encx24j600_cmdn`, SFR read/write/update functions, `regmap_encx24j600_reg_update_bits`, generic regmap bus callbacks, register readable/writeable/volatile/precious policies, and PHY regmap read/write callbacks. `regcfg` describes the main 8-bit-address/16-bit-value device regmap; `phycfg` describes indirect PHY registers.

## Control Flow

Initialization creates the main regmap and PHY regmap with custom buses. Reads/writes route by register number: direct SPI commands for command-like registers, banked SFR access with cached bank switching for low registers, translated short commands for selected pointer registers, and rejection for packet data stream registers in the SFR path. Update-bits uses hardware bit-field set/clear commands where valid. PHY reads/writes program `MIREGADR`, issue `MICMD` or `MIWR`, and poll `MISTAT.BUSY`.

## State And Persistence

State is limited to `ctx->bank`, the mutex, and devm-managed regmaps. Hardware registers persist in the device; regmap caches nonvolatile values with maple cache while volatile and precious policies prevent unsafe caching or side-effect reads.

## Dependencies And Integration Points

The file depends on Linux SPI, regmap, mutex/delay APIs, and `encx24j600_hw.h`. Its exported symbols are linked with the main ENCX24J600 driver by the local Makefile.

## Risks And Test Signals

Register classification and bank-cache correctness are the main risks. PHY polling has no explicit timeout if `MISTAT.BUSY` remains set. Data stream registers are intentionally rejected from generic SFR regmap access and must be accessed through appropriate SPI paths. Test banked/unbanked reads, update-bits, invalid register rejection, regcache behavior, PHY read/write, SPI error propagation, and module/built-in linkage.
