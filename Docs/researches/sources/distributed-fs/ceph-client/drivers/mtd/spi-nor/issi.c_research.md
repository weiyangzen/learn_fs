# sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/issi.c

## Purpose

`issi.c` registers ISSI and PMC SPI NOR parts and provides fixups for address-width and erase-opcode quirks.

## Important APIs, types, and functions

`is25lp256_post_bfpt_fixups()` corrects BFPT data that advertises 3-byte-only addressing despite 4-byte opcode support by setting `params->addr_nbytes = 4`. `pm25lv_nor_late_init()` changes 4K erase opcodes to `SPINOR_OP_BE_4K_PMC` for PM25LV devices. `issi_nor_default_init()` sets the manufacturer default quad-enable method to `spi_nor_sr1_bit6_quad_enable()`.

The table covers PM25LV, IS25CD, PM25LQ, IS25LQ/LP/WP devices with IDs, sizes, 4K sector hints, dual/quad read hints, quad page program support, and 4-byte opcode fixup flags.

## Control flow

During probe, matching entries feed common parameter setup. Manufacturer default init sets quad enable early. BFPT parsing may invoke the IS25LP256 fixup. Late init may rewrite PM25LV erase opcodes after the erase map exists. Setup then selects read/program/erase operations from the corrected parameters.

## State and persistence behavior

No local mutable state exists. The fixups influence runtime parameter state and may cause status-register writes for quad enable. PM25LV erase opcode correction affects persistent erase behavior on those parts.

## Dependencies and integration points

The file depends on SFDP BFPT macros, core erase-map structures, quad-enable helpers, and the generic fixup hook sequence.

## Risks

Address-width correction is critical for 256 Mbit parts; if wrong, accesses above 16 MiB fail or wrap. The PM25LV 4K opcode quirk must only apply to PM25LV entries. Manufacturer-wide quad-enable defaults could be wrong for a future ISSI part unless overridden by SFDP or part fixups.

## Test signals

Test PM25LV 4K erase, IS25LP256/IS25WP256 reads above 16 MiB, quad-read enable on LP/WP devices, and compare debugfs erase command lists before and after late init.
