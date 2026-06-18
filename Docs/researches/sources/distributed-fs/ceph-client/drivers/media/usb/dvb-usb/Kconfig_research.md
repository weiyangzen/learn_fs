# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/Kconfig

Purpose: Kconfig menu for the legacy `dvb-usb` framework and its USB DVB bridge drivers. It defines the common `DVB_USB` module, global debug option, and per-device options such as A800, AF9005, CXUSB, DiBcom variants, DW2102, Technisat, and others.

Important APIs/types/functions: Kconfig symbols include `DVB_USB`, `DVB_USB_DEBUG`, `DVB_USB_A800`, `DVB_USB_DIB3000MC`, `DVB_USB_CXUSB`, `DVB_USB_CXUSB_ANALOG`, and many device-specific tristates. Dependencies require DVB core, USB, I2C, and RC core for the base framework. `select` clauses pull in Cypress firmware support, demodulators, tuners, videobuf2, and analog helper drivers where automatic subdevice selection is enabled.

Control flow: enabling `DVB_USB` makes the legacy framework object available and reveals the `if DVB_USB` device submenu. Selecting a device driver causes the Makefile to build its composite object and, when `MEDIA_SUBDRV_AUTOSELECT` is enabled, selects likely frontend/tuner dependencies.

State and persistence: no runtime state; this file controls build-time availability, module composition, and dependency closure.

Dependencies and integration: integrated with the sibling Makefile and the wider media Kconfig hierarchy. It bridges user configuration with demod/tuner modules and optional analog/RC support.

Risks: `select` can force dependencies in ways that may surprise minimal configs. Some help text references external wiki information and old device names, so hardware support claims may drift. Built-in/module combinations are constrained in places such as analog support and DIB3000MC helper behavior.

Test signals: `oldconfig`, `allmodconfig`, and `randconfig` builds; each device symbol producing the expected module object; configs with and without `MEDIA_SUBDRV_AUTOSELECT`; base `DVB_USB_DEBUG`; analog CXUSB dependency combinations.
