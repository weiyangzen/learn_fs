# sources/distributed-fs/ceph-client/drivers/gpu/ipu-v3/ipu-csi.c

## Purpose
Configures IPUv3 Camera Sensor Interface blocks. It translates V4L2 media-bus formats and signal configuration into CSI register programming, sets active capture windows, downsizing, MIPI datatypes, frame skipping, and data destinations, and exposes get/put lifetime APIs for CSI instances.

## Important APIs, Types, and Functions
`struct ipu_csi` stores ID, module bit, IPU pointer, clock, MMIO base, lock, and use count. `struct ipu_csi_bus_config` captures data width, clock mode, polarity, protocol, data format, and MIPI datatype details. Exported APIs include `ipu_csi_init_interface()`, `ipu_csi_set_window()`, `ipu_csi_set_downsize()`, `ipu_csi_set_mipi_datatype()`, `ipu_csi_set_skip_smfc()`, `ipu_csi_set_dest()`, enable/disable, get/put, init/exit, and dump. Helpers convert media-bus codes and fill config from `v4l2_mbus_config` plus `v4l2_mbus_framefmt`.

## Control Flow
A client acquires a CSI with `ipu_csi_get()`, initializes the interface from media-bus config/frame format, programs optional window/downsize/MIPI datatype/skip settings, selects destination (`IC`, `IDMAC`, etc.), and enables the module. `ipu_csi_init_interface()` validates width/height and input format, calculates divider/protocol/data format fields, writes sensor config and frame size registers, and configures CCIR code registers for BT.656/BT.1120-like modes.

## State and Persistence
Per-CSI runtime state includes MMIO registers, use count protected by a spinlock, and the parent IPU module bit. Register state persists across client operations until reconfigured or reset. There is no filesystem persistence.

## Dependencies and Integration Points
Depends on V4L2 media-bus constants, videodev2 field/color definitions, clk APIs, and `ipu_module_enable()/disable()` in `ipu-common.c`. It integrates with SMFC, IC, IDMAC, and MIPI CSI2 routing via destination and datatype fields plus source muxing in common code.

## Risks
Media-bus conversion is dense and rejects unsupported combinations with `-EINVAL`; adding formats requires careful data-width/protocol mapping. Incorrect signal polarity or CCIR code generation can produce silent capture failures. Use-count balancing is required to avoid sharing conflicts. Register updates are not all globally serialized beyond local spinlock-protected lifetime state, so clients must avoid concurrent reconfiguration of an active CSI.

## Test Signals
Exercise supported media-bus codes, parallel and MIPI CSI2 modes, interlaced and progressive field handling, destination switching, skip/downsize controls, and invalid configuration rejection. Hardware signals include frame IRQs, correct active window size, and `ipu_csi_dump()` register values matching sensor timing.
