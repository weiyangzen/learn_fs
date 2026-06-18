# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/mtk_vcodec_dec_pm.c

## Purpose
This file implements decoder clock discovery, runtime power/clock gating, IRQ enable/disable, and inner-racing register snapshot management.

## Important APIs, Types, And Functions
`mtk_vcodec_init_dec_clk()` reads `clock-names`, obtains clocks, and stores them in `struct mtk_vcodec_pm`. Internal helpers power devices on/off with runtime PM, enable/disable clocks, and enable/disable IRQs for parent or subdevice hardware. `mtk_vcodec_dec_enable_hardware()` locks the selected hardware mutex, powers/clocks required blocks, enables IRQ, and loads racing info. `mtk_vcodec_dec_disable_hardware()` records racing info, disables IRQ, powers/clocks off, and unlocks.

## Control Flow
Probe initializes clocks. Before hardware execution, codec workers call enable for a hardware index. On LAT architecture, enabling CORE also powers LAT0; enabling LAT0 also powers LAT_SOC. After completion or error, workers call disable in reverse. Inner-racing capability snapshots/restores 132 registers when transitioning between zero and nonzero active decode count.

## State, Persistence, And Dependencies
State includes clock arrays, runtime PM usage counts, hardware mutexes, IRQ enable state, `dec_active_cnt`, `vdec_racing_info`, and `dec_racing_info_mutex`. It is runtime-only. Dependencies include Linux clocks, IRQ APIs, runtime PM, subdevice hardware state, and capability bits.

## Integration Points
Called by codec-specific decoder implementations around hardware access. Parent and subdevice probe use `mtk_vcodec_init_dec_clk()`.

## Risks
`mtk_vcodec_dec_clock_on()` logs errors but returns void, so callers cannot fail early after partial clock enable failure. PM get failures are logged but not propagated in child-on path. IRQ calls assume valid subdevice data. Racing snapshot offsets/count are hard-coded.

## Test Signals
Clock-name parsing failures, runtime PM errors, enable/disable nesting across hardware indexes, LAT/core dependency coverage, IRQ enable state, and inner-racing capability tests.
