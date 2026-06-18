# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dsc/dscc_types.h

## Purpose

`dscc_types.h` defines the small DSC calculation interface between AMD DC register-preparation code and DRM DSC PPS structures. It adds hardware-programming data that is not part of the raw PPS.

## Important APIs, Types, And Functions

It defines `NUM_BUF_RANGES` when absent, `struct dsc_pps_rc_range`, `struct dsc_parameters`, forward-declares `struct rc_params`, and declares `dscc_compute_dsc_parameters`.

## Control Flow

There is no runtime flow in the header. Callers build a DRM `drm_dsc_config`, calculate `struct rc_params`, call `dscc_compute_dsc_parameters`, and receive a possibly adjusted PPS plus `bytes_per_pixel` and RC buffer model size for register programming.

## State, Dependencies, Risks, And Test Signals

All state is caller-owned stack or heap data. The interface has no persistent storage and no hardware side effects by itself. It depends on `<drm/display/drm_dsc.h>` and is used by DCN DSC backends after `calc_rc_params`. Risks include ABI mismatch with DRM DSC config fields, incorrect `NUM_BUF_RANGES`, and callers misreading the nonzero return as success. Tests should validate RC threshold/range propagation, bytes-per-pixel units, and invalid PPS error paths.
