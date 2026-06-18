# sources/distributed-fs/ceph/src/client/fscrypt_uapi.h

## Purpose
`fscrypt_uapi.h` provides Ceph FUSE-facing wrappers and restricted ioctl definitions around Linux fscrypt user API structures.

## Important APIs, Types, and Functions
On Linux it includes `<linux/fscrypt.h>`, defines `fscrypt_policy_arg` as a union of policy v1/v2, defines `fscrypt_add_key64_arg` with a 64-byte raw key buffer, and declares restricted ioctl constants for set/get policy and add-key operations.

## Control Flow
There is no executable flow. The header is consumed by FUSE ioctl handling to parse and reply to fscrypt requests.

## State and Persistence Behavior
The structs describe user/kernel ABI payloads. Persistent encryption state is stored by CephFS/FSCrypt code outside this header.

## Dependencies and Integration Points
`fuse_ll.cc` includes this header and accepts both standard and restricted fscrypt ioctl numbers. It integrates with `FSCrypt.h` and `Client` fscrypt methods.

## Risks
ABI layout must stay aligned with Linux fscrypt definitions. The definitions are Linux-only, so non-Linux builds must avoid references behind the same preprocessor guards.

## Test Signals
Builds should verify ioctl constants compile on Linux, and FUSE ioctl tests should cover v2 policy, key add/remove/status, and short-buffer errors.
