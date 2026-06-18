# sources/distributed-fs/ceph-client/drivers/media/usb/as102/Kconfig

## Purpose
Defines the kernel configuration entry for the Abilis AS102 USB DVB receiver driver.

## Important APIs, types, and functions
The single symbol is `DVB_AS102`, a tristate option named "Abilis AS102 DVB receiver". It depends on `DVB_CORE`, `USB`, `I2C`, and `INPUT`, and selects `FW_LOADER` because the driver can request and upload firmware blobs during registration.

## Control flow and state
This file does not contain runtime code. Its state effect is build-time selection: enabling the symbol includes the AS102 module and ensures firmware loader support is available. If built as module, the object is produced by the local Makefile as `dvb-as102`.

## Dependencies and integration points
Integrates with the media USB Kconfig tree and the DVB build system. The selected firmware loader is required by `as102_fw.c`, while DVB/USB/I2C/INPUT dependencies match the driver's DVB adapter, USB transport, frontend attachment, and input-related device support requirements.

## Risks and test signals
The main risk is configuration drift: missing a dependency can produce unresolved symbols, while an unnecessary hard dependency can hide the driver from valid configurations. Test signals are Kconfig visibility under media USB DVB options, successful `=m` and `=y` builds, and automatic inclusion of firmware loading support.
