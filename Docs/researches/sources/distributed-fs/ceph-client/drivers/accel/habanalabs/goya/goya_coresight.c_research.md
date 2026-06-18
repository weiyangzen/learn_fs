# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/goya/goya_coresight.c

## Purpose

`goya_coresight.c` implements Goya-specific debug/CoreSight programming for STM, ETF, ETR, funnel, bus monitor, and SPMU blocks. It translates generic `struct hl_debug_params` operations from the Habanalabs debug interface into direct register writes against Goya block base addresses, and provides a halt path that disables trace sinks during context/reset cleanup.

## Important APIs, Types, And Data

- Static base-address tables map debug enum indices to Goya register bases: `debug_stm_regs[]`, `debug_etf_regs[]`, `debug_funnel_regs[]`, `debug_bmon_regs[]`, and `debug_spmu_regs[]`.
- `goya_coresight_timeout()` wraps `hl_poll_timeout()` with a longer timeout under PLDM and logs the failing address/bit/direction.
- Config functions include `goya_config_stm()`, `goya_config_etf()`, `goya_config_etr()`, `goya_config_funnel()`, `goya_config_bmon()`, and `goya_config_spmu()`.
- `goya_etr_validate_address()` restricts ETR trace buffers to the device DRAM MMU virtual range.
- `goya_debug_coresight()` is the exported dispatcher used by `goya_funcs.debug_coresight`.
- `goya_halt_coresight()` disables all ETF blocks and ETR for cleanup/reset.

## Control Flow

The dispatcher examines `params->op` and calls the matching config helper. STM configuration unlocks the block, programs masks, IDs, timestamp frequency, and enable bits; disable clears masks, waits for not-busy state, and leaves the block disabled. ETF/ETR flows first unlock and detect no-op enable/disable state, flush/stop existing capture through FFCR-style bits, wait for drain/ready state, then either program sink mode and enable or clear registers and disable. ETR enable validates nonzero buffer size and checks the buffer address/size against DMMU bounds before programming the 40-bit address registers; disable can return the write pointer through `params->output`.

Funnel configuration simply unlocks and writes an enable mask. BMON configuration programs address windows, capture settings, ID routing, and a PCIe-specific workaround offset when enabled; disable restores broad masks/defaults and clears the block. SPMU enable validates 3 to 6 event types, writes event selectors, and enables counters. SPMU disable validates output space, reads event counters, overflow, and cycle count, then clears overflow state.

After every debug operation, `goya_debug_coresight()` performs a PCIe device ID register read to flush posted configuration writes. `goya_halt_coresight()` iterates all ETF indices with a zeroed `params` structure, then disables ETR and logs failures without aborting the whole halt sequence.

## State And Persistence Behavior

CoreSight state is persisted in hardware registers, not in driver-owned memory. Enable operations program capture masks, sink modes, event selectors, trace buffer addresses, IDs, and routing; disable operations clear the same register sets and may sample output counters or ETR write pointer. PLDM mode stretches timeouts by multiplying the base CoreSight timeout. The code assumes `params->input` and `params->output` point to operation-specific structs/buffers managed by the caller.

## Dependencies And Integration Points

This file depends on `goyaP.h`, Goya CoreSight enum definitions, ASIC register and mask headers, the debug UAPI, and generic register access macros. It is wired into the main ASIC vtable by `goya.c` through `.debug_coresight = goya_debug_coresight` and `.halt_coresight = goya_halt_coresight`. It also depends on ASIC properties such as `hdev->pldm`, `hdev->asic_prop.psoc_timestamp_frequency`, `hdev->asic_prop.dmmu`, and `hdev->asic_prop.fw_security_enabled`.

## Risks And Edge Cases

- Register index bounds checks are the primary protection against invalid enum input; mismatched enum/table ordering would program the wrong block.
- ETR address validation only checks DMMU virtual range and overflow; callers must ensure the backing memory is mapped and suitable for trace writes.
- `goya_config_spmu()` computes `events_num = output_arr_len - 2` before validating `output_arr_len >= 3`; because these are unsigned values, too-small buffers underflow locally before the later check. The function returns `-EINVAL`, but this ordering is fragile.
- Posted writes are flushed only once in the dispatcher; direct helper use would miss that flush.
- Disable paths often reset registers to magic constants. These values are hardware-specific and need regression coverage when registers or masks change.

## Test Signals

Tests should cover each debug op with valid and invalid `reg_idx`, missing input on enable, missing/too-small output on disable, ETR zero-size and out-of-range buffers, PLDM timeout scaling, SPMU event count bounds, ETF/ETR timeout errors, halt behavior across all ETF entries, and the final register-read flush after successful or failed configuration.
