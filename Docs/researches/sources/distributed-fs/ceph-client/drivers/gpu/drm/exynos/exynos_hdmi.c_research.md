# sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_hdmi.c

## Purpose
This file implements the Exynos HDMI encoder, connector, PHY programming, hotplug, EDID/DDC, CEC notifier, bridge attachment, runtime PM, and HDMI audio codec integration. It supports several Exynos HDMI IP variants with different register maps, PHY programming tables, clock gates/muxes, APB or I2C PHY access, PMU/sysreg controls, and timing programming paths.

## Important APIs, Types, and Functions
Key data structures are `struct hdmi_context`, `struct hdmi_driver_data`, `struct hdmiphy_config`, `struct hdmiphy_configs`, `struct string_array_spec`, and `struct hdmi_audio`. Variant tables include Exynos4210, Exynos4212, Exynos5420, and Exynos5433 driver data and PHY configuration arrays. The exported platform driver is `hdmi_driver`.

Important functions include `hdmi_probe()`, `hdmi_remove()`, `hdmi_bind()`, `hdmi_create_connector()`, `hdmi_get_modes()`, `hdmi_mode_valid()`, `hdmi_mode_fixup()`, `hdmi_enable()`, `hdmi_disable()`, `hdmiphy_enable()`, `hdmiphy_disable()`, `hdmiphy_conf_apply()`, `hdmi_conf_apply()`, `hdmi_v13_mode_apply()`, `hdmi_v14_mode_apply()`, `hdmi_irq_thread()`, `hdmi_register_audio_device()`, and HDMI codec callbacks for hw params, mute, shutdown, and ELD.

## Control Flow
Probe allocates context, loads variant data, initializes resources, maps HDMI registers, gets DDC and PHY access, requests GPIO HPD IRQ, obtains PMU/sysreg regmaps, enables an optional `hdmi-en` regulator, enables runtime PM, initializes default audio infoframe fields, registers the HDMI audio codec, and joins the component framework. Bind initializes a TMDS encoder, sets possible CRTCs, locates the HDMI Exynos CRTC, assigns a `pipe_clk` callback that controls the HDMI PHY, and creates the HDMI connector.

Connector probing reads EDID over DDC when available, updates connector display info and CEC physical address, detects DVI mode from EDID, or falls back to 640x480 no-EDID modes. Mode validation requires an exact pixel-clock match in the selected PHY table. Enabling the encoder powers and configures the PHY, initializes HDMI/DVI mode, audio, infoframes, and timing registers, then starts the timing generator. HPD GPIO interrupts schedule debounced hotplug work. Runtime suspend/resume gates HDMI clocks.

## State and Persistence Behavior
`hdmi_context` persists device resources, connector state, bridge, CEC notifier, clock/regulator handles, audio parameters, and a `powered` flag protected by `mutex`. PHY and HDMI core registers are reprogrammed on enable and mode set. Audio parameters and mute state persist in software and are applied when powered. The CEC physical address is updated from EDID and invalidated on disconnect/disable. Runtime PM controls clock gates, while `hdmiphy_enable()` controls regulators, PMU PHY enable, sysreg refclk, PHY power, and clock parent switching.

## Dependencies and Integration Points
The file depends on DRM connector/encoder/bridge/EDID helpers, Exynos CRTC pipe-clock hooks, GPIO descriptors, I2C DDC, optional I2C or APB HDMI PHY access, regmap syscon for PMU/sysreg, regulator bulk APIs, clock framework, runtime PM, CEC notifier, sound `hdmi-codec`, and register definitions in `regs-hdmi.h`. It is registered by the Exynos DRM driver when HDMI support is enabled and is paired with the mixer CRTC for TV output.

## Risks
Mode validation requires exact pixel clocks from static PHY tables, so otherwise valid EDID modes with close clocks are rejected. `hdmiphy_reg_write_buf()` returns raw short-write values from `i2c_master_send()`, which may be positive but still treated as an error by callers. `hdmiphy_enable()` logs but ignores regulator bulk enable failure, then continues to power/configure the PHY. `hdmi_disable()` cancels hotplug work and invalidates CEC but deliberately does not power down when `powered` is true, relying on the mixer/pipe clock sequencing; this coupling must be preserved. The file as present contains a duplicated function parameter line in `hdmi_audio_hw_params()` and a duplicated debug string in `hdmi_mode_valid()`, which are strong build-review signals. Resource cleanup must balance DDC adapter, I2C PHY client, APB PHY iounmap, bridge, audio platform device, regulators, and runtime PM.

## Test Signals
Build with all Exynos HDMI variants, boot with Exynos4210/4212/5420/5433 compatible data, test DDC EDID and no-EDID fallback, HPD debounce, DVI versus HDMI infoframe behavior, CEC physical address updates, bridge attachment, mode validation for all PHY-table clocks, interlaced and progressive modes, suspend/resume, regulator/clock failure paths, audio hw_params/mute/ELD, and combined mixer enable/disable sequencing.
