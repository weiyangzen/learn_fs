# sources/distributed-fs/orangefs/src/io/description/pint-distribution.c

## Purpose
Implements the core distribution registry, cloning/copying/freeing distribution descriptors, parameter get/set helpers, packed encode/decode wrappers, lookup, and debug dump.

## Important APIs, Types, And Functions
Exports `PINT_register_distribution`, `PINT_unregister_distribution`, `PINT_dist_create`, `PINT_dist_free`, `PINT_dist_copy`, `PINT_dist_getparams`, `PINT_dist_setparams`, `PINT_dist_lookup`, `PINT_dist_encode`, `PINT_dist_decode`, and `PINT_dist_dump`. Global private state is `PINT_Dist_table` and `PINT_Dist_count`.

## Control Flow
Registration appends a static distribution to the fixed table and calls its `registration_init`. Unregistration finds by name, calls `unregister`, bubbles table entries down, and clears the last slot. `PINT_dist_create` looks up a named static distribution, allocates one contiguous packed object, copies the name and params into that object, and keeps method pointers shared. Copy duplicates an already packed distribution and fixes internal pointers. Encode/decode defer to macros that serialize the name and method-specific params.

## State And Persistence
State is a fixed-size in-memory table of registered distributions. Packed distribution objects are heap allocations owned by callers. Encoded distributions are persistent metadata only when stored by higher layers; this file just packs/unpacks buffers.

## Dependencies And Integration Points
Depends on `pint-distribution.h`, encode stubs, gossip logging, and built-in distribution globals. Used by request encode/decode and distribution evaluation across clients and servers.

## Risks And Test Signals
Risks include a hard table size of eight, no duplicate registration checks, `PINT_dist_create` copying only `strlen+1` bytes of name while using rounded name space, decode macros exiting the process on missing methods, and shallow sharing of method tables. Tests should cover registry overflow, duplicate names, create/copy/free, parameter get/set, encode/decode before and after initialization, and lookup failures.
