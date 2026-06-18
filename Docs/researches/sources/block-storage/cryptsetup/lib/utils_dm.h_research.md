# File Research: sources/block-storage/cryptsetup/lib/utils_dm.h

## Purpose
Declares cryptsetup’s internal device-mapper backend interface, target structures, and feature flags.

## Key Responsibilities
- Defines dm resume/suspend private flags and kernel-support feature flags.
- Defines dm target types: crypt, verity, integrity, linear, error, zero, unknown.
- Defines active-device query flags.
- Describes `struct dm_target` for crypt, verity, integrity, linear, and zero target parameters.
- Describes `struct crypt_dm_active_device` for active mapping state and target segment data.
- Declares target construction, dm create/reload/suspend/resume/remove/status/query helpers.
- Declares dm name, UUID, dependency, and devpath helper functions.

## Important Details
- Several feature flags encode kernel target capability detection, including verity FEC/signatures, integrity options, keyring keys, sector sizes, and workqueue options.
- `DM_INTEGRITY_DISCARDS_SUPPORTED` and `DM_INTEGRITY_RESIZE_SUPPORTED` share the same bit by design comment.
- `single_segment()` is a small helper for active-device segment checks.

## Dependencies
Forward-declares core cryptsetup structs and is consumed by activation, storage wrapper, verity, and devpath code.
