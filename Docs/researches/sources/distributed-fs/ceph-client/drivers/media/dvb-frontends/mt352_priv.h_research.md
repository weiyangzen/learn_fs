# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mt352_priv.h

## Purpose
`mt352_priv.h` defines the private MT352 register map, chip id, byte helpers, and IF-frequency scaling constant used by `mt352.c`.

## Important APIs, Types, And Functions
`ID_MT352` is the expected chip id `0x13`. `msb()` and `lsb()` extract bytes for register programming. `enum mt352_reg_addr` names status, interrupt, SNR, error counter, AGC, TPS, reset, acquisition, tuner, clock, GPIO, ADC, and chip-id registers. `IF_FREQUENCYx6` encodes the default 36.166 MHz IF in 1/6 MHz units for readback frequency calculation.

## Control Flow
There is no control flow. The C file uses these constants for all register access and calculations.

## State And Persistence
The header contains constants only. Register values live in the demodulator hardware.

## Dependencies And Integration Points
It is private to the MT352 driver and pairs with the public `mt352.h` integration header.

## Risks
Incorrect register constants or byte extraction break tuning and status. The IF scaling constant is an approximation embedded in readback logic, so changing it affects reported frequency.

## Test Signals
Hardware attach, init register writes, tuning, get-frontend readback, and stats reads validate this map indirectly.
