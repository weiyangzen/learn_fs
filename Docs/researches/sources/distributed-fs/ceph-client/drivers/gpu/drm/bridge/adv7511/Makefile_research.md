<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/adv7511/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/adv7511/Makefile

## Purpose

The ADV7511 Makefile defines the composite bridge module and conditionally adds audio and CEC implementation objects.

## Important APIs, Types, And Targets

- `adv7511-y := adv7511_drv.o adv7533.o`: always includes the main driver and ADV7533/7535 DSI companion.
- `adv7511-$(CONFIG_DRM_I2C_ADV7511_AUDIO) += adv7511_audio.o`.
- `adv7511-$(CONFIG_DRM_I2C_ADV7511_CEC) += adv7511_cec.o`.
- `obj-$(CONFIG_DRM_I2C_ADV7511) += adv7511.o`.

## Control Flow

No runtime flow exists here. Kbuild composes `adv7511.o` from the selected objects.

## State And Persistence Behavior

Only build artifacts are affected.

## Dependencies And Integration Points

The object list matches optional function prototypes/stubs in `adv7511.h` and Kconfig symbols in the same directory.

## Risks And Edge Cases

Optional object omission must match stub definitions; otherwise bridge funcs would reference missing symbols. `adv7533.o` is always built with the main driver because chip variants share the module.

## Test Signals

Compile with audio/CEC on and off, run modpost, and load the module on ADV7511 and ADV7533/7535 systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/adv7511/Makefile -->
