# sources/distributed-fs/ceph-client/include/media/i2c/tvaudio.h

## Purpose
Defines I2C addresses and input selector constants for legacy TV audio decoder/control subdevices.

## Important APIs, Types, and Functions
Macros define supported chip addresses such as TDA8425, TDA9840, TDA9874/9875, TDA985x, TEA6300, TEA6420, and PIC16C54, plus input selectors `TVAUDIO_INPUT_TUNER`, `RADIO`, `EXTERN`, and `INTERN`. `tvaudio_addrs()` returns the shifted I2C probe address list terminated by `I2C_CLIENT_END`.

## Control Flow
Bridge drivers use the address list to probe supported audio chips and use input selectors to configure audio routing.

## State and Persistence Behavior
No local state. Probe and selected input state persists in the selected I2C audio chip.

## Dependencies and Integration Points
Integrates legacy analog TV capture drivers with common tvaudio I2C subdevice probing and input routing.

## Risks
Duplicate address macros and shared addresses reflect chip-family overlap; probing or routing the wrong chip can produce silent audio or wrong-source capture.

## Test Signals
Address probing, tuner/radio/external/internal input routing, chip autodetect, and compile coverage.
