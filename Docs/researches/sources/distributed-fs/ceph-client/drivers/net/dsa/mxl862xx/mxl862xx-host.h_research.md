# sources/distributed-fs/ceph-client/drivers/net/dsa/mxl862xx/mxl862xx-host.h

## Purpose
Declares the public host transport interface for the MxL862xx driver.

## Important APIs, Types, and Functions
Prototypes are `mxl862xx_host_init`, `mxl862xx_host_shutdown`, `mxl862xx_api_wrap`, and `mxl862xx_reset`.

## Control Flow and State
No runtime logic. The declared functions initialize/cancel CRC error work, issue firmware API commands with optional readback and quiet error behavior, and perform software reset.

## Dependencies and Integration Points
Includes `mxl862xx.h` for `struct mxl862xx_priv` and flag/work definitions. Used by the main driver to initialize transport state and send all firmware-backed operations.

## Risks and Test Signals
Risks are signature drift with callers and missing shutdown during remove paths. Test signals include build coverage, probe/remove cycles, reset path tests, and API wrapper calls from FDB/VLAN/bridge/stat operations.
