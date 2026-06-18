# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_devlink.c

## Purpose

`i40e_devlink.c` integrates i40e PFs with Linux devlink. It allocates the PF inside a devlink private area, exposes firmware/device version information, registers a runtime `max_mac_per_vf` parameter, and creates a physical devlink port for each PF.

## Important APIs, Types, And Functions

- `i40e_max_mac_per_vf_get()` and `i40e_max_mac_per_vf_set()` implement the generic devlink `MAX_MAC_PER_VF` runtime parameter.
- Version helpers format DSN, management firmware version/build, API version, NVM version, EETRACK, CIVD, and PBA data.
- `i40e_devlink_info_get()` populates devlink info request fields.
- `i40e_alloc_pf()` and `i40e_free_pf()` allocate/free `struct i40e_pf` via devlink private storage.
- `i40e_devlink_register()` and `i40e_devlink_unregister()` register/unregister parameters and the devlink instance.
- `i40e_devlink_create_port()` and `i40e_devlink_destroy_port()` manage `pf->devlink_port`.

## Control Flow

Probe-time allocation calls `devlink_alloc()` with i40e ops and returns `devlink_priv()`. Registration first registers devlink params, logs errors, then registers devlink. Info requests call formatting helpers in sequence and short-circuit on devlink put errors. Port creation builds physical port attrs using `hw.pf_id` and a switch id derived from PCI DSN, then registers the port with the PF id as index.

## State And Persistence

Runtime devlink state includes the devlink instance, registered parameter state, `pf->max_mac_per_vf`, and `pf->devlink_port`. The `max_mac_per_vf` parameter is runtime-only here and cannot be changed while SR-IOV VFs are allocated. Version information is read from hardware/adminq state and device identifiers.

## Dependencies And Integration Points

The file depends on `<net/devlink.h>`, PCI DSN helpers, unaligned big-endian formatting helpers, i40e PF hardware state, version formatting helpers declared elsewhere, and devlink core registration APIs.

## Risks

- `i40e_devlink_register()` logs parameter registration failure but still registers devlink, so parameter availability can differ from devlink availability.
- `max_mac_per_vf` changes are blocked only when `num_alloc_vfs > 0`; callers must ensure SR-IOV lifecycle serialization.
- Empty PBA strings are skipped, which is intentional but means board id can be absent.
- Switch id uses PCI DSN; hardware without a meaningful DSN may produce less useful devlink topology identity.

## Test Signals

Use `devlink dev info` to verify serial and version fields, `devlink dev param show/set` for `max_mac_per_vf`, tests that setting the parameter fails with SR-IOV enabled, and probe/remove tests validating devlink and port registration cleanup.
