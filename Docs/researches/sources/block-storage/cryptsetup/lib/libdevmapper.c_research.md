# File Research: sources/block-storage/cryptsetup/lib/libdevmapper.c

This file is the libcryptsetup device-mapper backend. It translates cryptsetup’s internal target descriptions into Linux device-mapper tasks and parses active kernel dm tables back into cryptsetup structures.

Major responsibilities:
- Initializes and tears down libdevmapper logging/state via `dm_backend_init` and `dm_backend_exit`.
- Probes device-mapper ioctl and target versions with `_dm_check_versions`, then records feature flags for dm-crypt, dm-verity, dm-integrity, dm-zero, deferred remove, secure data, target-version probing, kernel keyring keys, sector-size support, discard support, FEC, verity signatures, workqueue options, high-priority dm-crypt, and integrity inline mode.
- Builds target parameter strings for:
  - dm-crypt: cipher/CAPI conversion, key or keyring-key string, IV offset, data device, data offset, discards, sector size, integrity tags, workqueue/performance options.
  - dm-verity: data/hash/FEC devices, block sizes, hash algorithm, root hash, salt, corruption policy, FEC options, root-hash signature key description.
  - dm-integrity: data/meta devices, tag size, journal/direct/recovery/bitmap/inline modes, journal sizing, sector size, integrity/MAC/encryption keys, discard/recalculate/fixup flags.
  - dm-linear and dm-zero.
- Creates, reloads, resumes, suspends, clears, removes, and force-removes DM devices.
- Handles udev synchronization cookies and private-device udev rule suppression.
- Uses forced deactivation by replacing busy mappings with read-only `error` targets when requested.
- Queries active mappings through `DM_DEVICE_TABLE` and `DM_DEVICE_STATUS`, parsing dm-crypt, dm-verity, dm-integrity, dm-linear, dm-error, and dm-zero target lines.
- Reports status for active/busy/suspended devices, verity validity and repaired block count, integrity failure count, dependency chains, active integrity helper mappings, and DM UUID/type comparisons.
- Provides target setter helpers: `dm_crypt_target_set`, `dm_verity_target_set`, `dm_integrity_target_set`, `dm_linear_target_set`, `dm_zero_target_set`.

Security-sensitive behavior:
- Uses `dm_task_secure_data` when available so libdevmapper treats table data as sensitive.
- Allocates DM target parameter strings and key material with `crypt_safe_alloc` and wipes/free them with `crypt_safe_free`.
- Wipes parsed dm-crypt key strings after query.
- Supports keyring-backed dm-crypt keys and converts key descriptions into dm-crypt table syntax.
- Refuses to return crypt keys from suspended devices.
- On suspend with key wipe, sends the `key wipe` dm-crypt target message, and can reinstate keys through `key set ...` target messages.

Filesystem/block-storage relevance:
- This is the operational bridge from libcryptsetup policy/metadata to live Linux block devices under `/dev/mapper`.
- It controls mapped-device geometry, read-only state, discard/TRIM behavior, dm-verity corruption handling, dm-integrity journaling/recovery, and stacked crypt+integrity relationships.
- Query paths reconstruct block mapping state so higher-level cryptsetup APIs can report or refresh active devices.

Important implementation details:
- libdevmapper is treated as not context-friendly; a global `_context` is switched around each DM call for logging.
- Version probing is cached globally with `_dm_*_checked` booleans and `_dm_flags`.
- `_dm_create_device` distinguishes existing devices, missing referenced devices, kernel key errors, and busy devices using both dm-task errno and follow-up status checks.
- `check_retry` silently drops unsupported optional dm-crypt flags for retry in some cases, but hard-errors for explicitly requested unsupported verity/integrity features.
- Active table parsers are strict: unknown target options generally return `-EINVAL`, which prevents silently accepting unrecognized kernel table state.
