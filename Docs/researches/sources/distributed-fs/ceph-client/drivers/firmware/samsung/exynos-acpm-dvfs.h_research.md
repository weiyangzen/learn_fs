# sources/distributed-fs/ceph-client/drivers/firmware/samsung/exynos-acpm-dvfs.h

## Purpose
This private header declares ACPM DVFS helper functions used by the core ACPM ops setup.

## Important APIs
- `acpm_dvfs_set_rate(struct acpm_handle *handle, unsigned int acpm_chan_id, unsigned int id, unsigned long rate)`
- `acpm_dvfs_get_rate(struct acpm_handle *handle, unsigned int acpm_chan_id, unsigned int clk_id)`

## Control Flow And Integration
`exynos-acpm.c` assigns these functions to `acpm->handle.ops.dvfs_ops`, exposing them to ACPM protocol clients through the public firmware protocol handle.

## State And Persistence
No state is owned by the header. The implementation changes or reads firmware-managed DVFS state.

## Risks
The header is private to the composite object; public consumers should use the protocol ops rather than include this file.

## Test Signals
Build failures involving DVFS ops setup or missing prototypes point to this interface.
