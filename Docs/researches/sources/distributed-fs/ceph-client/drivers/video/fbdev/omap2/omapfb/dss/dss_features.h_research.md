# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/dss_features.h

## Purpose

This header declares the DSS feature identifiers, register-field identifiers, numeric-range identifiers, maximum DSS resource counts, and feature-query API implemented by `dss_features.c`. The complete 97-line header was read.

## Important APIs, Types, and Functions

Constants define `MAX_DSS_MANAGERS`, `MAX_DSS_OVERLAYS`, `MAX_DSS_LCD_MANAGERS`, and `MAX_NUM_DSI`. `enum dss_feat_id` lists hardware capabilities and quirks such as LCD enable polarity, line-buffer split, independent core clock divider, LCD clock source, DSI PLL power bug, DSI VC features, DPI `vdds_dsi` usage, HDMI CTS/audio MCLK, FIFO merge, burst 2D, DSI PHY DCC, and MFLAG. `enum dss_feat_reg_field` names SoC-specific bitfield layouts; `enum dss_range_param` names numeric limits for DSS fck, pixel clock divisor, DSI PLL LP divisor, DSI fck, downscale, and line width.

The declared API exposes feature presence, register field lookup, parameter min/max, supported displays/outputs, supported color modes, overlay caps, clock-source names, FIFO units, rotation support, and initialization by `omapdss_version`.

## Control Flow

There is no executable flow. Consumers include this header, call `dss_features_init()` during core setup, and then issue query calls throughout DSS, DISPC, DPI, DSI, and HDMI logic.

## State and Persistence Behavior

The header has no runtime state. It defines enum values that must stay in sync with the table indexes in `dss_features.c`.

## Dependencies and Integration Points

It depends on OMAP DSS public enums from `video/omapfb_dss.h` through users of the prototypes. It is the compile-time contract between capability tables and feature-gated hardware code in the DSS subtree.

## Risks and Edge Cases

Adding a feature id, register field, or range parameter requires updating every relevant per-SoC table. Mismatched enum/table ordering can produce incorrect register writes or limits. Resource maxima bound static arrays in the DSS core and DSI code, so increasing hardware support requires reviewing array users.

## Test Signals

Build all DSS configurations after enum changes, boot feature-table initialization on supported versions, and run targeted checks for each feature-gated path whose identifier is changed or added.
