# sources/distributed-fs/glusterfs/xlators/features/upcall/src/upcall-cache-invalidation.h

## Purpose
Defines the default cache invalidation timeout option for upcall.

## Important APIs, Types, and Functions
- `CACHE_INVALIDATION_TIMEOUT "60"` is used as the default value for the `cache-invalidation-timeout` volume option.

## Control Flow
No runtime control flow.

## State and Persistence
No state. The default value influences runtime private configuration at `init()`.

## Dependencies and Integration Points
Included by `upcall.c` when registering volume options.

## Risks
Changing the string alters default cache retention and notification behavior for deployments that do not set the option.

## Test Signals
Option parsing tests should confirm default timeout is 60 seconds.
