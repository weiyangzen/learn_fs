# sources/distributed-fs/ceph-client/sound/soc/codecs/tas571x.h

## Purpose
This header provides the register map constants for the TAS571x-family amplifier driver. It covers common control/status/volume/mux registers plus device-specific biquad, cross-biquad, and mixer coefficient register addresses for TAS5707, TAS5717, and TAS5733-style parts.

## APIs, Types, and Functions
The header exports register-address macros such as `TAS571X_CLK_CTRL_REG`, `TAS571X_SDI_REG`, `TAS571X_SYS_CTRL_2_REG`, `TAS571X_SOFT_MUTE_REG`, volume registers, input/PWM mux registers, and many `TAS5707_*`, `TAS5717_*`, and `TAS5733_*` biquad/mixer registers. It also defines key masks and shifts including `TAS571X_SDI_FMT_MASK`, `TAS571X_SYS_CTRL_2_SDN_MASK`, and soft-mute channel shifts.

## Control Flow
There is no runtime flow. The constants are consumed by `tas571x.c` to size registers, define regmap defaults and access tables, create ALSA controls, map serial formats, and route coefficient read/write controls to the right hardware registers.

## State and Persistence
No state is stored in the header. Its address definitions are effectively part of the persistent driver ABI because ALSA control names in `tas571x.c` expose these coefficient blocks as user-programmable mixer controls.

## Dependencies and Integration
The header is local to the codec driver and has no direct includes beyond its guard. It assumes Linux bit-shift conventions and is integrated by `tas571x.c` for all family variants supported by the OF/I2C match tables.

## Risks and Test Signals
Risks include wrong register constants causing coefficient controls or mux defaults to program unintended DSP blocks, and duplicated or family-mismatched register names when adding new TAS57xx devices. Test signals are compile coverage, probe/control enumeration for every supported chip, and coefficient writes verified against datasheet addresses or hardware traces.
