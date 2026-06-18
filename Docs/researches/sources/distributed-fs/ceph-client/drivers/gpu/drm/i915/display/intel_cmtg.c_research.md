# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_cmtg.c

## Purpose

`intel_cmtg.c` handles inherited Common Primary Timing Generator state. The current driver does not actively use CMTG, but firmware or pre-OS code may leave it enabled. This file reads a minimal CMTG configuration and disables CMTG when it can do so without requiring a modeset, so later display sanitization does not leave unsupported timing-generator topology active.

## Important APIs, Types, And Functions

The only public function is `intel_cmtg_sanitize()`. The private `struct intel_cmtg_config` records whether CMTG A and B are enabled and whether transcoder A or B is in CMTG secondary mode. `intel_cmtg_has_cmtg_b()` gates the second CMTG on display version 20 and newer. `intel_cmtg_has_clock_sel()` gates CMTG clock selection register handling on display version 14 and newer. `intel_cmtg_transcoder_is_secondary()` safely reads `TRANS_DDI_FUNC_CTL2` under the transcoder power domain. `intel_cmtg_get_config()` reads CMTG enable and secondary-mode state. `intel_cmtg_disable_requires_modeset()` blocks no-modeset disable on pre-display-version-20 systems if any transcoder is secondary. `intel_cmtg_disable()` clears secondary-mode bits, disables CMTG A/B, and marks their clock selections disabled when supported.

## Control Flow

`intel_cmtg_sanitize()` first exits if `HAS_CMTG(display)` is false. Otherwise it reads current CMTG state, logs it, and checks whether disabling requires a modeset. On older platforms, a secondary transcoder implies modeset-sensitive state, so the function returns and leaves CMTG untouched. On platforms that can be disabled safely, it clears secondary mode for transcoders A/B if present, clears `CMTG_ENABLE` on CMTG A and B, and updates `CMTG_CLK_SEL` to disabled values for the affected CMTGs.

The function must run before any port PLL is disabled in broader sanitization because CMTG registers may depend on the port PLL currently supplying the CMTG clock.

## State And Persistence

There is no persistent software state. The local config is a one-time readout snapshot. Hardware state persists in `TRANS_CMTG_CTL_A/B`, `TRANS_DDI_FUNC_CTL2` secondary-mode bits, and `CMTG_CLK_SEL`. The code intentionally avoids tracking enabled CMTG as an ongoing driver-managed feature.

## Dependencies And Integration Points

The file depends on display version/platform macros, `HAS_CMTG()`, display power-domain helpers, register accessors from `intel_de.h`, transcoder register definitions, and CMTG register definitions from `intel_cmtg_regs.h`. It is part of display sanitization and must be ordered before PLL shutdown.

## Risks

The main risk is disabling timing topology while a transcoder still depends on it. The code mitigates this by refusing the pre-D20 case where secondary mode implies a modeset is required, but the FIXME notes that the driver lacks full CMTG state tracking and synchronized modeset disable. Another risk is register access with power domains disabled; `intel_cmtg_transcoder_is_secondary()` uses `with_intel_display_power_if_enabled()` to avoid forcing domains on just for readout. Future platforms with additional CMTGs or transcoders would need this minimal A/B logic extended.

## Test Signals

Test signals include boot/sanitize logs showing inherited CMTG state, systems where firmware leaves CMTG enabled, display version 13/14/20 platform coverage, and verification that CMTG is disabled only when safe. MMIO traces should show `TRANS_CMTG_CTL_A/B`, `TRANS_DDI_FUNC_CTL2`, and `CMTG_CLK_SEL` updates. Regression tests should watch for blank screens or modeset failures after sanitization.
