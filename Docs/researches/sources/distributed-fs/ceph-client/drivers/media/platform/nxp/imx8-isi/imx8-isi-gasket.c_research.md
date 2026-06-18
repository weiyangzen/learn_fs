# sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx8-isi/imx8-isi-gasket.c

## Purpose
`imx8-isi-gasket.c` programs SoC-specific gasket or camera-mux registers between upstream camera interfaces and the ISI crossbar. It converts V4L2 frame descriptors and frame formats into syscon regmap writes for i.MX8MN/i.MX8MP-style gaskets and i.MX93 camera mux hardware.

## Important APIs, Types, and Functions
The file exports `mxc_imx8_gasket_ops` and `mxc_imx93_gasket_ops`. i.MX8 helpers `mxc_imx8_gasket_enable()` and `mxc_imx8_gasket_disable()` write per-port size and control registers under `GASKET_BASE(port)`, including CSI-2 data type and dual-component enable for `MIPI_CSI2_DT_YUV422_8B`. i.MX93 helpers `mxc_imx93_gasket_enable()` and `mxc_imx93_gasket_disable()` program `DISP_MIX_CAMERA_MUX`, including CSI-2 data type, gasket enable, and source type selection for parallel inputs.

## Control Flow
The crossbar calls the selected `mxc_gasket_ops.enable()` before enabling upstream streams for an input, passing the upstream frame descriptor, sink format, and port. The gasket function writes size/type fields and enables the block. When the last user of an input disables streams, crossbar calls the matching disable function, which clears the control register.

## State and Persistence
State is hardware register state in the syscon regmap referenced by `isi->gasket`. No software state is stored in this file. The registers are only meaningful while a stream is active and are cleared on disable.

## Dependencies and Integration Points
The file depends on `linux/bitfield.h`, `linux/regmap.h`, media CSI-2 data type definitions, and the `mxc_gasket_ops` contract from `imx8-isi-core.h`. Platform data in `imx8-isi-core.c` selects these ops for SoCs that require gasket programming.

## Risks and Edge Cases
The code assumes the frame descriptor has already been validated by the crossbar and uses entry 0 directly. YUV422 8-bit dual-component handling is hard-coded for the i.MX8 gasket path. The i.MX93 path ignores the `port` argument because it uses a single camera mux register, which matches current platform data but would not scale without changes. Incorrect `fsl,blk-ctrl` syscon wiring prevents gasket setup entirely.

## Test Signals
Tests should verify regmap writes for CSI-2 RAW and YUV422 data types, dual-component enable for YUV422 on i.MX8MN/i.MX8MP-style platforms, parallel-source source-type selection on i.MX93, gasket clear on stream disable, and failure-free interaction with crossbar stream enable/disable ordering.
