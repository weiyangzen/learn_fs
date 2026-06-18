# sources/distributed-fs/ceph-client/drivers/video/fbdev/aty/radeon_pm.c

## Purpose

`radeon_pm.c` implements Radeon framebuffer power management. It controls dynamic clocking, prepares chips for low-power suspend states, saves/restores hardware registers, handles D2 sleep and selected D3-cold reinitialization paths, wires into the PCI `dev_pm_ops`, and applies machine-specific workarounds for PowerMacs and selected x86 laptops. It is tightly coupled to `radeon_base.c`, which initializes PM after probe and uses the exported PM ops from the PCI driver.

## Important APIs, Types, And Functions

Public entry points are `radeonfb_pm_init()`, `radeonfb_pm_exit()`, and `radeonfb_pci_pm_ops`. x86 workaround data is represented by `struct radeon_device_id` and `radeon_workaround_list`, where subsystem IDs can OR PM capabilities into `rinfo->pm_mode` and replace `rinfo->reinit_func`.

Dynamic-clock control is split between `radeon_pm_disable_dynamic_mode()` and `radeon_pm_enable_dynamic_mode()`, with separate paths for R100/RV100/RV350/R300/mobility/IGP families. PM register preservation uses `radeon_pm_save_regs()` and `radeon_pm_restore_regs()` over the fixed `rinfo->save_regs[100]` array. Low-power preparation helpers include `radeon_pm_disable_iopad()`, `radeon_pm_program_v2clk()`, `radeon_pm_low_current()`, and `radeon_pm_setup_for_suspend()`. Memory-controller and PLL reinit helpers include `INMC()`, `OUTMC()`, DLL enable functions, `radeon_pm_full_reset_sdram()`, `radeon_pm_reset_pad_ctlr_strength()`, `radeon_pm_all_ppls_off()`, `radeon_pm_start_mclk_sclk()`, spread-spectrum helpers, and pixel PLL restoration.

Chip-specific D3-cold reinitializers include `radeon_reinitialize_M10()` for RV350/M10/M11 style chips and PPC-only `radeon_reinitialize_M9P()` for M9+ PowerMac hardware. A large `radeon_reinitialize_QW()` implementation exists under `#if 0` as incomplete reference code.

## Control Flow

`radeonfb_pm_init()` records dynamic-clock policy, immediately enables/disables dynamic clocks when requested, detects PowerMac capabilities from OF node names, marks D2 or D3-cold resume support, registers platform wake capability, applies x86 subsystem workarounds unless suppressed, and honors `force_sleep` by enabling D2. `radeonfb_pm_exit()` tears down the old PPC early-resume hook when applicable.

Suspend enters through `radeonfb_pci_suspend_late()`. Freeze/prethaw do not power down hardware. For real suspend/hibernate, it locks the console, marks fbdev suspended, idles/resets the accelerator, blanks the display, sets `asleep` and `lock_blank`, deletes the LVDS timer, suspends PMAC AGP if needed, and saves a full register context if D3-cold resume is supported. Mobility chips without D2 support receive explicit LVDS shutdown. If D2 is supported, `radeon_set_suspend(..., 1)` disables dynamic mode, saves registers, programs V2CLK, disables pads, selects low-current settings, sets suspend clock/power registers, disables PCI, saves PCI state, repeatedly forces PCI D2 until it sticks, and calls platform power transition.

Resume enters `radeonfb_pci_resume()`. It locks the console, checks for D3-cold power loss by comparing key saved PLL registers against live hardware, invokes `rinfo->reinit_func` when required, or resumes from D2 with `radeon_set_suspend(..., 0)`. After hardware wake, it writes the saved display mode registers-only, reinitializes the accelerator, restores pan offset and cmap, clears fbdev suspend, unblanks, resumes PMAC AGP, reapplies dynamic-clock policy, and marks the PCI device ON.

## State And Persistence

PM state lives in `rinfo->dynclk`, `rinfo->pm_mode`, `rinfo->reinit_func`, `rinfo->save_regs[100]`, `rinfo->asleep`, `rinfo->lock_blank`, and `rinfo->no_schedule`. The saved register array is an implicit ABI inside this file; many indices have family-specific meanings. PM also relies on `rinfo->state` from `radeon_base.c` to restore the programmed mode after resume. PCI power state is tracked through `pdev->dev.power.power_state` and `pdev->current_state`; no state persists across driver unload.

## Dependencies And Integration Points

The file depends on Radeon MMIO/PLL helpers from `radeonfb.h`, PCI PM APIs, fbdev suspend APIs, console locking, AGP backend headers, optional PPC PMAC features, OF node naming, and subsystem IDs from `ati_ids.h`. It calls accelerator reset/init functions indirectly through base resume flow and expects `radeon_screen_blank()` and `radeon_write_mode()` from `radeon_base.c` to be available. PowerMac integration uses `pmac_suspend_agp_for_card()`, `pmac_resume_agp_for_card()`, and `pmac_call_feature()`.

## Risks

The most important risk is ordering: clock, PLL, memory-controller, LVDS, and PCI power transitions are register-sequence sensitive and family-specific. `save_regs` uses numeric slots rather than named structure fields, so duplicate slot use or family-dependent interpretation can cause subtle resume breakage; slot 96 is assigned both an R300 MC value and later `HDP_DEBUG` depending on path. Several sequences include magic constants copied from firmware traces. D2 entry loops until the PCI PM state bit matches the target and sleeps 500 ms each iteration, so bad hardware could hang suspend. `radeonfb_pci_resume()` can return early without completing if `no_schedule` is set and `console_trylock()` fails. D3-cold resume without a reinit function returns `-EIO` and leaves display recovery to soft reboot. Dynamic clocking changes can interact with DRI or active rendering if not fully quiesced.

## Test Signals

Testing should cover boot/probe with `default_dynclk=-2,-1,0,1`, `ignore_devlist`, and `force_sleep`; suspend/resume, hibernate/restore, and freeze/thaw; D2-capable mobility chips; D3-cold reinit paths for M10/M11 and M9+ where hardware is available; resume after simulated power loss; console-lock early resume behavior; LVDS panel blank and unblank after resume; framebuffer content and cmap restoration; accelerator reset/init after resume; and logs for dynamic clock enable/disable and workaround detection. Static validation should verify every `save_regs` index is intentionally assigned and read for the target family.
