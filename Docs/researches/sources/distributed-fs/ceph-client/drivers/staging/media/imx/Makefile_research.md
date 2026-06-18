# sources/distributed-fs/ceph-client/drivers/staging/media/imx/Makefile

## Purpose
This Makefile composes the i.MX media driver objects selected by `CONFIG_VIDEO_IMX_MEDIA`.

## Important Build Rules
`imx-media-common-objs` groups common capture/device/of/utils code. `imx6-media-objs` groups the core i.MX6 media device, internal subdevs, IC common/PRP/PRPENCVF, VDIC, and CSC/scaler. `imx6-media-csi-objs` groups CSI and frame interval monitor support. The option also builds `imx6-mipi-csi2.o` directly.

## Control Flow and State
No runtime state exists in this file. It determines link composition and therefore which internal symbols are available inside the i.MX media staging module set.

## Dependencies and Integration Points
It depends on Kbuild object aggregation and the `VIDEO_IMX_MEDIA` Kconfig symbol. The IC files in this subset are linked into `imx6-media.o`.

## Risks and Test Signals
Risks include stale object names, accidental omission of an object needed by internal references, and all-or-nothing build inclusion. Test signals are clean built-in/module builds and successful symbol resolution for IC, VDIC, CSI, MIPI CSI2, and capture helpers.
