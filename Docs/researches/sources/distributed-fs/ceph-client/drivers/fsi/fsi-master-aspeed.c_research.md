<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fsi/fsi-master-aspeed.c -->
# sources/distributed-fs/ceph-client/drivers/fsi/fsi-master-aspeed.c

## Purpose
`fsi-master-aspeed.c` is the AST2600 hardware FSI master driver. It accesses the FSI controller through an OPB bridge, initializes the embedded hub master, exposes FSI master callbacks to the core, and supports optional board-level CFAM reset and Tacoma external-cable muxing.

## Important APIs, types, and functions
`struct fsi_master_aspeed` embeds `struct fsi_master` and stores lock, device, OPB MMIO base, clock, and optional CFAM reset GPIO. Low-level helpers are `__opb_read()`, `__opb_write()`, typed OPB accessors, and `check_errors()`. Master callbacks are `aspeed_master_read()`, `aspeed_master_write()`, `aspeed_master_link_enable()`, `aspeed_master_term()`, and `aspeed_master_break()`. Probe initializes hardware in `aspeed_master_init()`.

## Control flow
Probe applies optional cable mux fixup, allocates state, maps OPB registers, enables the clock, sets optional CFAM reset sysfs, configures OPB interrupt masks, retry counter, controller/FSI base windows, read/write data ordering, selects OPB0, reads `FSI_MVER` for link count, fills `struct fsi_master`, initializes the controller, registers the master, and takes an extra device reference for remove. Read/write callbacks validate ID, encode ID into address bits and link into hub link offset, serialize OPB access under `lock`, perform byte/halfword/fullword transfers, and clear master errors on `-EIO`. Link enable writes `MSENP0` or `MCENP0` and delays for setup.

## State and persistence behavior
Runtime state is MMIO configuration, enabled clock, optional GPIO state, the bus divisor module parameter `bus_div`, and the master object. No persistent storage exists. Hardware initialization programs FSI MMODE, delays, error control, link enable masks, and bridge resets.

## Dependencies and integration points
It depends on platform/OF matching `aspeed,ast2600-fsi-master`, clocks, MMIO, GPIO descriptors, tracepoints, mutexes, and the FSI core master API. Optional board integration uses `fsi-routing` and `fsi-mux` GPIOs plus `cfam-reset`.

## Risks and edge cases
OPB polling has a short timeout and synchronous error handling. The driver currently selects OPB0 for all operations and notes future work for OPB1/DMA. Global `aspeed_fsi_divisor` can be altered by cable fixup unless module parameters override it. Remove does not drop the extra master device reference directly in this file, so lifetime depends on core unregister/release behavior.

## Test signals
Probe with OPB resource/clock, hub version/link count read, FSI scans across reported links, byte/halfword/word transfers, OPB timeout and `STATUS_ERR_ACK` handling, CFAM reset sysfs action, cable mux divisor change, and unregister cleanup validate this driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fsi/fsi-master-aspeed.c -->
