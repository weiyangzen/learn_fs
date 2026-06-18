# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn351/dcn351_hwseq.c

## Purpose
`dcn351_hwseq.c` implements the small DCN351 override layer for hardware block gating and ONO sequencing. It reuses DCN35 calculations as a base, then enforces DCN351-specific contiguous HUBP/DPP gate and ungate behavior and custom power up/down order.

## Important APIs, types, and functions
The file defines `dcn351_calc_blocks_to_gate`, `dcn351_calc_blocks_to_ungate`, `dcn351_hw_block_power_down`, and `dcn351_hw_block_power_up`. Each operates on `struct dc`, `struct dc_state`, and `struct pg_block_update`.

## Control flow
The gate/ungate functions first call the DCN35 equivalent, then scan from the highest pipe down. When they find the first active HUBP/DPP pair that must remain powered or be powered, they force all lower-numbered HUBP/DPP entries to the same state. The power-down sequence walks pipes from high to low, gating DSC before paired HUBP/DPP, then gates the shared plane/OTG domain. The power-up sequence enables plane/OTG first, then walks low to high and ungates paired HUBP/DPP before DSC.

## State and persistence behavior
The functions mutate `pg_block_update` masks and live hardware power-gate state through `dc->res_pool->pg_cntl`. They honor `dc->debug.ignore_pg` and leave domains 22, 23, and 25 effectively always on according to comments.

## Dependencies and integration points
The implementation includes DC core/resource types, its own header, and `dcn35_hwseq.h`. It depends on DCN35 calculation semantics and on `pg_cntl` callbacks `dsc_pg_control`, `hubp_dpp_pg_control`, and `plane_otg_pg_control`. `dcn351_init.c` binds these overrides into the DCN351 public hwseq table.

## Risks and edge cases
The contiguous lower-pipe rule can intentionally keep more HUBP/DPP blocks powered than the base DCN35 calculation. This avoids invalid ONO sequencing but can reduce power savings. The high-to-low and low-to-high order must match DCN351 hardware requirements; changing it risks display hangs or power-domain violations. Missing `pg_cntl` callbacks silently skip parts of the sequence.

## Test signals
Test bandwidth optimize/prepare across pipe counts, DSC allocation changes, plane add/remove, sequential display bring-up/teardown, and `ignore_pg` debug mode. PG debug logs should show the expected DCN351 order and no underflow or register timeouts.
