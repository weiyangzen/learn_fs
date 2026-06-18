# sources/distributed-fs/ceph-client/drivers/gpu/drm/xlnx/zynqmp_dp.h

## Purpose

`zynqmp_dp.h` declares the ZynqMP DisplayPort bridge/control API used by platform, KMS, and audio code.

## Important APIs, Types, And Functions

It forward declares `struct zynqmp_dp` and `struct zynqmp_dpsub`, and declares probe/remove, vblank enable/disable, audio channel enable/disable, and audio N/M programming helpers.

## Control Flow

No runtime flow exists in the header.

## State And Persistence Behavior

No state is owned by the header; all operations act on `struct zynqmp_dp` created by `zynqmp_dp_probe()`.

## Dependencies And Integration Points

It connects `zynqmp_dpsub.c`, `zynqmp_kms.c`, and `zynqmp_dp_audio.c` to the DP implementation.

## Risks And Test Signals

Risk is signature drift across display, KMS, and audio call sites. Build coverage with audio enabled and disabled validates the contract.
