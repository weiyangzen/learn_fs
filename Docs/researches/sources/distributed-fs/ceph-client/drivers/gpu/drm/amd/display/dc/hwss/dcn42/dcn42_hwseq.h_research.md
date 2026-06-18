# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn42/dcn42_hwseq.h

## Purpose
`dcn42_hwseq.h` declares the DCN42-specific hardware sequencer deltas that are installed by `dcn42_init.c`. It keeps the DCN42 public surface small because most behavior is inherited from DCN401 and earlier generations.

## Important APIs
The header declares DCN42 init, MPCC update, color histogram programming, MCM/RMCM LUT programming, hardware release, bandwidth prepare/optimize, power-gating mask calculation, block power up/down, root-clock control, DMUB hardware lock helpers, stereo setup, and boot power-down.

## Control Flow and State Behavior
The declarations show the DCN42 state model: functions operate on `struct dc`, `struct dc_state`, `struct pipe_ctx`, `struct dc_plane_state`, `struct dc_plane_cm`, `struct hubp`, `struct mpc`, and `struct pg_block_update`. PG helpers split calculation from execution, allowing prepare/optimize code to compute a power transition mask and then apply root-clock and block power operations.

## Dependencies and Integration Points
It includes `dc.h` and `hw_sequencer_private.h`, so it is tied to the DC core and private sequencer contracts. Its functions are consumed by `dcn42_init.c` and may be invoked through generic `dc->hwss` or `dc->hwseq->funcs` pointers.

## Risks and Test Signals
API risk is mostly around keeping declarations synchronized with the function tables and implementation. Compile coverage validates signatures. Runtime coverage should exercise DCN42-specific PG, RMCM, MPCC, stereo, DMUB lock, and boot power-down paths rather than only inherited DCN401 behavior.
