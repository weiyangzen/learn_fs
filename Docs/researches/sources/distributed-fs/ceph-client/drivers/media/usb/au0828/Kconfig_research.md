# sources/distributed-fs/ceph-client/drivers/media/usb/au0828/Kconfig

## Purpose
Defines build-time configuration for the Auvitek AU0828 hybrid analog/digital USB capture driver and its optional analog V4L2 and remote-control support.

## Important APIs, types, and functions
`VIDEO_AU0828` is the main tristate and depends on I2C, INPUT, DVB_CORE, USB, and VIDEO_DEV. It selects media controller support, DVB media-controller glue, bit-banged I2C, TV EEPROM, vb2-vmalloc when video is enabled, and common demod/tuner dependencies when auto-select is enabled. `VIDEO_AU0828_V4L2` gates analog video/VBI support. `VIDEO_AU0828_RC` gates remote-controller support and depends on RC core compatibility.

## Control flow and state
No runtime flow exists. Build-time symbols decide whether `au0828-video.o`, `au0828-vbi.o`, and `au0828-input.o` are linked and whether inline stubs in `au0828.h` are used.

## Dependencies and integration points
Integrates with media Kconfig, media-controller graph support, DVB frontend/tuner auto-selection, V4L2, RC, and I2C infrastructure.

## Risks and test signals
Risks include invalid built-in/module dependency combinations for V4L2 or RC and missing tuner/demod auto-select entries for supported boards. Test signals are successful builds for core-only, V4L2-enabled, RC-enabled, and module combinations, plus correct menu visibility.
