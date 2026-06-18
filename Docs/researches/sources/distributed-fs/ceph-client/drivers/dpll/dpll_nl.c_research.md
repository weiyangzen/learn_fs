# sources/distributed-fs/ceph-client/drivers/dpll/dpll_nl.c

## Purpose
This is generated YNL kernel glue for the DPLL generic-netlink family. It defines netlink attribute policies, split operation tables, multicast groups, and the `dpll_nl_family` descriptor used by `dpll_netlink.c`.

## Important APIs and data
Policy arrays include `dpll_pin_parent_device_nl_policy`, `dpll_pin_parent_pin_nl_policy`, `dpll_reference_sync_nl_policy`, and per-command static policies for device ID/get/set and pin ID/get/set. `dpll_nl_ops[]` binds DPLL commands to the hand-written pre/do/post handlers. `dpll_nl_mcgrps[]` defines the monitor multicast group. `dpll_nl_family` sets the family name/version, `netnsok`, `parallel_ops`, module owner, ops, and groups.

## Control flow
Generic netlink dispatch validates incoming attributes against these policies, then calls the registered pre/do/post handlers. Device and pin ID lookups take only identity attributes and use a global lock helper. Object-specific GET/SET commands use pre-doit hooks to resolve the numeric ID into `info->user_ptr[0]` under `dpll_lock`.

## State and persistence
The file contains static immutable dispatch metadata plus the exported family object. It has no hardware or persistent state.

## Dependencies and integration points
It is generated from `Documentation/netlink/specs/dpll.yaml`, includes generic netlink headers and `uapi/linux/dpll.h`, and declares callbacks implemented in `dpll_netlink.c` through `dpll_nl.h`.

## Risks and test signals
The main risk is generated-code drift from the YAML ABI or mismatched max attribute bounds. Tests should include YNL schema regeneration checks, invalid attribute type/range tests, command capability checks, and module load/unload coverage ensuring the family registers with the intended monitor group.
