# sources/distributed-fs/ceph-client/net/psp/psp-nl-gen.c

## Purpose
`psp-nl-gen.c` is generated YNL kernel code from `Documentation/netlink/specs/psp.yaml`. It defines PSP generic netlink policies, split operation tables, multicast groups, and the `psp_nl_family` object registered by `psp_main.c`.

## Important APIs, types, and functions
The file exports `psp_keys_nl_policy` and defines per-command policies for device get/set, key rotation, RX association, TX association, and stats get. `psp_nl_ops[]` maps PSP commands to generated policy metadata plus implementation callbacks declared in `psp-nl-gen.h`, such as `psp_device_get_locked()`, `psp_assoc_device_get_locked()`, `psp_device_unlock()`, `psp_nl_dev_get_doit()`, `psp_nl_tx_assoc_doit()`, and dump handlers.

`psp_nl_mcgrps[]` defines `mgmt` and `use` multicast groups. `psp_nl_family` sets family name/version, `netnsok`, `parallel_ops`, module owner, split ops, and multicast groups.

## Control flow and state
Runtime control is generic-netlink driven. For each command, the family applies the generated attribute policy, optional pre-doit lock/acquire callback, implementation callback, and post-doit unlock callback. Dump operations skip pre/post for the entries that only provide dumpit. No mutable state is stored in this file beyond generic netlink family registration state owned by the netlink core.

## Dependencies and integration points
This file depends on UAPI definitions in `<uapi/linux/psp.h>` and implementation callbacks in `psp_nl.c` plus locking helpers declared in the generated header. It is registered by `genl_register_family(&psp_nl_family)` in `psp_main.c`.

## Risks and edge cases
Generated files should not be hand-edited; drift from the YAML spec can break user/kernel ABI. Policy bounds are security critical: device ids require minimum 1, enabled version mask is limited to `0xf`, association version is max 3, and TX keys are nested under `psp_keys_nl_policy`. `parallel_ops = true` makes callback locking discipline important.

## Test signals
Use YNL/generated userspace tests to validate every command policy, missing/invalid attributes, dump behavior, multicast group discovery, parallel command locking, and regeneration from `psp.yaml` producing no unexpected diff.
