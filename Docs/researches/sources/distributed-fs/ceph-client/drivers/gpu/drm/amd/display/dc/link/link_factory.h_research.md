# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/link_factory.h

## Purpose

`link_factory.h` declares the basic link object lifecycle API.

## Important APIs, Types, And Functions

It exposes `link_create(const struct link_init_data *init_params)` and `link_destroy(struct dc_link **link)`. The service lifecycle functions are implemented in `link_factory.c` but not declared here in this snapshot, implying they are declared through another shared header or used with local visibility expectations.

## Control Flow

The header has no runtime flow. Callers use `link_create()` to allocate and construct physical or DPIA links and `link_destroy()` to destruct, free, and null a link pointer.

## State And Persistence Behavior

No state is stored in the header. The implementation allocates and releases `struct dc_link` objects and their nested DDC, panel, encoder, and sink resources.

## Dependencies And Integration Points

It includes `link_service.h` for lifecycle types. It is the public entry for DC resource-pool/link initialization code.

## Risks And Edge Cases

`link_destroy()` expects a valid pointer-to-pointer and does not advertise null tolerance. Creation failure returns null after partial cleanup. Callers must not use link fields after destruction because the pointer is explicitly nulled.

## Test Signals

Build coverage catches signature drift. Runtime tests should validate link create/destroy across physical and DPIA connectors, including failure cleanup paths.
