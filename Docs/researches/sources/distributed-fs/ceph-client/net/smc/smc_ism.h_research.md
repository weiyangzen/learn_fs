# sources/distributed-fs/ceph-client/net/smc/smc_ism.h

## Purpose
`smc_ism.h` defines the SMC-D device-list, VLAN, system-EID, DIBS-GID conversion, and helper API used by SMC-D core and diagnostics.

## Important APIs, Types, and Functions
The header defines `SMC_EMULATED_ISM_CHID_MASK`, `SMC_ISM_IDENT_MASK`, `struct smcd_dev_list`, `struct smc_ism_vlanid`, and `struct smc_ism_seid`. It declares the SMC-D device list and all ISM helpers implemented in `smc_ism.c`. Inline helpers include `smc_ism_write()`, `__smc_ism_is_emulated()`, `smc_ism_is_emulated()`, `smc_ism_is_loopback()`, `copy_to_smcdgid()`, and `copy_to_dibsgid()`.

## Control Flow
Callers use `smc_ism_cantalk()` during negotiation, `smc_ism_get_vlan()`/`put_vlan()` around VLAN-scoped link-group lifetime, `smc_ism_register_dmb()`/`unregister_dmb()` for RMB allocation, and `smc_ism_set_conn()`/`unset_conn()` for interrupt routing. Data transfer uses `smc_ism_write()` to call the DIBS `move_data` operation and normalize positive returns to 0.

## State and Persistence
The header describes transient device-list and VLAN-refcount state. Conversion helpers translate between SMC-D wire GID fields and DIBS UUIDs without storing data. Emulated and loopback checks are computed from DIBS fabric IDs.

## Dependencies and Integration Points
It depends on Linux UIO/types/mutex/DIBS APIs and local SMC structures. It is consumed by SMC core, diagnostics, netlink, and ISM implementation code. The conversion helpers are important for CLC negotiation, DMB registration, diagnostics, and event handling.

## Risks
Endian conversion for GIDs must stay consistent between CLC, diagnostics, and DIBS callbacks. Emulated ISM matching uses GID extension semantics that differ from native devices. `smc_ism_write()` assumes valid DIBS operations and maps nonnegative device returns to success, so callers cannot distinguish partial positive progress.

## Test Signals
Validate GID round trips, emulated and loopback CHID classification, DMB write behavior, VLAN refcount paths, v2 capability reporting, and compile coverage with different DIBS providers.
