# sources/distributed-fs/ceph-client/drivers/media/usb/cx231xx/Makefile

## Purpose
Builds the Conexant cx231xx media driver modules and optional RC, ALSA, and DVB pieces.

## Important APIs, types, and functions
The core `cx231xx` module includes video, I2C, cards, core, AV core, MPEG encoder support, PCB config, and VBI objects. `cx231xx-input.o` is added when RC support is enabled. `cx231xx-alsa-objs` maps to `cx231xx-audio.o`. Object targets add `cx231xx.o`, `cx231xx-alsa.o`, and `cx231xx-dvb.o` under their respective config symbols.

## Control flow and state
No runtime flow. Object selection controls which modules are emitted and whether input support is linked into the base driver.

## Dependencies and integration points
Adds include paths for tuner and DVB frontend headers, matching Kconfig's selected tuner/demod dependencies. Integrates with kbuild module naming and media subsystem build layout.

## Risks and test signals
Risks are object list drift when files are added/renamed, mismatch with Kconfig optional modules, and missing include paths for new frontends. Test signals are successful builds for base-only, RC, ALSA, and DVB combinations, with produced module names `cx231xx`, `cx231xx-alsa`, and `cx231xx-dvb`.
