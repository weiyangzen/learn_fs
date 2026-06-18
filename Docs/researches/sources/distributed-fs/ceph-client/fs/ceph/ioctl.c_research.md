# sources/distributed-fs/ceph-client/fs/ceph/ioctl.c

## Purpose
`ioctl.c` implements CephFS-specific file and directory ioctls plus forwarding for fscrypt ioctls. It exposes layout inspection/change, directory layout policy setting, file-offset-to-object-location mapping, lazy/sync I/O mode flags, and encryption policy/key operations through the VFS ioctl entry point.

## Important APIs, types, and functions
The public entry is `ceph_ioctl`. Important local handlers are `ceph_ioctl_get_layout`, `__validate_layout`, `ceph_ioctl_set_layout`, `ceph_ioctl_set_layout_policy`, `ceph_ioctl_get_dataloc`, `ceph_ioctl_lazyio`, `ceph_ioctl_syncio`, `vet_mds_for_fscrypt`, `ceph_set_encryption_policy`, and `ceph_ioctl_cmd_name`.

The file uses `struct ceph_ioctl_layout` and `struct ceph_ioctl_dataloc` from `ioctl.h`, `struct ceph_file_info` for per-open flags/mode, `struct ceph_inode_info` for layout and mode counters, MDS requests for layout mutation, and OSD map helpers for data location calculation.

## Control flow
`ceph_ioctl` logs the decoded command name and dispatches by command number. `CEPH_IOC_GET_LAYOUT` refreshes layout caps with `ceph_do_getattr`, then copies the current inode layout to userspace. `CEPH_IOC_SET_LAYOUT` copies user input, fetches the current layout, treats zero fields as "leave current value", validates the normalized layout, sends a `CEPH_MDS_OP_SETLAYOUT` request to the auth MDS, and drops shared/exclusive file caps so the reply can refresh layout state. `CEPH_IOC_SET_LAYOUT_POLICY` validates the supplied layout and sends `CEPH_MDS_OP_SETDIRLAYOUT` for the directory.

`CEPH_IOC_GET_DATALOC` copies a requested file offset from userspace, calculates the Ceph object number and object offset from the inode layout, builds the object name, maps the object locator through the current OSD map to a PG and primary OSD, optionally copies the OSD address, and returns the filled structure. `CEPH_IOC_LAZYIO` marks the open file mode lazy under `i_ceph_lock`, updates per-mode counts and MDS fmode touch state, then asks cap logic to re-evaluate. `CEPH_IOC_SYNCIO` sets a per-file sync flag.

For fscrypt ioctls, the dispatcher first verifies that an MDS session advertises `CEPHFS_FEATURE_ALTERNATE_NAME` for operations that depend on encrypted alternate names. Setting an encryption policy also rejects directories with striped layout, obtains shared file caps so empty-directory checks are reliable, delegates to `fscrypt_ioctl_set_policy`, and releases any cap refs.

## State and persistence behavior
Layout mutations persist in CephFS metadata through MDS requests. `GET_LAYOUT` and `GET_DATALOC` are read-only, but depend on current layout, MDS map data pool lists, and OSD map state. `LAZYIO` and `SYNCIO` are per-open client-side flags; lazy mode also updates `i_nr_by_mode` and cap desired-mode state in the inode, affecting consistency behavior while that file is open. Fscrypt policy and key ioctls persist or query fscrypt-managed metadata/key state, with Ceph-specific feature gating.

## Dependencies and integration points
The file integrates with VFS ioctl dispatch in Ceph file and dir operations, MDS client request creation/submission, MDS maps, OSD maps and striper object mapping, Ceph object locators, user-copy APIs, fscrypt ioctl helpers, cap acquisition/release, and Ceph debug logging. Layout validation depends on `mdsc->mdsmap->m_data_pg_pools`; data location depends on `osdc->osdmap` under `osdc->lock`.

## Risks
Risks include ABI compatibility of ioctl structs, accepting invalid striping or pool values, stale layout or OSD map data during dataloc queries, races between lazy/sync mode changes and cap revocation, per-file mode counter imbalance, feature detection that only checks the first non-null MDS session, and encryption-policy correctness when directory layout or rstats are stale. `CEPH_IOC_SET_LAYOUT_POLICY` and `CEPH_IOC_SYNCIO` both use ioctl number 5 with different direction encoding, which is ABI-sensitive and should not be changed casually.

## Test signals
Tests should cover layout get/set with zero/default fields, invalid unaligned stripe/object sizes, invalid data pools, directory layout policy inheritance, dataloc mapping across object boundaries and degraded/no-primary PGs, lazyio idempotence and cap checks, syncio path selection in reads/writes, fscrypt ioctls with and without MDS alternate-name support, striped directory encryption-policy rejection, and user-copy fault injection returning `-EFAULT`.
