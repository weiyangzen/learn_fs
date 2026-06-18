# sources/distributed-fs/ceph-client/include/media/tuner.h

## Purpose
Defines tuner-core setup contracts, tuner mode masks, and includes the tuner model ID namespace.

## Important APIs, Types, and Functions
Includes `tuner-types.h`. `enum tuner_mode` maps radio and analog-TV modes to V4L2 tuner-type bits. `struct tuner_setup` contains I2C address, tuner type, allowed mode mask, optional tuner-specific config, and callback for bridge-controlled side effects such as GPIO reset.

## Control Flow
Bridge drivers broadcast `tuner_setup` to tuner subdevices, which accept commands only for compatible address/mode masks. Callbacks let tuner drivers ask bridges to perform component-specific actions.

## State and Persistence Behavior
Setup data is transient command payload; selected tuner mode/type persists in tuner driver state and hardware after configuration.

## Dependencies and Integration Points
Depends on kernel-only V4L2 tuner definitions and `tuner-types.h`. Integrates analog TV/radio bridge drivers, tuner-core, and tuner-simple.

## Risks
Wrong `mode_mask` causes radio-only or TV-only tuners to accept the wrong commands. `config` is untyped and must match the selected tuner. Callback component/cmd values are bridge-specific.

## Test Signals
Radio/TV mode switching, multi-tuner boards, address-specific setup, tuner callback paths, and tuner ID mapping to implementation support.
