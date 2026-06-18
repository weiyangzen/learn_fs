# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lnbh25.h

## Purpose
`lnbh25.h` defines board configuration and option bits for the ST LNBH25 LNB supply driver.

## Important APIs, Types, and Functions
It defines DATA2 option bits `LNBH25_TEN`, `LNBH25_LPM`, and `LNBH25_EXTM`. `struct lnbh25_config` carries an I2C address and DATA2 configuration byte. `lnbh25_attach()` is declared under `CONFIG_DVB_LNBH25` and stubbed otherwise.

## Control Flow
Board drivers fill `lnbh25_config`, call attach with an existing frontend and I2C adapter, and the C file installs voltage-control SEC callbacks.

## State and Persistence
The config byte is copied into runtime state and rewritten on each voltage change. No persistent state is defined here.

## Dependencies and Integration Points
It depends on Linux I2C and DVB frontend headers. Integration is limited to satellite SEC voltage-control setup.

## Risks and Edge Cases
The I2C address is expected in the board convention used by the C file, which shifts it right by one. Supplying an already 7-bit address would address the wrong chip.

## Test Signals
Build both Kconfig paths, verify address handling on target boards, and check that DATA2 option bits are present in every LNBH25 write.
