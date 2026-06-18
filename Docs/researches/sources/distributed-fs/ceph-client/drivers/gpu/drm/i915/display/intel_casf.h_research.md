# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_casf.h

## Purpose

`intel_casf.h` exposes the Content Adaptive Sharpness Filter interface to display atomic-check, readout, scaler, and commit code while keeping the implementation details in `intel_casf.c`.

## Important APIs, Types, And Functions

The header forward-declares `struct intel_crtc_state` and declares seven functions. `intel_casf_compute_config()` validates and computes CASF state from the user sharpness property. `intel_casf_update_strength()` performs a strength-only hardware update. `intel_casf_sharpness_get_config()` reads CASF state from hardware. `intel_casf_enable()` and `intel_casf_disable()` program or clear the filter. `intel_casf_scaler_compute_config()` computes scaler coefficients. `intel_casf_needs_scaler()` tells scaler allocation that CASF requires a scaler.

## Control Flow And Integration

Callers use the header in three phases: atomic validation computes `hw.casf_params`, scaler allocation checks whether CASF needs scaler resources, and commit/readout code programs or reconstructs the hardware state. The interface is intentionally CRTC-state centric, reflecting that CASF is per pipe and has no global state object.

## State And Persistence

No state is defined in the header. CASF state lives in `intel_crtc_state`, and hardware state is handled by the C implementation through per-pipe sharpness and scaler registers.

## Dependencies, Risks, And Test Signals

The header only includes `<linux/types.h>` for `bool` and basic types, which keeps include coupling low. The main risk is call ordering: coefficient computation must precede enable, and `intel_casf_needs_scaler()` must participate in scaler allocation before programming. Compile tests catch prototype drift; runtime tests should cover property-driven enable/disable, fast strength updates, scaler conflicts, and hardware readout.
