# sources/distributed-fs/orangefs/src/io/description/dist-twod-stripe.c

## Purpose
Implements a two-dimensional stripe distribution that partitions servers into groups, stripes within a group for a configurable factor, then advances across groups.

## Important APIs, Types, And Functions
Defines methods for logical/physical mapping, next mapped offset, contiguous length, logical file size, custom parameter setting, parameter encode/decode, registration/unregistration, params string, block size, default params, and exports `PINT_dist twod_stripe_dist`.

## Control Flow
Mapping functions compute effective group count, small group size, server's group, servers in that group, group-local server number, global stripe size, and per-group offsets. Logical-to-physical accumulates full global stripes and, when the logical offset falls inside this server's group, adds group strip progress. Physical-to-logical reconstructs the global logical position from physical strip count, group position, and server position. `next_mapped_offset` advances an arbitrary logical offset to this server's next represented byte. Parameter setting validates positive `strip_size`, `num_groups`, and `group_strip_factor` before copying.

## State And Persistence
Static default params include default groups, strip size, and factor. Per-distribution instances persist params in encoded metadata. No other persistent state exists.

## Dependencies And Integration Points
Depends on PVFS encode stubs, `pint-distribution.h`, `pint-dist-utils.h`, `pvfs2-dist-twod-stripe.h`, logging, and utility macros. Registered by distribution initialization.

## Risks And Test Signals
Risks include division by zero if invalid parameters still flow after logging, behavior when `num_groups > server_ct`, uneven last-group math, `physical_to_logical_offset` using `strips > factor` versus `>=`, and complex boundary cases. Tests should cover even and uneven group partitions, group counts larger than servers, strip-factor boundaries, parameter encode/decode, and offset round trips for every server.
