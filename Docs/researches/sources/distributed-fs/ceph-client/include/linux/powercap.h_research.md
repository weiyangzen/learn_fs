# sources/distributed-fs/ceph-client/include/linux/powercap.h

Purpose: declares the sysfs power-capping class interface for control types, hierarchical power zones, and power-limit constraints.

Important APIs and types: `struct powercap_control_type_ops` enables/disables and releases a control type. `struct powercap_control_type` stores class device, child IDR, zone count, ops, mutex, allocation ownership, and global list node. `struct powercap_zone_ops` exposes energy, power, enable, and release callbacks. `struct powercap_zone` stores ID/name, control-type instance, ops, device, child/parent IDRs, private data, sysfs attribute groups, allocation ownership, and constraints. `struct powercap_zone_constraint_ops` defines mandatory limit/window/name callbacks plus min/max bounds. Registration APIs add/remove control types and zones, and helpers get/set zone private data.

Control flow: a driver registers a named control type, then registers top-level and child zones with zone ops and constraint ops. The framework creates devices and sysfs attributes, routes reads/writes to callbacks, and requires child zones be removed before parents and all zones before unregistering a control type.

State and persistence: runtime state includes class devices, IDR trees, mutex-protected hierarchy, attribute arrays, private data pointers, constraints, and ownership flags controlling release behavior. Power limits may persist in hardware depending on the driver; the framework state is live kernel state.

Dependencies and integration points: integrates with device model sysfs, IDR allocation, mutex/list management, RAPL or other power-control drivers, and user-space powercap ABI.

Risks and test signals: risks include missing mandatory callbacks, unregistering parents before children, freeing client-owned memory without release, hierarchy IDR leaks, units confusion between uJ/uW/us, and insufficient callback locking. Test sysfs reads/writes for energy/power/constraints, enable toggles, nested zones, unregister ordering, release callbacks, private data helpers, and error paths for duplicate control-type names.
