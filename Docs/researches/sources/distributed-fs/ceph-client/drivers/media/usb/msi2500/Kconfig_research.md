<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/msi2500/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/usb/msi2500/Kconfig

Purpose: Kconfig entry for the Mirics MSi2500/MSi3101 SDR USB driver.

Important APIs/types/functions: `config USB_MSI2500` is a tristate depending on `VIDEO_DEV` and `SPI`. It selects `VIDEOBUF2_VMALLOC` and `MEDIA_TUNER_MSI001`.

Control flow: selecting the symbol builds `msi2500.o`; the SPI dependency is required because the USB device exposes an SPI bridge used to instantiate the `msi001` tuner subdevice.

State and persistence: build-time configuration only.

Dependencies and integration: integrates the SDR USB driver with V4L2, vb2 vmalloc, SPI core, and the MSI001 tuner driver.

Risks: no explicit help text beyond the prompt string, so users get little guidance. The selected tuner driver must remain compatible with the SPI messages emitted by `msi2500.c`.

Test signals: `COMPILE_TEST`/allmodconfig coverage; verify the option is unavailable without SPI; modular build should pull `msi001` support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/msi2500/Kconfig -->
