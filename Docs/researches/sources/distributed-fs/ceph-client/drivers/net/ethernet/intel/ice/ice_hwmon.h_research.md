# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_hwmon.h

## Purpose
Provides the conditional public interface for `ice` hwmon support.

## Important APIs, types, and functions
- `ice_hwmon_init(struct ice_pf *pf)` and `ice_hwmon_exit(struct ice_pf *pf)` are real declarations under `CONFIG_ICE_HWMON`.
- The same names are inline no-ops when hwmon support is not configured.

## Control flow
No runtime control flow exists in the header. Compile-time configuration selects real hooks or stubs.

## State and persistence behavior
No state is stored here; `pf->hwmon_dev` is managed by the implementation when enabled.

## Dependencies and integration points
Used by PF initialization/teardown code so callers can invoke hwmon hooks unconditionally.

## Risks
The stubs should remain side-effect free. Signature changes must be coordinated with probe/remove call sites and the implementation.

## Test signals
Build coverage for both `CONFIG_ICE_HWMON` states verifies the contract.
