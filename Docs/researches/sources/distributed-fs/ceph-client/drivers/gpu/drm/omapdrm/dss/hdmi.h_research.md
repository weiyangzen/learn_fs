<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/hdmi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/hdmi.h

## Purpose
`hdmi.h` is the private shared HDMI header for OMAP HDMI implementations. It defines wrapper, PLL, PHY, core audio/video configuration types, register offsets, power-state enums, register access helpers, function prototypes, and the top-level `struct omap_hdmi` state used by HDMI4 code and common HDMI helpers.

## Important APIs, types, and functions
The header names HDMI wrapper registers and IRQ bits, PLL control registers, and PHY registers. It defines enums for PLL and PHY power commands, HDMI versus DVI mode, packing modes, audio format details, audio transfer modes, audio layouts, CTS modes, and MCLK ratios. Major structures include `struct hdmi_config`, `struct hdmi_wp_data`, `struct hdmi_pll_data`, `struct hdmi_phy_data`, `struct hdmi_core_data`, `struct omap_hdmi`, and audio format/DMA/core config types. Inline helpers `hdmi_write_reg()`, `hdmi_read_reg()`, `REG_FLD_MOD()`, `REG_GET()`, and `hdmi_wait_for_bit_change()` provide low-level register access.

## Control flow
The header describes the layered flow used by `hdmi4.c`: wrapper initialization and video programming, PLL initialization and configuration, PHY initialization and lane parsing, core initialization and HDMI4-specific video/audio programming, audio callbacks, CEC integration, DRM bridge operation, and platform lifecycle management. It also exposes common wrapper, PLL, PHY, audio, and lane parsing functions implemented in companion files.

## State and persistence
`struct omap_hdmi` carries mutex-protected display and audio state, platform and DSS pointers, wrapper/PLL/PHY/core blocks, current HDMI config, regulator, core enable state, DSS output and DRM bridge, audio platform device, audio callbacks, idle mode, audio configuration cache, and spinlock-protected audio playback/display booleans. Hardware state persists in wrapper, PLL, PHY, and core registers until bridge disable, core disable, runtime suspend, or remove.

## Dependencies and integration points
The header integrates Linux platform IO, HDMI and CEC framework types, OMAP HDMI audio platform data, DRM bridge, OMAP DSS, and DSS PLL definitions. It is shared by HDMI4 driver code, HDMI core code, CEC code, and common wrapper/PLL/PHY helper implementations.

## Risks
Register offsets and bitfield helpers are a direct hardware ABI. Audio structures combine ALSA, CEA, HDMI wrapper, and core expectations, so changes can break audio silently. `struct omap_hdmi` has mixed mutex and spinlock state; lock ordering must stay consistent between bridge and audio callbacks. Wrapper IRQ masks include hotplug, PLL, video, and audio events, so incorrect masks can produce missed hotplug or audio FIFO faults.

## Test signals
Build coverage should include HDMI4 with and without CEC, HDMI audio, and all common HDMI helpers. Runtime signals include EDID reads, hotplug IRQs, HDMI versus DVI mode selection, AVI infoframe transmission, audio configuration/start/stop, CEC adapter operation, PLL/PHY power transitions, and debugfs register dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/hdmi.h -->
