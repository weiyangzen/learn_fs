# sources/distributed-fs/ceph-client/drivers/media/pci/saa7164/Kconfig

Purpose: declares the `VIDEO_SAA7164` driver option for NXP SAA7164 PCIe bridge TV cards.

Important APIs, types, and functions: `VIDEO_SAA7164` is a tristate symbol. It depends on `DVB_CORE`, `VIDEO_DEV`, `PCI`, and `I2C`; selects `I2C_ALGOBIT`, `FW_LOADER`, `VIDEO_TUNER`, `VIDEO_TVEEPROM`, and optional tuner/demod frontends (`DVB_TDA10048`, `DVB_S5H1411`, `MEDIA_TUNER_TDA18271`) under `MEDIA_SUBDRV_AUTOSELECT`.

Control flow: build configuration controls whether the monolithic `saa7164` module/built-in is compiled. Runtime firmware loading and board support are in the C files.

State and persistence: Kconfig state persists in `.config`; no runtime state.

Dependencies and integration points: couples the PCI bridge driver to DVB, V4L2, I2C, firmware loader, tveeprom, and frontend/tuner drivers used by supported Hauppauge boards.

Risks: missing firmware loader or frontend selections can produce a driver that builds but cannot initialize real hardware completely. Optional autoselect only helps when enabled; custom minimal configs need manual frontend coverage.

Test signals: `make olddefconfig` and module build with `CONFIG_VIDEO_SAA7164=m`; verify expected helper modules and firmware loader support are present.
