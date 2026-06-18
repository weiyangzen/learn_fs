# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/compressor.h

## Purpose

`compressor.h` defines the legacy frame-buffer compression (FBC) abstraction. It tracks compression capabilities, buffer sizing, attached controller instance, memory geometry, and callbacks for enabling, disabling, and programming FBC state.

## Important APIs, Types, And Functions

Important types are `enum fbc_compress_ratio`, `union fbc_physical_address`, `struct compr_addr_and_pitch_params`, `enum fbc_hw_max_resolution_supported`, `struct compressor_funcs`, `struct compressor`, `struct fbc_input_info`, and `struct fbc_requested_compressed_size`. Operations include `power_up_fbc`, `enable_fbc`, `disable_fbc`, `set_fbc_invalidation_triggers`, `surface_address_and_pitch`, and `is_fbc_enabled_in_hw`.

## Control Flow

Callers calculate source view size and compressed-surface needs, allocate or select an FBC buffer, set the compressor surface address/pitch, program invalidation triggers, and enable FBC for a controller instance. Disable paths clear FBC state and can query hardware mapping to determine the active CRTC.

## State And Persistence Behavior

`struct compressor` persists in the DC resource set. It stores attached instance, enable state, option bits, compressed-surface physical address, panel size, memory layout information, allocated/preferred sizes, LPT channel count, and minimum compression ratio. Persistent effects are hardware FBC programming and in-memory resource bookkeeping.

## Dependencies And Integration Points

The header depends on graphics object IDs and BIOS parser interfaces. It integrates with embedded-panel paths, memory allocation, invalidation logic, and older DCE bandwidth/FBC support. It is separate from DCN DCC surface compression handled by HUBP/HUBBUB.

## Risks And Edge Cases

FBC is constrained by fixed maximum resolutions and memory layout. Buffer size alignment and framebuffer-pool requirements must match firmware and hardware expectations. Stale `attached_inst` or `is_enabled` state can map compression to the wrong controller. Dynamic allocation and LPT options have platform-specific constraints.

## Test Signals

Tests should cover enable/disable around mode sets, source-size boundary values, dynamic vs static buffer allocation, invalidation triggers, hardware enabled readback, embedded panel resolutions, and suspend/resume. Visual corruption and stale compressed frames are the key runtime failures.
