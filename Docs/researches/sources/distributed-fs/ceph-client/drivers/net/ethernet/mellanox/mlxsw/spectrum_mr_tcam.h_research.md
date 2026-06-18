# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_mr_tcam.h

## Purpose
This small header exposes the TCAM multicast-routing backend to the generic MR core.

## Important APIs, Types, And Functions
It includes Spectrum and generic MR definitions and declares `extern const struct mlxsw_sp_mr_ops mlxsw_sp_mr_tcam_ops;`.

## Control Flow
Device initialization can pass `mlxsw_sp_mr_tcam_ops` to `mlxsw_sp_mr_init()` to select the TCAM/AFA implementation for multicast routing. The rest of the backend behavior is implemented in `spectrum_mr_tcam.c`.

## State And Persistence
The header declares no state. Runtime state is allocated by the backend's `.init` and per-route create callbacks.

## Dependencies And Integration Points
It is a bridge between files that want a generic `mlxsw_sp_mr_ops` provider and the TCAM backend implementation.

## Risks And Edge Cases
Any signature drift in `struct mlxsw_sp_mr_ops` must be reflected in the implementation, not this header. Missing inclusion where the backend is selected would break initialization at compile time.

## Test Signals
Build coverage and successful MR initialization with `mlxsw_sp_mr_tcam_ops` are the primary signals.
