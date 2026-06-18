# sources/distributed-fs/ceph-client/include/net/bond_options.h

## Purpose
This header defines the bonding driver's option metadata and parsing interface. It enumerates all supported bond options, option/value flags, the generic value carrier used by sysfs/netlink/module parameter paths, and helper initializers used before setting or parsing options.

## Important APIs, Types, And Constants
- `BOND_OPT_MAX_NAMELEN`, `BOND_OPT_VALID()`, and `BOND_MODE_ALL_EX()` support option table validation and mode masks.
- `BOND_OPTFLAG_NOSLAVES`, `BOND_OPTFLAG_IFDOWN`, and `BOND_OPTFLAG_RAWVAL` describe setter preconditions and raw parsing behavior.
- `BOND_VALFLAG_DEFAULT`, `MIN`, and `MAX` mark special values in option value tables.
- `enum BOND_OPT_*` assigns stable IDs for mode, transmit hash policy, ARP/NS targets, delays, LACP options, peer notifications, primary/active slave, queue IDs, TLB/ALB controls, actor settings, broadcast-neighbor behavior, and port priority.
- `struct bond_opt_value` carries either a numeric value, string, small raw `extra` buffer, or `slave_dev` pointer.
- `struct bond_option` names an option, describes unsupported modes, valid values, flags, and the setter callback.
- Public helpers set options with or without notification, parse values, look up options by ID/name/value, and clear ARP/NS targets or update slave multicast addresses.
- Inline initializers `bond_opt_initval`, `bond_opt_initstr`, `bond_opt_initextra`, and `bond_opt_slave_initval` enforce the string-vs-value convention.

## Control Flow And State
Callers prepare a `bond_opt_value`, then pass it to `__bond_opt_set()` or `__bond_opt_set_notify()`. The option layer locates metadata by ID, validates mode/precondition flags, parses numeric/string/raw values through `bond_opt_parse()`, and invokes the option-specific setter. Sysfs uses `bond_opt_get_by_name()`, netlink uses option IDs and `nlattr` error reporting, and module parameter initialization parses defaults with the same tables.

## State And Persistence Behavior
This header does not store option state. Successful setters mutate `struct bonding.params`, slave state, ARP/NS target arrays, active slave references, or mode-specific settings in implementation code. Options persist for the lifetime of the bond device and may be surfaced through sysfs/proc/netlink.

## Dependencies And Integration Points
The header depends on Linux bit, limits, type, string, netlink, and netdevice declarations. Implementations live in `drivers/net/bonding/bond_options.c`, with callers in `bond_sysfs.c`, `bond_netlink.c`, `bond_procfs.c`, and `bond_main.c`. IPv6 NS target helpers are gated by `CONFIG_IPV6`.

## Risks
- Option enum order is used as bit positions and table IDs; insertion/reordering must match implementation tables.
- `__bond_opt_init()` copies raw extra data only up to `BOND_OPT_EXTRA_MAXLEN`; callers must not pass oversized or pointer-lifetime-sensitive raw data except through the dedicated slave helper.
- Mode/precondition flags must be kept synchronized with setters, or users can change unsafe options while slaves are present or the device is up.
- String/numeric ambiguity is resolved by `ULLONG_MAX`; callers must use the right initializer.

## Test Signals
- Option tests should cover sysfs, netlink, and module-parameter parse paths for every option ID.
- Boundary tests should validate min/max/default values, unsupported modes, no-slaves and interface-down restrictions, raw-value parsing, ARP/NS target clearing, and bad netlink extack reporting.
