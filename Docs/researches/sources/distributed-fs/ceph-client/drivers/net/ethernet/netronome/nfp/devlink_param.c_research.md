# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/devlink_param.c

## Purpose
This file exposes selected NFP persistent hardware-info settings as generic devlink parameters. It maps devlink firmware-load-policy and reset-on-driver-probe values to NSP hwinfo keys and registers the parameters only when the NSP supports hwinfo lookup and set.

## Important APIs, types, and functions
- `struct nfp_devlink_param_u8_arg` describes one u8 parameter mapping: hwinfo key/default, invalid devlink value, bidirectional value maps, and valid ranges.
- `nfp_devlink_u8_args[]` defines mappings for `DEVLINK_PARAM_GENERIC_ID_FW_LOAD_POLICY` and `DEVLINK_PARAM_GENERIC_ID_RESET_DEV_ON_DRV_PROBE`.
- `nfp_devlink_param_u8_get()` opens NSP, looks up hwinfo with a default, parses and validates the hardware value, and returns the mapped devlink value or an unknown value.
- `nfp_devlink_param_u8_set()` maps a validated devlink value back to `key=value` and writes it through NSP hwinfo set.
- `nfp_devlink_param_u8_validate()` rejects out-of-range and unknown/invalid devlink values.
- `nfp_devlink_params_register()` and `_unregister()` gate registration on NSP capability.

## Control flow
Registration probes NSP support. If `nfp_nsp_open()` fails, registration returns the error; if lookup/set capabilities are absent, registration returns 0 and no params are registered. Get/set operations independently open and close NSP, so they do not persist NSP handles. Invalid stored hwinfo values are converted to devlink "unknown" when the param supports that, or to the configured negative error otherwise.

## State and persistence
The persistent state lives in device hwinfo, not in this driver. Devlink get reads current hwinfo; devlink set writes a permanent hwinfo setting because the parameters are registered with `DEVLINK_PARAM_CMODE_PERMANENT`.

## Dependencies and integration points
The file integrates Linux devlink params with NFP NSP APIs (`nfp_nsp_hwinfo_lookup_optional`, `nfp_nsp_hwinfo_set`) and constants from `nfp_nsp.h`. It uses `priv_to_devlink(pf)` and `devlink_priv()` to bridge PF and devlink objects.

## Risks
The mapping arrays assume devlink IDs index directly into `nfp_devlink_u8_args`; unsupported IDs are rejected by array bounds. Range constants must stay consistent with both devlink generic enums and NSP hwinfo values. Unregistration repeats the support probe; if NSP access changes between register and unregister, params could be skipped or errors hidden, although that mirrors the current gating model.

## Test signals
Test devlink get/set for both params, invalid user values, invalid stored hwinfo values, missing hwinfo falling back to defaults, NSP open failures, and devices whose NSP lacks lookup/set support. Verify values persist across driver reload according to device hwinfo behavior.
