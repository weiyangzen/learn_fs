<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dm-verity-loadpin.h -->
# sources/distributed-fs/ceph-client/include/linux/dm-verity-loadpin.h

## Purpose
Connects dm-verity root digests with LoadPin so the security subsystem can trust files loaded from verified block devices.

## Important APIs, Types, And Functions
Declares global `dm_verity_loadpin_trusted_root_digests`, `struct dm_verity_loadpin_trusted_root_digest`, and `dm_verity_loadpin_is_bdev_trusted()`. The digest struct has a list node, length, and counted flexible data array. Without `CONFIG_SECURITY_LOADPIN_VERITY`, the trust check returns false.

## Control Flow
dm-verity or security setup populates the trusted digest list. LoadPin asks whether a block device is trusted; the implementation checks the device's verity root digest against the trusted list.

## State And Persistence
State is the in-kernel list of trusted root digests. Trust is runtime security policy; the underlying verity metadata persists on block devices outside this header.

## Dependencies And Integration Points
Depends on lists, block devices, dm-verity, and LoadPin security configuration.

## Risks And Edge Cases
Digest length and list lifetime must be validated. The disabled-config stub must not accidentally grant trust. Race-free list updates and block-device identity checks are critical to avoid trusting the wrong device.

## Test Signals
Tests should cover trusted and untrusted root digests, malformed digest lengths, list update/removal, block-device teardown, and builds with LoadPin verity disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dm-verity-loadpin.h -->
