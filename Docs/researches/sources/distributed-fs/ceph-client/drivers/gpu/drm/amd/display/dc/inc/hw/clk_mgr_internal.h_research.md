# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/clk_mgr_internal.h

## Purpose

`clk_mgr_internal.h` defines private clock-manager register macros, internal structures, and helper predicates. It maps ASIC-specific clock registers/fields, stores SMU and DFS-bypass state, and provides low-level helpers used by clock-manager implementations.

## Important APIs, Types, And Functions

Important macros include `TO_CLK_MGR_INTERNAL`, `CLK_SRI`, register-list macros for DCE/DCN generations, mask/shift-list macros, and field-list macros. Types include `clk_mgr_registers`, `clk_mgr_shift`, `clk_mgr_mask`, `enum clock_type`, `state_dependent_clocks`, `clk_mgr_internal`, and `clk_mgr_internal_funcs`. Inline helpers are `should_set_clock`, `should_update_pstate_support`, `khz_to_mhz_ceil`, and `khz_to_mhz_floor`. External helpers count active displays and planes.

## Control Flow

ASIC implementations instantiate register/mask/shift tables through the macros, cast the public manager to `clk_mgr_internal`, and use `should_set_clock` to decide whether to raise or lower clocks in each commit phase. Internal function pointers set DISPCLK/DPREFCLK. Helper counters examine `dc_state` when deriving clock requirements or power policy.

## State And Persistence Behavior

`clk_mgr_internal` extends `clk_mgr` with SMU version, SMU callbacks, DCCG pointer, register tables, max clocks by state, DFS-bypass status, spread-spectrum metadata, xGMI state, current clock states, PHY clock request table, watermark table address, DPM/PME flags, and SMU presence. This state persists for the DC instance.

## Dependencies And Integration Points

It includes the public clock manager, `dc.h`, and `resource.h` for memory type definitions. It integrates tightly with ASIC register headers, SMU/PPLIB, DCCG, link PHY clock requests, DPM tables, and DC logging.

## Risks And Edge Cases

Register-list macros are generation-specific and easy to desynchronize from hardware headers. `should_set_clock` encodes a two-phase safety policy; misuse can lower clocks early. Spread-spectrum and xGMI handling affects DPREFCLK and audio/display clocks. The internal struct is not ABI-stable and should remain private to clock-manager implementations.

## Test Signals

Builds catch missing register symbols and field names for each ASIC. Runtime tests should cover all supported clock-manager generations, DFS bypass, DPREFCLK spread-spectrum, active display/plane counts, safe-to-lower sequencing, PHY clock request updates, and DPM/PMFW interactions.
