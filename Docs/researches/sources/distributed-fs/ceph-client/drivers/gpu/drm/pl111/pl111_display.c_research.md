# sources/distributed-fs/ceph-client/drivers/gpu/drm/pl111/pl111_display.c

## Purpose
Implements PL111 simple display pipe behavior: IRQ/vblank handling, mode validation, atomic check, enable/disable/update, pixel clock divider, format-to-control programming, and display pipe initialization.

## Important APIs, Types, and Functions
Public functions are `pl111_irq()` and `pl111_display_init()`. Internal display callbacks include `pl111_mode_valid()`, `pl111_display_check()`, `pl111_display_enable()`, `pl111_display_disable()`, `pl111_display_update()`, vblank enable/disable helpers, and `pl111_display_funcs`. Clock helpers implement `clk_ops` through `pl111_clk_div_choose_div()`, determine/recalc/set rate, and `pl111_init_clock_divider()`.

## Control Flow
IRQ handling reads masked IRQ status, handles `CLCD_IRQ_NEXTBASE_UPDATE` as vblank, clears IRQs, and returns handled status. Atomic check enforces 16-pixel horizontal granularity, dword-aligned framebuffer base, pitch equal to mode width times cpp, and mode changes for framebuffer format changes. Enable sets pixel clock, programs TIM0/TIM1/TIM2/TIM3 from mode timings and connector/bridge bus flags, selects grayscale/TFT mode, maps DRM formats to PL111/ST/PL110 control bits, enables LCD, waits for voltage stabilization, calls variant enable hook, powers LCD, and enables vblank if available. Update writes the upper base address and arms/sends page-flip events. Disable turns vblank off, powers down, waits, calls variant disable, clears control, and disables the clock.

## State and Persistence
Persistent state is in `pl111_drm_dev_private`: MMIO registers, selected control/IRQ offsets, connector/bridge/panel pointers, variant data/hooks, pixel clock/divider, and `tim2_lock`. Hardware state persists in CLCD timing/control/base/IRQ registers while enabled. CRTC event state is consumed on update.

## Dependencies and Integration Points
Depends on DRM simple KMS, GEM DMA framebuffer helpers, vblank/event handling, DRM format definitions, common clock framework, media bus formats, OF graph-discovered connector/bridge data, and PL111 private register definitions. Variant hooks allow board-specific display enable/disable and ST/PL110 bit routing.

## Risks and Edge Cases
TIM2 is shared between clock framework and display enable, requiring `tim2_lock`. Format routing differs between ARM PL110/PL111 and ST variants; BGR inversion is easy to regress. Broken clockdivider and broken vblank variants need fallback behavior. Bridge setup-time compensation toggles pixel clock edge. Pitch is constrained by absent pitch register. Bandwidth validation depends on `memory_bw` and default framebuffer depth.

## Test Signals
Signals include modeset on PL110/PL111/ST variants, vblank/page-flip events, framebuffer format matrix, grayscale bus format output, clock divider rate accuracy, bridge edge compensation, bandwidth rejection, suspend/disable power sequencing, and debugfs/timing register inspection after modeset.
