# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/hdmi/hdmi_hpd.c

## Purpose
Provides HDMI hot-plug-detect control for MSM HDMI bridges: PHY reset during HPD setup, HPD interrupt enable/disable, IRQ processing, and connector detect using HPD registers and optional GPIO.

## Important APIs, types, and functions
- `msm_hdmi_hpd_enable()` powers the HDMI block, resets the PHY, enables HPD interrupts, and toggles the HPD circuit.
- `msm_hdmi_hpd_disable()` disables HPD interrupts, updates `hpd_enabled`, restores HDMI mode according to `power_on`, and drops runtime PM.
- `msm_hdmi_hpd_irq()` acknowledges HPD interrupt status, flips connect/disconnect interrupt polarity, and queues bridge HPD work.
- `msm_hdmi_bridge_detect()` reports connector status using `detect_reg()` and optional `detect_gpio()`.
- `msm_hdmi_phy_reset()` toggles software reset bits according to active-low/high polarity bits in `REG_HDMI_PHY_CTRL`.

## Control flow
HPD enable optionally drives the HPD GPIO high, resumes runtime PM, sets HDMI into detect mode under `state_mutex`, resets the PHY, marks HPD enabled, programs the reference timer and interrupt control, then toggles `HDMI_HPD_CTRL_ENABLE` under `reg_lock` to force a fresh sense. IRQ processing reads status/control, ignores disabled or unrelated interrupts, acknowledges the current interrupt, reprograms the next polarity based on cable state, and queues the bridge hotplug work. Detection retries up to 20 times for GPIO and register agreement, but trusts GPIO if they disagree.

## State and persistence
Persistent state is `hdmi->hpd_enabled`, `hdmi->power_on`, GPIO output state, runtime PM usage, and HPD/PHY controller registers. IRQ polarity persists in `REG_HDMI_HPD_INT_CTRL` until the next event. Detect reads do not cache connector state.

## Dependencies and integration points
Depends on DRM bridge callbacks, runtime PM, GPIO descriptors, HDMI register helpers, `hdmi->state_mutex`, `hdmi->reg_lock`, and `hdmi_bridge->hpd_work`. It is called from HDMI bridge HPD ops and connector detect paths.

## Risks
Detection can be delayed by the 20x10 ms retry loop. Runtime PM error paths call `pm_runtime_put()` even after failed resume in `detect_reg()`, so PM accounting assumptions matter. Register/GPIO disagreement is intentionally resolved in favor of GPIO, which can hide hardware HPD register issues. PHY reset polarity is hardware-specific.

## Test signals
Check hotplug connect/disconnect events, HPD interrupt status/control logs, detect behavior with and without HPD GPIO, runtime suspend/resume balance, and HDMI mode restoration after disabling HPD.
