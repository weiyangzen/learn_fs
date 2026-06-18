# sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/regs-hdmi.h

## Purpose
This header defines the Samsung Exynos HDMI register map and bitfields used by `exynos_hdmi.c`. It covers HDMI 1.3 and 1.4 control/core/I2S/timing-generator regions, video timing, HPD/interrupts, PHY control/status, infoframe packets, ACR audio clock regeneration, HDCP register offsets, I2S audio routing/channel status, PHY mode-set values, PMU PHY control, and Exynos5433 sysreg refclk control.

## Important APIs, Types, and Functions
Address-space helpers `HDMI_CTRL_BASE()`, `HDMI_CORE_BASE()`, `HDMI_I2S_BASE()`, and `HDMI_TG_BASE()` compose offsets. Important groups include `HDMI_CON_*`, `HDMI_MODE_SEL`, `HDMI_*_BLANK`, `HDMI_*_SYNC*`, `HDMI_TG_*`, packet registers `HDMI_AVI_*`, `HDMI_AUI_*`, `HDMI_VSI_*`, ACR registers for v1.3/v1.4, I2S registers `HDMI_I2S_*`, HDCP offsets, `HDMIPHY*`, `PMU_HDMI_PHY_CONTROL`, and `EXYNOS5433_SYSREG_DISP_HDMI_PHY`.

## Control Flow
There is no executable flow. The HDMI driver uses these constants to disable IP HPD interrupts, choose HDMI or DVI mode, program infoframes, configure timing-generator registers for progressive/interlaced modes, set ACR N/CTS values, configure I2S audio, power/reset the PHY, and poll PHY-ready status.

## State and Persistence Behavior
The mapped registers persist hardware output state: mode selection, timing, infoframe transmit cadence, audio routing, PHY power, and HDCP-related blocks. The driver rewrites most of this state during encoder enable and mode application, and runtime PM may gate clocks around it.

## Dependencies and Integration Points
Direct consumer is `exynos_hdmi.c`. The macros tie together DRM display mode programming, HDMI infoframe helpers, sound HDMI codec callbacks, PMU/sysreg regmaps, APB/I2C PHY programming, and CEC/EDID hotplug behavior.

## Risks
The same semantic registers live at different offsets in HDMI 1.3 and 1.4, so `exynos_hdmi.c` maps selected registers through an indirection table; any missing mapped register can program the wrong generation. Several duplicate definitions exist, such as `HDMI_VACT_SPACE_6_0`, and unused HDCP offsets may be stale. I2S channel status values and word-length fields are easy to confuse because they mirror IEC status bytes. Timing-generator fields use low/high byte registers with 4-byte spacing, so write helper byte counts must match hardware expectations.

## Test Signals
Validate HDMI 1.3 and 1.4 modes, DVI/HDMI mode selection, infoframe transmission, ACR/I2S audio setup for 16/20/24-bit samples and common sample rates, PHY reset/ready polling, Exynos5433 refclk and mode-set behavior, interlaced timing, hotplug masking, and register dumps against hardware manuals.
