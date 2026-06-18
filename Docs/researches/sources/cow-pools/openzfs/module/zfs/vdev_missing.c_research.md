# File Research: sources/cow-pools/openzfs/module/zfs/vdev_missing.c

## Purpose
Defines placeholder leaf vdev types used when a pool configuration refers to a device that is missing or a top-level hole. These are primarily import-time constructs that let the kernel parse and instantiate the rest of the vdev tree even though the pool should ultimately fail validation.

## Main Responsibilities
- Provide a minimal open routine for missing/hole vdevs.
- Reject all I/O with `ENOTSUP`.
- Export separate operation vectors for `missing` and `hole` vdev types.

## Key Entry Points
- `vdev_missing_open()`: pretends to open successfully with zero size and zero shifts.
- `vdev_missing_close()`: no-op close.
- `vdev_missing_io_start()`: sets `io_error` to `ENOTSUP` and executes the ZIO.
- `vdev_missing_io_done()`: no-op completion.
- `vdev_missing_ops`: leaf ops for `VDEV_TYPE_MISSING`.
- `vdev_hole_ops`: leaf ops for `VDEV_TYPE_HOLE`.

## Important Semantics
`vdev_missing_open()` deliberately returns success instead of failing. The comment explains this preserves the desired later failure mode: a GUID sum mismatch with `VDEV_AUX_BAD_GUID_SUM`, rather than prematurely faulting the root vdev as having no replicas.

## Data and State
The implementation stores no private state. All size and shift outputs from open are set to zero.

## Dependencies
Depends only on generic vdev ops, ZIO execution, and default size conversion helpers.

## Edge Cases and Failure Handling
All I/O is unsupported. These vdevs exist to keep config parsing and import diagnostics coherent, not to serve data.
