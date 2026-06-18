<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/jz4780-efuse.c -->
# sources/distributed-fs/ceph-client/drivers/nvmem/jz4780-efuse.c

## Purpose
Registers the Ingenic JZ4780 eFuse block as a read-only NVMEM provider and handles controller read timing through regmap and clock configuration.

## Important APIs, Types, And Functions
`struct jz4780_efuse` stores device, regmap, and clock. `jz4780_efuse_read()` reads in fixed 32-byte chunks by programming address/length/read-enable bits, polling `EFUSTATE_RD_DONE`, bulk-reading data registers, and copying the requested slice. Probe configures regmap, enables the clock with devm cleanup, computes read adjust/strobe fields from bus rate, and registers `jz4780-efuse`.

## Control Flow
Probe maps MMIO, initializes a 32-bit regmap, enables clock, calculates timing constraints, writes read timing fields, and registers a 1024-byte byte-addressed NVMEM device. Reads loop until the caller's byte range is satisfied, aligning each hardware transaction to a 32-byte boundary.

## State And Persistence
State is device, regmap, and clock. Fuse contents are persistent and read-only here.

## Dependencies And Integration Points
Depends on platform/OF matching, regmap MMIO, clock framework, polling helpers, and NVMEM provider core.

## Risks
Timing calculation must fit four-bit fields; unsupported clock rates fail probe. Read timeout returns errors to consumers. The driver reads full chunks for partial requests, so controller side effects must tolerate repeated aligned reads.

## Test Signals
Probe at supported clock rates, verify timing register values, read unaligned ranges spanning chunk boundaries, force timeout paths if possible, and compare exported NVMEM data to factory fuse maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/jz4780-efuse.c -->
