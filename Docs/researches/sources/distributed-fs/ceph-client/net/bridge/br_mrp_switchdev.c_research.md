<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_mrp_switchdev.c -->
# sources/distributed-fs/ceph-client/net/bridge/br_mrp_switchdev.c

Purpose: is the switchdev adapter for bridge MRP. It converts bridge MRP instance, role, state, test generation, and port role/state requests into switchdev objects or attributes, and reports whether hardware fully handled the operation, supports software-backup mode, or cannot support the request.

Important APIs, types, and functions:

- Instance object operations: `br_mrp_switchdev_add()` and `br_mrp_switchdev_del()`.
- Ring operations: `br_mrp_switchdev_set_ring_role()`, `br_mrp_switchdev_send_ring_test()`, and `br_mrp_switchdev_set_ring_state()`.
- Interconnect operations: `br_mrp_switchdev_set_in_role()`, `br_mrp_switchdev_send_in_test()`, and `br_mrp_switchdev_set_in_state()`.
- Port attribute operations: `br_mrp_port_switchdev_set_state()` and `br_mrp_port_switchdev_set_role()`.
- `br_mrp_switchdev_port_obj()` is the common add/delete wrapper that maps switchdev return codes to `enum br_mrp_hw_support`.

Core control flow:

- When `CONFIG_NET_SWITCHDEV` is disabled, operations that can fall back to software return `BR_MRP_SW`, while pure state-setting helpers return success. This lets `br_mrp.c` run software protocol logic without requiring hardware support.
- `br_mrp_switchdev_port_obj()` calls `switchdev_port_obj_add()` or `switchdev_port_obj_del()` on the bridge device. Success means hardware handled the object (`BR_MRP_HW`). `-EOPNOTSUPP` means software fallback is allowed (`BR_MRP_SW`). Any other error means no usable support (`BR_MRP_NONE`).
- `br_mrp_switchdev_add()` sends `SWITCHDEV_OBJ_ID_MRP` with primary/secondary port devices, ring ID, and priority. Delete sends the same object ID with null ports and ring ID.
- Ring role and interconnect role setters first try full hardware offload. If full offload is unsupported, they retry with `sw_backup = true`, asking hardware to install the pieces needed while software runs protocol behavior. Success in that retry returns `BR_MRP_SW`.
- Ring and interconnect test generation create switchdev test objects with interval, max-miss, IDs, period, and monitor flags. A zero interval deletes/stops the object.
- Port state and role helpers send switchdev attributes `SWITCHDEV_ATTR_ID_PORT_STP_STATE` and `SWITCHDEV_ATTR_ID_MRP_PORT_ROLE` to the physical port.

State and persistence behavior:

- This file does not store state. It reflects the current `struct br_mrp` and port fields into switchdev driver state and reports support level to callers.
- Hardware state persists in the driver until corresponding delete/disable calls or device teardown. Software state such as `ring_role_offloaded` is stored by callers in `br_mrp.c`.

Dependencies and integration points:

- Depends on switchdev object IDs for MRP, ring role/test/state, interconnect role/test/state, and switchdev attributes for port STP state and MRP port role.
- Called exclusively by `br_mrp.c` during MRP configuration, teardown, and software/hardware fallback decisions.
- Uses `rtnl_dereference()` for MRP port pointers, matching the administrative locking expected by the caller.

Risks and edge cases:

- Return-code mapping defines runtime behavior. Treating non-`EOPNOTSUPP` errors as fallback would hide real hardware programming failures; treating `EOPNOTSUPP` as fatal would disable software MRP unnecessarily.
- The interconnect role fallback path differs from ring role logic: the first helper returns on any support value other than `BR_MRP_NONE`, so review is needed to ensure retry-on-unsupported semantics match the intended switchdev contract.
- Role disable paths use object delete operations and may dereference `i_port`; callers must ensure the port exists when disabling interconnect role.
- Null `extack` in several switchdev calls limits user diagnostics for hardware failures.

Test signals:

- Use switchdev-capable and non-switchdev bridge ports to verify full hardware, software-backup, and unsupported outcomes.
- Mock or instrument switchdev drivers to return success, `-EOPNOTSUPP`, and other errors for each object type.
- Confirm MRP add/delete objects carry correct ring ID, priority, and port devices.
- Verify ring/interconnect test start and stop issue add/delete object operations based on interval.
- Check port STP state and MRP port role attributes are sent when MRP runtime state changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_mrp_switchdev.c -->
