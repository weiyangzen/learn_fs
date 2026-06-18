## sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_sdlb.c

### Purpose
`sparx5_sdlb.c` manages service dual leaky bucket groups used by PSFP flow meters and policers. It defines rate classes, computes token update intervals, and maintains per-group linked lists of active leaky buckets in hardware.

### Important APIs, Types, And Functions
Exports include `sdlb_groups`, `sparx5_get_sdlb_group()`, `sparx5_sdlb_clk_hz_get()`, `sparx5_sdlb_pup_token_get()`, `sparx5_sdlb_group_get_by_rate()`, `sparx5_sdlb_group_get_by_index()`, `sparx5_sdlb_group_add()`, `sparx5_sdlb_group_del()`, and `sparx5_sdlb_group_init()`. Internal helpers read first/next list links, detect empty/singular/first/last entries, and enable/disable PUP.

### Control Flow
Initialization computes each group's PUP interval from core clock, max token, and max rate, writes frame-rate tokens and threshold shift, and leaves groups ready for use. Group selection scans from low-rate groups upward in reverse index order, rejects full groups based on `pup_interval / 4 - 1`, and selects a group whose max rate exceeds requested rate. Add inserts an LB index at the head of the hardware list and enables the group; delete relinks around first, last, middle, or singular entries and disables the group if empty.

### State, Persistence, And Dependencies
Group metadata is stored in global `sdlb_groups[]` and augmented with computed `pup_interval` and `frame_size`. Active membership persists in ANA_AC_SDLB registers. Dependencies include core clock period helpers, generated SDLB register macros, chip ops, and constants in `sparx5_main.h`.

### Integration Points
PSFP flow meters use this file for group selection and list membership. Policer programming uses group intervals to compute PUP tokens. QoS initialization calls `sparx5_sdlb_group_init()` for each group.

### Risks
`sparx5_sdlb_group_get_count()` appears to return zero for a single-element group because it checks `itr == next` before incrementing; verify this against intended fullness logic. Linked-list operations depend on valid hardware state and can fail delete if membership is inconsistent. Global `sdlb_groups[]` is shared across devices.

### Test Signals
Test group initialization per core clock, token calculation for zero/nonzero rates, selection for boundary rates and full groups, add/delete head/middle/tail/singular cases, lookup by index, and PSFP police add/delete integration.
