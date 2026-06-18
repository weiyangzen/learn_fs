# sources/distributed-fs/ceph-client/drivers/gpu/drm/mxsfb/Makefile

## Purpose
This Makefile maps the Kconfig symbols in the `mxsfb` directory to kernel objects.

## Important APIs, Types, And Data
`mxsfb-y` combines `mxsfb_drv.o` and `mxsfb_kms.o`; `obj-$(CONFIG_DRM_MXSFB)` links them as `mxsfb.o`. `imx-lcdif-y` combines `lcdif_drv.o` and `lcdif_kms.o`; `obj-$(CONFIG_DRM_IMX_LCDIF)` links them as `imx-lcdif.o`.

## Control Flow, State, And Integration
There is no runtime control flow. Kbuild uses the variables to compile the platform-driver/probe portions and KMS plane/CRTC portions together for each hardware generation. The module split mirrors the source split between classic LCDIF and LCDIFv3.

## Risks And Test Signals
The main risk is object omission: missing the KMS object would leave unresolved `*_kms_init`, while missing the driver object would omit module registration. Test signals are successful module builds for `CONFIG_DRM_MXSFB=m/y` and `CONFIG_DRM_IMX_LCDIF=m/y`, plus modpost showing the expected module names.
