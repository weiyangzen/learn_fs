# sources/distributed-fs/ceph-client/drivers/powercap/powercap_sys.c

Purpose: generic Linux power capping sysfs class. It lets drivers register control types and nested zones with common attributes for enable state, energy/power telemetry, and power-limit constraints.

Important APIs/types/functions: exported `powercap_register_control_type()`, `powercap_unregister_control_type()`, `powercap_register_zone()`, and `powercap_unregister_zone()`. Internal helpers seed global `constraint_N_*` device attributes, create constraints, validate control types, manage device release, and implement sysfs show/store callbacks.

Control flow: `powercap_init()` seeds one global set of constraint attribute objects and registers class `powercap`. Drivers first register a control type device, then register zones under either the control type or another zone. Zone registration validates callbacks, allocates or resets the zone, assigns an ID from the parent idr, duplicates the name, allocates constraints and attribute arrays, attaches attributes based on supplied ops, registers the device, and increments `nr_zones`. Unregistration decrements `nr_zones` and unregisters the device; device release removes IDs, destroys child idrs, frees allocations, and calls driver release hooks.

State and persistence: `powercap_cntrl_list` is protected by `powercap_cntrl_list_lock`; each control type has its own lock and idr. Constraint attribute name strings are global and allocated once for `MAX_CONSTRAINTS_PER_ZONE`, while each zone stores pointers to the relevant attributes. Device lifetime uses kernel device references and release callbacks.

Dependencies/integration: used by RAPL and other powercap providers. The sysfs ABI includes `enabled`, zone `name`, `energy_uj`, `power_uw`, max range files, and `constraint_<id>_{power_limit_uw,time_window_us,name,...}` depending on callbacks.

Risks: unregistering a control type with live zones fails; global constraint attributes must outlive all zones; sysfs attribute names are parsed with `sscanf`; a driver-supplied embedded zone requires a release callback; `enabled_show()` treats callback failures as disabled; energy reset only accepts zero and silently ignores nonzero input.

Test signals: module init class creation, control type registration/unregistration with and without zones, nested zone registration, sysfs permission modes, constraint count bounds, callback failure propagation, device lifetime under open sysfs references, and invalid registration parameters.
