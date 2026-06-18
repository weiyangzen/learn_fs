# sources/distributed-fs/ceph-client/drivers/media/usb/au0828/au0828-reg.h

## Purpose
Defines AU0828 bridge register addresses and bit constants used by core, I2C, audio, and analog streaming code.

## Important APIs, types, and functions
Key definitions include GPIO-like registers `REG_000` through `REG_003`, analog sensor control registers `AU0828_SENSORCTRL_100` and `AU0828_SENSORCTRL_VBI_103`, I2C registers from trigger/status/clock/destination/FIFOs/multibyte mode, audio control `AU0828_AUDIOCTRL_50C`, and `REG_600` for bridge power. Bit constants define I2C trigger write/read/hold, status read/write done, no-ack, and busy bits, plus clock divider presets.

## Control flow and state
No executable flow. These constants are used to program persistent hardware state in register writes. Mislabelled or changed values affect GPIO reset, I2C transport, stream setup, and audio mode.

## Dependencies and integration points
Included by `au0828.h` and analog video code. Integrated across `au0828-core.c`, `au0828-cards.c`, `au0828-i2c.c`, and `au0828-video.c`.

## Risks and test signals
Risks are incorrect register addresses, unclear names for still-reverse-engineered registers, and clock-divider values that break tuner/demod communication. Test signals are I2C register polling behavior, successful GPIO reset sequencing, analog stream enable, and I2S audio init.
