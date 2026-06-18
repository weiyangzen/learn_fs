# sources/distributed-fs/ceph-client/drivers/net/wan/slic_ds26522.h

## Purpose
`slic_ds26522.h` defines DS26522 register addresses, reset values, clock/framer/LIU bit fields, and small enums used by the DS26522 SPI configuration driver. It is a hardware-description header rather than a logic implementation.

## Important APIs, Types, And Functions
There are no functions. Register ranges cover receive framer, global, transmit framer, LIU, test, and BERT address spaces. Individual address constants include mode, clock, reset, ID, E1 TAF/TNAF, receive/transmit control, and LIU impedance/control registers. Bit/value constants encode E1/T1 selection, framer enable, init done, HDB3/CCS, B8ZS, 1.544/2.048 MHz clocking, reset/normal states, and transmitter enable. Enums define `line_rate`, `tdm_trans_mode`, and `card_support_type`.

## Control Flow
Control flow is supplied by `slic_ds26522.c`; this header drives which addresses are cleared and which values are written during E1 setup. The range constants are used in loops that zero framer, LIU, and BERT registers.

## State And Persistence
The header has no runtime state. Its constants describe hardware state that persists in the DS26522 until reset or reprogramming.

## Dependencies And Integration Points
It is included by `slic_ds26522.c` and depends conceptually on the DS26522 data sheet. The enums suggest broader line-control integration, but in this source set only hard-coded E1 configuration is used.

## Risks
There is no include guard, so repeated inclusion would rely on build structure rather than protection. Several constants and enums are unused by the current C file, which can hide stale or unvalidated register definitions. Naming comments reference an older `drivers/tdm/line_ctrl` path, while the file now lives under `drivers/net/wan`.

## Test Signals
Compile coverage is the basic signal. Hardware tests should confirm constants against the DS26522 data sheet and verify that range endpoints do not accidentally cover reserved or test-only registers during zeroing loops.
