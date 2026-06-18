# sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec.h

## Purpose
This small header defines EC translator-wide constants, internal xattr names, cache limits, and derived maximum node counts.

## Important APIs, Types, And Functions
Important macros include `EC_XATTR_PREFIX`, `EC_XATTR_CONFIG`, `EC_XATTR_SIZE`, `EC_XATTR_VERSION`, `EC_XATTR_HEAL`, `EC_XATTR_HEAL_NEW`, `EC_XATTR_DIRTY`, `EC_XATTR_READMASK`, `EC_STRIPE_CACHE_MAX_SIZE`, `EC_VERSION_SIZE`, `EC_SHD_INODE_LRU_LIMIT`, and `EC_DEFAULT_INODE_READ_MASK`. It also aliases `EC_MAX_FRAGMENTS` to `EC_METHOD_MAX_FRAGMENTS` and derives `EC_MAX_NODES`.

## Control Flow
There is no executable control flow. These macros are consumed by option parsing, xattr filtering, heal logic, and read-mask handling.

## State And Persistence Behavior
The xattr names define persistent metadata keys under `trusted.ec.*`; changing them would break compatibility with existing EC volumes. Cache and LRU constants affect in-memory behavior only.

## Dependencies And Integration Points
The header includes `ec-method.h` to derive coding limits. It is included by `ec.c` and other EC components that need common names.

## Risks
The main risk is compatibility: xattr names and maximum-node derivation are part of the translator contract. `EC_MAX_NODES` deliberately enforces redundancy less than fragment count; relaxing it would require broader layout review.

## Test Signals
Build tests catch macro availability. Functional tests should verify internal xattrs remain protected, heal xattrs are recognized, and invalid redundancy/node configurations are rejected consistently with these constants.
