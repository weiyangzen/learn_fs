# sources/distributed-fs/ceph-client/drivers/gpu/ipu-v3/ipu-di.c

## Purpose
Implements Display Interface timing generation for IPUv3. It programs pixel clocks, sync waveforms, data pins, polarities, and panel timing registers for DI0/DI1.

## Important APIs, Types, and Functions
`struct ipu_di` stores ID, use count, clocks, IPU pointer, module bit, and MMIO base. `struct di_sync_config`, `enum di_pins`, and sync wave enums describe waveform generation. Exported APIs include `ipu_di_adjust_videomode()`, `ipu_di_init_sync_panel()`, `ipu_di_enable()/disable()`, `ipu_di_get_num()`, `ipu_di_get()/put()`, `ipu_di_init()/exit()`. Core helpers are `ipu_di_sync_config()`, interlaced/noninterlaced sync builders, `ipu_di_config_clock()`, and pin/data-wave configuration routines.

## Control Flow
Clients acquire a DI, optionally adjust a videomode to hardware constraints, call `ipu_di_init_sync_panel()` with signal config, then enable the DI pixel clock. Sync-panel setup locks a global mutex, configures clock source/divider, generates waveforms for H/V sync, data enable, and interlaced fields, sets polarity and data-ready behavior, and writes DI_GENERAL. Enable prepares/enables the chosen pixel clock; disable unprepares it.

## State and Persistence
Per-DI state includes selected `clk_di_pixel`, use count, and MMIO timing registers. `di_mutex` serializes global timing programming, while `ipu_di_lock` protects get/put use counts. Clock rates may be changed via `clk_set_rate()`, affecting shared clock tree state beyond this driver.

## Dependencies and Integration Points
Depends on Linux clk, videomode structures, IPU module enable/disable, and display clients that provide `struct ipu_di_signal_cfg`. It integrates directly with DC through DI IDs and with panel/bridge drivers through mode timing and polarity.

## Risks
Clock divisor selection is sensitive to pixel-clock limits and parent rates; rounding can produce modes outside display tolerance. Interlaced waveform generation has many derived offsets and counters. Global locking prevents concurrent programming but not bad sequencing by callers. `WARN_ON(IS_ERR(di->clk_di_pixel))` indicates enable/disable assumes successful prior initialization.

## Test Signals
Mode validation should cover low/high pixel clocks, external clock flags, interlaced and progressive modes, polarity variants, and DI0/DI1 concurrency. Scope or display-controller measurements of HSync/VSync/data-enable timing are the strongest hardware validation.
