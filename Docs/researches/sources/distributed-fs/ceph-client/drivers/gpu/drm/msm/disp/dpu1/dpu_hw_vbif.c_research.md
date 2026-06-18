# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_vbif.c

## Purpose
Implements the VBIF hardware wrapper for memory-interface error clearing, memory type, outstanding transaction limits, halt control, QoS remap, and write gather enable.

## Important APIs, types, and functions
- `dpu_hw_vbif_init()` constructs the VBIF wrapper.
- `dpu_hw_clear_errors()` reads pending/source error registers and clears them.
- `dpu_hw_set_mem_type()` programs AXI AMEMTYPE fields per XIN client.
- `dpu_hw_set_limit_conf()` and `dpu_hw_get_limit_conf()` set/read read or write outstanding limits.
- `dpu_hw_set_halt_ctrl()` and `dpu_hw_get_halt_ctrl()` control XIN halt.
- `dpu_hw_set_qos_remap()` programs both RP and level remap tables when supported.
- `dpu_hw_set_write_gather_en()` enables write gather per XIN.

## Control flow
Initialization installs core ops and only exposes QoS remap if the catalog feature bit is set. Limit configuration computes register and byte field from XIN ID and read/write direction. Memory type supports up to 16 XINs across two registers. QoS remap computes register group from XIN high bit and priority level, then updates matching nibbles in both remap table families.

## State and persistence
Wrapper state is catalog pointer, MMIO base, and ops. VBIF programming persists in memory-interface registers and affects all display clients until reconfigured or reset.

## Dependencies and integration points
Depends on catalog VBIF feature data, `MAX_XIN_COUNT`, register helpers, and DPU VBIF policy code (`dpu_vbif.c`) that calls these ops from plane/QoS paths and runtime resume.

## Risks
Many helpers do limited argument validation; XIN IDs beyond supported hardware can produce bad bit shifts in limit/halt paths. QoS remap depends on catalog `qos_rp_remap_size`. Because VBIF is shared, incorrect settings can cause underruns, hangs, or memory ordering/performance problems across all active pipes.

## Test signals
Signals include underrun absence under bandwidth stress, correct OT/QoS debug behavior, VBIF error counters clearing, runtime resume reprogramming, and register snapshots for limit/remap/memtype/halt registers.
