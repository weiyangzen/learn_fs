# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/hdmi.h

## Purpose

This header defines the shared internal HDMI contract for OMAP DSS HDMI drivers. It provides wrapper, PLL, and PHY register offsets, IRQ bits, HDMI/video/audio enums and structs, MMIO helpers, wrapper/PLL/PHY/common/audio function prototypes, and the aggregate `struct omap_hdmi` state used by HDMI4. The complete 360-line header was read.

## Important APIs, Types, and Functions

Important defines include HDMI wrapper registers (`HDMI_WP_*`), IRQ flags (`HDMI_IRQ_*`), PLL control registers (`PLLCTRL_*`), and PHY registers (`HDMI_TXPHY_*`). Enums describe PLL and PHY power commands, HDMI vs DVI mode, packing mode, audio channel/type/justification/sample order/sample size/transfer/layout/CTS/MCLK settings.

Important structs are `hdmi_video_format`, `hdmi_config`, `hdmi_audio_format`, `hdmi_audio_dma`, `hdmi_core_audio_i2s_config`, `hdmi_core_audio_config`, `hdmi_wp_data`, `hdmi_pll_data`, `hdmi_phy_data`, `hdmi_core_data`, and `omap_hdmi`. Inline helpers are `hdmi_write_reg()`, `hdmi_read_reg()`, `REG_FLD_MOD`, `REG_GET`, `hdmi_wait_for_bit_change()`, and `hdmi_mode_has_audio()`.

The prototypes cover wrapper video/IRQ/PHY/PLL/audio DMA operations, PLL compute/init/uninit, PHY configure/init/lane parsing, OF lane parsing, ACR computation, and HDMI audio programming.

## Control Flow

The header has no standalone runtime flow. HDMI4 code initializes `omap_hdmi.wp`, `.pll`, `.phy`, and `.core`, then calls wrapper/PLL/PHY/core helpers through these declarations during power-on, audio setup, EDID reads, IRQ handling, and debug dumps.

## State and Persistence Behavior

No state is stored in the header. It defines state containers used at runtime: MMIO bases, physical DMA address, PHY lane function/polarity, current HDMI config, regulator/core/display/audio flags, child audio platform device, audio config cache, and locks for audio/display coordination.

## Dependencies and Integration Points

It depends on Linux IO/delay/platform headers, HDMI infoframe types, OMAP DSS public types, OMAP HDMI audio pdata, and internal DSS helpers. It integrates HDMI wrapper, PLL, PHY, common parsing, audio, and HDMI4/HDMI5 core code behind a common state and register helper API.

## Risks and Edge Cases

The polling helper waits up to about 10 ms and returns the last observed value, so callers must compare carefully. Register helpers assume valid MMIO bases and bitfield ranges. `struct omap_hdmi` mixes mutex-protected display state and spinlock-protected audio playback state; users must follow the documented lock split. Enum values are hardware encodings, so renumbering is unsafe.

## Test Signals

Build HDMI4/HDMI5 with audio enabled, exercise wrapper register dumps, PLL/PHY init and power transitions, OF lane parsing, HDMI vs DVI mode audio gating, audio DMA address setup, ACR calculation, and IRQ bit handling.
