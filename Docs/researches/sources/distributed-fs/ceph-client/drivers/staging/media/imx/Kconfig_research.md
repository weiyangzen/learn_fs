# sources/distributed-fs/ceph-client/drivers/staging/media/imx/Kconfig

## Purpose
This Kconfig fragment enables the i.MX5/6 V4L2 media-controller staging drivers.

## Important Option
`VIDEO_IMX_MEDIA` is a tristate depending on `ARCH_MXC || COMPILE_TEST`, `HAS_DMA`, `VIDEO_DEV`, and `IMX_IPUV3_CORE`. It selects media controller support, V4L2 fwnode, V4L2 mem2mem, vb2 DMA-contig, and the V4L2 subdev API.

## Control Flow and State
There is no runtime flow. The option controls whether the i.MX media common, i.MX6 media graph, CSI, MIPI CSI2, VDIC, and IC subdevice objects are built.

## Dependencies and Integration Points
The option integrates with the i.MX IPUv3 core, Linux media controller, V4L2 subdevice, fwnode, mem2mem, and DMA-contiguous buffer frameworks.

## Risks and Test Signals
Risks are missing IPUv3 symbols, compile-test-only coverage hiding runtime DT issues, and broad object inclusion from a single option. Test signals include `ARCH_MXC` builds, `COMPILE_TEST` builds, module load on i.MX5/6, and media graph enumeration.
