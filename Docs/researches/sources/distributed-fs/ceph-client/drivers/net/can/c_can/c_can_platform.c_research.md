<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/c_can/c_can_platform.c -->
## sources/distributed-fs/ceph-client/drivers/net/can/c_can/c_can_platform.c

Purpose: this file is the platform/OF wrapper for Bosch C_CAN and D_CAN controllers. It maps platform resources, selects C_CAN versus D_CAN register access, handles TI-specific RAMINIT through direct function registers or syscon regmaps, enables runtime PM, and wires suspend/resume for D_CAN power-down mode.

Important APIs, types, and functions: register accessors include 16-bit aligned, 32-bit aligned, and D_CAN 32-bit paths. RAMINIT helpers include `c_can_hw_raminit_syscon()` and `c_can_hw_raminit()`, protected by `raminit_lock`. Static driver data describes generic C_CAN, generic D_CAN, DRA7 D_CAN, and AM3352/AM4372 D_CAN message object counts and RAMINIT bits. Main lifecycle functions are `c_can_plat_probe()`, `c_can_plat_remove()`, `c_can_suspend()`, and `c_can_resume()`.

Control flow: probe reads match data, gets the clock, IRQ, and MMIO resource, allocates a C_CAN device with the configured object count, chooses register maps and accessors by controller id and resource memory type, configures RAMINIT from `syscon-raminit` when present for TI SoCs, fills base/device/clock/type, enables runtime PM, registers the shared C_CAN netdev, and leaves runtime operation to the core. Suspend detaches a running D_CAN netdev, calls `c_can_power_down()`, and marks the state sleeping; resume calls `c_can_power_up()`, restores error-active state, and reattaches/restarts the queue.

State and persistence: wrapper state is mostly `struct c_can_priv` fields set at probe: MMIO base, clock rate, register map/accessors, type, device pointer, and RAMINIT configuration. Syscon-backed RAMINIT state persists in `priv->raminit_sys` and uses shared register bits across CAN instances.

Dependencies and integration points: it depends on platform devices, OF match data (`bosch,c_can`, `bosch,d_can`, `ti,dra7-d_can`, `ti,am3352-d_can`, `ti,am4372-d_can`), clocks, resource flags, syscon/regmap, runtime PM, and the shared C_CAN core exported APIs.

Risks: `device_get_match_data()` must provide valid driver data; legacy platform-id matching depends on the driver table. TI RAMINIT sequences are sensitive to start/done bit semantics and the DRA7 pulse requirement. Shared syscon access needs locking to avoid cross-instance corruption. Suspend/resume is only meaningful for D_CAN and warns for C_CAN. Clock frequency is assumed stable after probe.

Test signals: probe generic C_CAN/D_CAN and TI variants, validate 16-bit versus 32-bit resource access, test `syscon-raminit` instance ids and timeout logs, run CAN traffic across suspend/resume, check runtime PM balance on open/close, and verify cleanup after registration failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/c_can/c_can_platform.c -->
