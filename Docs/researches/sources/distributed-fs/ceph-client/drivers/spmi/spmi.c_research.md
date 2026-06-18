# sources/distributed-fs/ceph-client/drivers/spmi/spmi.c

## Purpose
SPMI framework core: defines the `spmi` bus type, controller/device lifetime, client driver registration, OF child enumeration, exported SPMI command helpers, tracing, and probe/remove runtime-PM wrapping.

## Important APIs, Types, and Functions
Exports `spmi_device_add/remove/alloc`, `spmi_controller_alloc/add/remove`, `__spmi_driver_register`, `spmi_find_device_by_of_node`, register helpers (`spmi_register_read/write`, `spmi_ext_register_read/write`, `spmi_ext_register_readl/writel`, `spmi_register_zero_write`) and non-data commands (`spmi_command_reset/sleep/wakeup/shutdown`). The bus callbacks are `spmi_device_match`, `spmi_drv_probe`, `spmi_drv_remove`, `spmi_drv_shutdown`, and `spmi_drv_uevent`.

## Control Flow
`postcore_initcall(spmi_init)` registers `spmi_bus_type` and enables controller registration. A controller driver allocates a `spmi_controller`, sets `cmd/read_cmd/write_cmd`, then calls `spmi_controller_add`. The core adds the controller device and, for OF systems, iterates child nodes with two-cell `reg`, validates `SPMI_USID` and slave ID, allocates `spmi_device`, sets fwnode/USID, and calls `device_add`. Client drivers bind by OF match or by device name prefix. Exported register helpers validate width/address limits, route to controller callbacks, and emit tracepoints.

## State and Persistence
Global state is `is_registered` and `ctrl_ida` for numeric controller IDs. Device/controller allocations embed Linux device objects and release via `spmi_dev_release`/`spmi_ctrl_release`. No on-disk state exists; persistence is through driver model references and OF nodes.

## Dependencies and Integration Points
Integrates with Linux driver core, OF, PM runtime, trace events, IDA, and controller implementations such as Qualcomm PMIC Arbiter. SPMI client drivers include `linux/spmi.h` and use the exported helpers rather than controller-private callbacks.

## Risks
Controller callbacks must be set and controller device type must match or all helpers return `-EINVAL`. OF registration rejects malformed `reg` entries and unsupported address types. Probe enables runtime PM before invoking client probe and unwinds on failure; buggy client remove/probe paths can leave usage-count expectations fragile.

## Test Signals
Check `bus_register` succeeds before controller add, OF child devices appear as `<ctrl>-<usid>`, modalias uevents are generated for OF clients, helpers reject invalid lengths/addresses, tracepoints bracket read/write/cmd calls, and controller/device references release without leaks on removal.
