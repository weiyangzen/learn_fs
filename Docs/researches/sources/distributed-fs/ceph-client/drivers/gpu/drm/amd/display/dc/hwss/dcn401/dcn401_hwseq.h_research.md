# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn401/dcn401_hwseq.h

## Purpose
`dcn401_hwseq.h` declares the DCN401 hardware sequencer surface consumed by DCN401 initialization and reused by later DCN generations such as DCN42. It exposes direct hardware programming functions and sequence-builder variants for the display core commit path.

## Important APIs and Types
- `enum ips_ono_state` and `struct ips_ono_region_state` describe ON/OFF/in-progress power-gating state for IPS/ONO-style regions, though the header only defines the types.
- Public hardware entry points include initialization, stream timing, stream enable/unblank, link disable, cursor position, bandwidth prepare/optimize/update, idle power optimization, ODM update, front-end programming, pipe reset, pipe change detection, and hardware release.
- Color and LUT APIs include `dcn401_program_gamut_remap()`, `dcn401_set_mcm_luts()`, `dcn401_set_output_transfer_func()`, `dcn401_populate_mcm_luts()`, and `dcn401_trigger_3dlut_dma_load()`.
- Sequence APIs mirror critical immediate operations: pipe programming, plane enable/disable, plane power-down/disconnect, blanking, writeback, GSL locking, MPCC updates, vupdate interrupt setup, HDR multiplier, MALL pipe config, p-state verification, and recovery.

## Control Flow and State Behavior
The header itself stores no state, but its signatures show the state model: most operations take `struct dc *`, `struct dc_state *`, `struct pipe_ctx *`, or `struct block_sequence_state *`. Immediate functions mutate hardware and software state directly; sequence functions append work into a `block_sequence_state` while sometimes updating software-visible fields such as pipe resource ownership.

## Dependencies and Integration Points
It includes DC core types, stream types, private and public sequencer declarations, and DCN401 DCCG definitions. It is included by `dcn401_init.c`, `dcn42_init.c`, and DCN42 hardware sequencing code, making DCN401 a base implementation layer for later ASICs.

## Risks and Test Signals
The main risk is API drift: the init dispatch tables rely on these prototypes matching function-pointer contracts in `hw_sequencer_funcs` and `hwseq_private_funcs`. Header-level validation comes from successful compilation across DCN401 and DCN42 configs, plus runtime coverage of both immediate and sequence paths where a declared helper is installed into a function table.
