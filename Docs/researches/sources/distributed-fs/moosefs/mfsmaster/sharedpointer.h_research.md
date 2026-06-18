# sources/distributed-fs/moosefs/mfsmaster/sharedpointer.h

## Purpose
`sharedpointer.h` declares a minimal opaque shared-pointer API used by master restore helpers.

## Important APIs, Types, And Functions
The header exports `shp_new(void *pointer, void (*freefn)(void*))`, `shp_get(void *vs)`, `shp_inc(void *vs)`, and `shp_dec(void *vs)`.

## Control Flow
Callers receive and pass around `void *` handles. The wrapped pointer is retrieved with `shp_get()`, and lifetime is managed manually with `shp_inc()` and `shp_dec()`.

## State, Persistence, And Dependencies
The header exposes no concrete struct and has no include dependencies. State is heap-owned by the C file.

## Integration Points
The restore file API accepts shared-pointer filename handles but types them as `void *`; this header supplies the required operations.

## Risks
The API is not type-safe. The destructor callback is required and must match the payload allocation method. The reference count is not thread-safe.

## Test Signals
Compile tests should include this header from C and C++-like strict contexts if applicable. Runtime tests should check destructor pairing with the payload allocator used by callers.
