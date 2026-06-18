# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/hdmi/hdmi.h

Purpose: shared internal header for MSM HDMI transmitter, bridge, audio, DDC, HDCP, PHY, and PLL code. It defines device state containers, platform config contracts, register access helpers, PHY abstractions, and cross-file function prototypes.

Important APIs and types:
- `struct hdmi_audio` stores enabled/rate/channel state used by audio register programming.
- `struct hdmi` is the central device object with DRM, platform, power, MMIO, PHY, DDC, connector/bridge, encoder, workqueue, HDCP, mutex, and spinlock state.
- `struct hdmi_platform_config` lists regulator and clock names for HDMI core power.
- `struct hdmi_bridge` wraps `drm_bridge` and hotplug work.
- `enum hdmi_phy_type`, `struct hdmi_phy_cfg`, and `struct hdmi_phy` describe HDMI PHY variants and resources.
- Inline helpers `hdmi_write/read`, `hdmi_qfprom_read`, `hdmi_phy_write/read` centralize MMIO access.

Control flow: HDMI submodules include this header and collaborate through `struct hdmi`. The top-level driver fills resources, bridge code drives power/timing/infoframes, audio code reads/writes audio fields, DDC/HDCP modules attach through prototypes, and PHY files implement the declared PHY/PLL functions.

State and persistence: persistent state is all in `struct hdmi` and `struct hdmi_phy`. `state_mutex` protects `power_on` and `hpd_enabled`; `reg_lock` protects several shared HDMI registers across interrupt/work/atomic contexts. The header also defines compile-time HDCP and common-clock stubs so callers can use uniform functions when features are disabled.

Dependencies and integration points: includes Linux I2C, clock, platform, regulator, GPIO, HDMI definitions, DRM bridge, MSM driver definitions, and generated `hdmi.xml.h` register definitions. Exposes hooks to ALSA HDMI codec bridge callbacks and DRM bridge HPD/detect flows.

Risks: inline QFPROM read has no NULL guard, so callers must ensure resource availability. The `hdmi_phy` field `cfg` is non-const despite extern const configs, which can invite accidental mutation. Locking rules are documented but not enforced by types. Feature stubs return `-ENODEV` or no-op and must be handled by callers.

Test signals: compile with and without `CONFIG_COMMON_CLK` and `CONFIG_DRM_MSM_HDMI_HDCP`, sparse/lockdep attention around `reg_lock` and `state_mutex`, and cross-module build coverage for HDMI audio, bridge, DDC, HDCP, PHY, and PLL files.
