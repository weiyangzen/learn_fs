# sources/distributed-fs/ceph-client/drivers/staging/media/Kconfig

## Purpose
Defines top-level staging media driver configuration. `STAGING_MEDIA` gates non-production media drivers, and `STAGING_MEDIA_DEPRECATED` separately gates deprecated staging media drivers.

## Important Entries and Integration
The file depends on `MEDIA_SUPPORT` before sourcing child Kconfigs. It currently sources atomisp, av7110, imx, ipu3, ipu7, max96712, meson/vdec, sunxi, and tegra-video in alphabetical order, plus deprecated atmel under `STAGING_MEDIA_DEPRECATED`.

## Risks and Test Signals
The help text warns APIs may not match normal V4L/DVB/RC expectations. Test signals are Kconfig visibility with `MEDIA_SUPPORT`, correct gating of deprecated drivers, and build menu reachability for atomisp.
