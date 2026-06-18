# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lnbp22.h

## Purpose
`lnbp22.h` defines LNBP22 control bits and the attach API for the LNBP22 SEC helper.

## Important APIs, Types, and Functions
It defines `LNBP22_EN`, `LNBP22_VSEL`, and `LNBP22_LLC`. `lnbp22_attach()` accepts an existing frontend and I2C adapter under `CONFIG_DVB_LNBP22`, with a disabled-driver warning stub otherwise.

## Control Flow
Board drivers call attach after demodulator/frontend creation. The C file installs voltage and high-voltage callbacks and uses a fixed I2C address.

## State and Persistence
The header contains no state. The control bits map to byte 3 of the runtime four-byte config array.

## Dependencies and Integration Points
It depends on DVB frontend types and integrates with satellite frontend SEC setup.

## Risks and Edge Cases
The comment mentions override masks, but the actual attach signature has no override parameters. Callers cannot configure address or default bytes through this header.

## Test Signals
Build both Kconfig paths and verify control bits produce expected voltage/LLC writes in `lnbp22.c`.
