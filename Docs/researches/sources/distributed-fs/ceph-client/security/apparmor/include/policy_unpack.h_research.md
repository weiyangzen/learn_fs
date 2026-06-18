# sources/distributed-fs/ceph-client/security/apparmor/include/policy_unpack.h

Purpose: defines the binary policy-load interface used to convert serialized AppArmor policy blobs into in-kernel profiles and raw-load metadata.

Important APIs/types: `struct aa_load_ent` binds a new profile to old/rename targets and namespace names during atomic replacement. Packed flags/modes encode profile hats and runtime modes. `enum aa_code` defines the typed stream format. `struct aa_ext` is the unpack cursor. `struct aa_loaddata` holds raw policy payload, compression metadata, hash, ABI, revision, namespace, apparmorfs dentries, and two lifetimes: inode/fs users via `count` and profile users via `pcount`.

Control flow: apparmorfs receives a blob, wraps it in `aa_loaddata`, calls `aa_unpack()` into a load-entry list, then policy replacement deduplicates rawdata and attaches profile refs. KUnit-only unpack helpers expose primitive cursor reads for parser tests.

State and persistence: raw payload can remain compressed or uncompressed and may be exported under apparmorfs. `__aa_loaddata_update()` stamps policy revision, while `aa_rawdata_eq()` supports deduplication.

Dependencies and integration: integrates with `policy.c`, apparmorfs rawdata directories, hash/compression settings, profile replacement, and delayed work cleanup. Risks are malformed stream bounds, refcount split-brain between dentries and profiles, and ABI/version drift. Test signals include KUnit unpack primitive tests, invalid blob fuzzing, duplicate rawdata loads, compressed export reads, and failed atomic policy-load cleanup.
