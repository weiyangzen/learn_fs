# sources/distributed-fs/orangefs/src/io/description/dist-varstrip.c

## Purpose
Implements the variable-stripe distribution, where a parameter string defines an arbitrary repeating sequence of strips assigned to data-file numbers.

## Important APIs, Types, And Functions
Defines methods for logical-to-physical and physical-to-logical mapping, next mapped offset, contiguous length, logical file size, data-file count, custom parameter setting, encode/decode, registration/unregistration, params string, block size, and exports `PINT_dist varstrip_dist`.

## Control Flow
Most methods parse `params->strips` into strip descriptors on every call. Logical-to-physical finds the stripe repeat, locates the strip on the current server containing the logical offset, and accounts for earlier strips assigned to the same server. Physical-to-logical computes the stripe number from total strips assigned to this server and finds the descriptor containing the physical in-stripe offset. `next_mapped_offset` finds the current descriptor and either returns the logical offset, a later strip for this server, or the first strip for this server in the next stripe. `get_num_dfiles` verifies all data-file numbers from zero through the maximum appear and fit within available servers.

## State And Persistence
Static default params contain an empty strip string. Actual distribution instances persist the strip string in encoded metadata. Parsed strip arrays are temporary heap allocations.

## Dependencies And Integration Points
Depends on `pint-distribution`, `pint-dist-utils`, `pvfs2-dist-varstrip.h`, `dist-varstrip-parser`, and gossip logging. Registered by `PINT_dist_initialize`.

## Risks And Test Signals
Risks include repeated parsing overhead, incomplete logical-to-physical handling for offsets not mapped to the current server, possible memory leak on some `get_num_dfiles` error returns, no explicit rejection of unknown parameter names, and divide by zero if a server has no strips despite validation gaps. Tests should cover valid variable layouts, missing server numbers, too many data files, next-mapped wrapping, physical/logical round trips, contiguous lengths, and encode/decode of strip strings.
