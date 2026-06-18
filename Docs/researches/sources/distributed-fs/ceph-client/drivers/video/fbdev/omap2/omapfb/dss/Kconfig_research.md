# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/Kconfig

## Purpose

`dss/Kconfig` defines configuration symbols for the legacy OMAP2 DSS fbdev subsystem. The complete 111-line file was read. It selects required helpers, exposes optional debug/debugfs/IRQ-stat features, and gates hardware output blocks such as DPI, VENC, SDI, DSI, and HDMI variants.

## Important APIs, Types, and Functions

Important symbols include `FB_OMAP2_DSS_INIT`, `FB_OMAP2_DSS`, `FB_OMAP2_DSS_DEBUG`, `FB_OMAP2_DSS_DEBUGFS`, `FB_OMAP2_DSS_COLLECT_IRQ_STATS`, `FB_OMAP2_DSS_DPI`, `FB_OMAP2_DSS_VENC`, `FB_OMAP2_DSS_HDMI_COMMON`, `FB_OMAP4_DSS_HDMI`, `FB_OMAP5_DSS_HDMI`, `FB_OMAP2_DSS_SDI`, `FB_OMAP2_DSS_DSI`, `FB_OMAP2_DSS_MIN_FCK_PER_PCK`, and `FB_OMAP2_DSS_SLEEP_AFTER_VENC_RESET`.

## Control Flow

This is build-time control flow. Enabling `FB_OMAP2_DSS` selects `VIDEOMODE_HELPERS`, `FB_OMAP2_DSS_INIT`, and `HDMI`; sub-options determine which objects the Makefile adds and which code paths are compiled. Debugfs and IRQ statistics are nested so IRQ stats are available only when debugfs support is enabled.

## State and Persistence Behavior

Kconfig values persist in the kernel `.config` and drive compile-time feature selection. Runtime behavior is affected by these symbols but the file itself owns no runtime state.

## Dependencies and Integration Points

The file feeds `dss/Makefile` object selection and `#ifdef CONFIG_FB_OMAP2_DSS_*` branches across DSS sources. `FB_OMAP2_DSS_MIN_FCK_PER_PCK` is used by DISPC divisor selection to constrain functional clock to pixel clock ratio.

## Risks and Edge Cases

Defaults enable DPI, VENC, and OMAP4 HDMI when the parent is enabled, which can expand build surface. `FB_OMAP2_DSS` is a tristate but many child outputs are bools, so module/built-in combinations need build coverage. The integer clock ratio can make otherwise valid display timings fail if set too high.

## Test Signals

Signals include allmodconfig/allyesconfig builds, minimal DSS builds, debugfs and IRQ-stat build variants, HDMI4/HDMI5 separate builds, and runtime validation that selected output drivers are registered or omitted as expected.
