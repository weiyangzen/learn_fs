# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_hdcp_gsc_message.h

## Purpose

`intel_hdcp_gsc_message.h` exposes the minimal GSC-backed HDCP lifecycle API to the generic HDCP core. It keeps the command translation implementation private to `intel_hdcp_gsc_message.c`.

## Important APIs, Types, And Functions

The header forward declares `struct intel_display` and declares `intel_hdcp_gsc_init(struct intel_display *display)` plus `intel_hdcp_gsc_fini(struct intel_display *display)`. No command structs or GSC internals are exposed here.

## Control Flow

`intel_hdcp_component_init()` calls `intel_hdcp_gsc_init()` when the platform routes HDCP 2.2 through GSC. `intel_hdcp_component_fini()` calls `intel_hdcp_gsc_fini()` on teardown. All authentication-stage calls then go through the `i915_hdcp_arbiter` installed by init rather than through this header.

## State And Persistence Behavior

The header stores no state. The implementation behind it allocates and frees display-level GSC HDCP context and arbiter pointers.

## Dependencies And Integration Points

This header integrates the GSC message implementation with `intel_hdcp.c` while avoiding broader dependency exposure. It depends only on a forward-declared display object.

## Risks And Edge Cases

API misuse risk is lifecycle ordering: fini must not run while HDCP authentication work can still dereference the arbiter or GSC context. Any signature change affects the generic component init/fini path.

## Test Signals

Build coverage plus runtime init/fini on GSC-capable platforms are the main signals. Successful HDCP 2.2 capability checks after init and clean unload after fini validate the contract.
