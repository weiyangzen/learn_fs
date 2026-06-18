# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/virtual/virtual_link_encoder.c

## Purpose
Provides a virtual `link_encoder` implementation for virtual display paths that need to satisfy Display Core interfaces without programming physical link hardware. Most callbacks are no-ops, with validation always succeeding and a conservative default DP-like max link capability returned.

## Important APIs, Types, And Functions
`virtual_link_encoder_construct()` initializes a caller-provided `struct link_encoder` with the virtual function table, context, id, HPD source, connector, transmitter, `SIGNAL_TYPE_VIRTUAL`, and `ENGINE_ID_VIRTUAL`. The static function table includes no-op setup, TMDS/DP/MST enable, disable, lane settings, PHY pattern, MST allocation, DIG BE/FE connect, and init callbacks. `virtual_link_encoder_destroy()` frees the allocated encoder and nulls the caller pointer. `virtual_link_encoder_get_max_link_cap()` returns four lanes at high link rate with 0.5% downspread.

## Control Flow
All enable/setup/programming callbacks immediately discard parameters and return void, except validation returns true and max-cap copies a stack literal into the output. Destruction releases memory through `kfree()`. Construction is the only path that mutates the encoder object.

## State And Persistence
The virtual encoder persists only the base object fields assigned at construction. It has no hardware state and no private allocation beyond the object allocated by the caller.

## Dependencies And Integration Points
The file includes DM service headers and the virtual link header. It is used by core DC virtual link setup (`dc.c`) and allows higher-level link/resource logic to operate on virtual connectors without special-casing every physical operation.

## Risks
Because validation always returns true and operations are no-ops, higher layers must avoid using this encoder for physical connectors. The fixed max link cap may be misleading if virtual paths start modeling bandwidth constraints. Destroy assumes the object was heap allocated and owned by the link encoder pointer.

## Test Signals
Virtual display creation should construct and destroy cleanly, mode validation should proceed without hardware access, and no register/AUX/HPD operations should occur. Memory debugging can verify destroy nulls the pointer and frees the object.
