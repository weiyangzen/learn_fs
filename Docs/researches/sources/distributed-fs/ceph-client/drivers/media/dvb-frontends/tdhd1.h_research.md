
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tdhd1.h

## Purpose
`tdhd1.h` provides board-specific support data for the ALPS TDHD1-204A tuner/demodulator combination using the TDA10046 DVB-T demodulator.

## Important APIs, Types, and Functions
It forward-declares `alps_tdhd1_204_request_firmware()` and defines static `alps_tdhd1_204a_config`, a `struct tda1004x_config` with demod address `0x8`, inverted spectrum, 4 MHz crystal, default AGC, 36.17 MHz IF, and board firmware request callback.

## Control Flow
The header has no standalone flow. Including board code uses the static config when calling `tda10046_attach()` and supplies the declared firmware callback elsewhere.

## State and Persistence Behavior
The static config is compile-time board data. No runtime state or persistence is owned by the header.

## Dependencies and Integration Points
It includes `tda1004x.h` and is integrated by board drivers that know how to request TDHD1 firmware.

## Risks and Edge Cases
Because the config is `static` in a header, each including translation unit gets its own copy. The firmware callback is only declared here; missing or mismatched definition causes build/link problems in consumers. Board-specific hard-coded IF/xtal/inversion values must match the ALPS module.

## Test Signals
Compile tests should cover the board file that includes this header and defines the firmware callback. Runtime signals include successful TDA10046 attach/init with 4 MHz xtal, 36.17 MHz IF, inverted spectrum, and firmware request through the board callback.
