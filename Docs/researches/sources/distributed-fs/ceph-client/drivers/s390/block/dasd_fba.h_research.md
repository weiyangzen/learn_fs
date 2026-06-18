# sources/distributed-fs/ceph-client/drivers/s390/block/dasd_fba.h

## Purpose
This header defines the fixed-block architecture DASD payloads used by `dasd_fba.c`: maximum request chaining, Define Extent data, Locate data, and the Read Device Characteristics layout for FBA devices.

## Important APIs, Types, and Functions
`DASD_FBA_MAX_BLOCKS` caps the number of blocks chained in one request. `struct DE_fba_data` is the FBA Define Extent payload with permissions, block size, extent locator, beginning block, and ending block. `struct LO_fba_data` is the Locate payload with operation nibble, auxiliary byte, block count, and block number. `struct dasd_fba_characteristics` maps the device characteristic data returned by the hardware, including mode bits such as data chaining, feature bits such as removable/shared/MAM, block size, blocks per cycle/boundary, base device size, and related controller fields.

## Control Flow
The header has no executable control flow. `dasd_fba.c` fills `DE_fba_data` before each request to define the logical extent and fills `LO_fba_data` before READ/WRITE commands to select the range inside that extent. The characteristics structure is populated by `dasd_generic_read_dev_chars()` during device check and drives later block-size, capacity, and data-chain decisions.

## State and Persistence
The structures describe transient channel-program payloads or cached hardware characteristics. They do not implement persistence. `dasd_fba_characteristics` becomes part of the device's in-memory private state and information ioctl output.

## Dependencies and Integration Points
The header relies on kernel fixed-width integer types provided by includers and is private to the DASD FBA discipline. It is coupled to s390 FBA channel command payload layouts and the generic DASD block/request model used by `dasd_fba.c`.

## Risks and Test Signals
The primary risks are packed-layout drift, incorrect bitfield interpretation, and mismatches between `DASD_FBA_MAX_BLOCKS` and the discipline's channel-program sizing assumptions. Test signals include successful characteristic reads, correct capacity calculation from `blk_bdsa` and `blk_size`, correct behavior on devices with `data_chain` clear or set, and compile/runtime validation that Define Extent and Locate payload sizes match the expected 16-byte and 8-byte CCW counts.
