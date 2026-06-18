# Research: sources/distributed-fs/ceph-client/drivers/media/radio/Kconfig

Purpose: defines configuration entries for radio receiver/transmitter drivers in the media subsystem, including USB, PCI, I2C, MFD-backed, TEA575x, and legacy ISA boards.

Important entries in this subset: `RADIO_ADAPTERS` gates all radio adapters. USB entries include `USB_DSBR`, `USB_KEENE`, `USB_MA901`, `USB_MR800`, and `USB_RAREMONO`. ISA support is gated by `V4L_RADIO_ISA_DRIVERS`, with board symbols such as `RADIO_AZTECH`, `RADIO_CADET`, `RADIO_GEMTEK`, `RADIO_RTRACK`, and helper `RADIO_ISA`. `RADIO_MAXIRADIO` depends on PCI/HAS_IOPORT and selects `RADIO_TEA575X`.

Control flow/state: no runtime code; symbols drive which drivers and helper objects are built and whether fixed I/O port configuration prompts are exposed.

Dependencies and integration: depends broadly on `VIDEO_DEV`, `MEDIA_RADIO_SUPPORT`, bus features (`USB`, `PCI`, `I2C`, `ISA`, `HAS_IOPORT`), and helper libraries such as TEA575x or `radio-isa`.

Risks: many legacy ISA drivers can be built for `COMPILE_TEST`, but real hardware needs correct I/O ports and sometimes unsafe probing. Test signals are Kconfig dependency checks, allmodconfig/COMPILE_TEST builds, and symbol-to-Makefile consistency.
