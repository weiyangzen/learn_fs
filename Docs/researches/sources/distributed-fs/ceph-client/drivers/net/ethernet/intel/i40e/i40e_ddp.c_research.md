# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_ddp.c

## Purpose

`i40e_ddp.c` implements Dynamic Device Personalization profile load and rollback through the ethtool flash callback. It validates DDP package structure, checks compatibility with already loaded profiles, writes or rolls back profile data in firmware, updates firmware profile tracking info, and keeps an in-memory rollback stack.

## Important APIs, Types, And Functions

- `struct i40e_ddp_profile_list` mirrors firmware’s loaded-profile list response.
- `struct i40e_ddp_old_profile_list` stores previously loaded profile buffers on `pf->ddp_old_prof` for rollback.
- `i40e_ddp_profiles_eq()` compares track id, version, and name.
- `i40e_ddp_does_profile_exist()` and `i40e_ddp_does_profile_overlap()` query firmware and enforce duplicate/overlap rules.
- `i40e_add_pinfo()` and `i40e_del_pinfo()` write profile info sections with add/remove track-id operations.
- `i40e_ddp_is_pkg_hdr_valid()` performs package header version, size, segment count, alignment, and bounds checks.
- `i40e_ddp_load()` performs the core add/remove flow, and `i40e_ddp_flash()` is the public ethtool flash entry point.

## Control Flow

`i40e_ddp_flash()` only accepts region `100` and only permits operations on physical function 0. A normal flash request builds a firmware path under `intel/i40e/ddp/`, calls `request_firmware()`, and loads the profile via `i40e_ddp_load(..., true)`. On success it allocates a rollback entry and copies the firmware image into `pf->ddp_old_prof`. A request whose data string is `"-"` invokes `i40e_ddp_restore()` to roll back the first stored profile.

`i40e_ddp_load()` validates the package, finds metadata and i40e profile segments, builds a profile identity, checks existence and overlap, writes or rolls back profile data using `i40e_write_profile()` or `i40e_rollback_profile()`, then updates firmware’s profile list using `i40e_add_pinfo()` or `i40e_del_pinfo()`.

## State And Persistence

Firmware stores the active DDP profile and loaded profile metadata. Driver rollback state is volatile memory in `pf->ddp_old_prof`; it is lost on driver unload/reset and can consume memory proportional to successfully loaded profile sizes. Firmware files are loaded from the kernel firmware search path.

## Dependencies And Integration Points

The file depends on `<linux/firmware.h>`, ethtool flash plumbing, i40e package/segment definitions, admin queue helpers `i40e_aq_get_ddp_list()` and `i40e_aq_write_ddp()`, and profile write/rollback helpers from the i40e common code.

## Risks

- Rollback is best effort: if allocation for rollback storage fails, the new profile remains loaded but cannot be restored through this in-memory stack.
- Package validation is structural but not cryptographic; trust ultimately rests on firmware acceptance and admin-controlled firmware file paths.
- Profile overlap semantics depend on track-id group encoding.
- Only PF0 can operate, so multi-function systems need clear operator handling.

## Test Signals

Test invalid region, non-PF0 rejection, missing firmware file, malformed package headers, missing metadata/profile segments, duplicate profile detection, overlap detection, unsupported-device `-ENODEV` mapping to `-EPERM`, successful add plus rollback, and rollback allocation failure logging.
