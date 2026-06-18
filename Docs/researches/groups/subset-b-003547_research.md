# subset-b-003547 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/analogix/analogix-anx78xx.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/analogix/analogix-anx78xx.c

Purpose: I2C DRM bridge driver for Analogix ANX7808/7812/7814/7816/7818 SlimPort transmitters. It turns an HDMI/TMDS input into DisplayPort output, exposes a DRM connector, registers a DP AUX channel, and manages the chip's five I2C register pages.

Important APIs/types/functions: `struct anx78xx` stores the bridge, connector, AUX adapter, cached EDID, GPIO/regulator platform data, regmaps, chip ID, DPCD cache, mutex, and power flag. Probe is `anx78xx_i2c_probe`; remove is `anx78xx_i2c_remove`; bridge ops are `anx78xx_bridge_attach`, `mode_valid`, `mode_set`, `enable`, and `disable`; interrupt paths are `anx78xx_hpd_threaded_handler` and `anx78xx_intp_threaded_handler`; AUX is delegated through `anx78xx_aux_transfer` to `anx_dp_aux_transfer`.

Control flow: probe obtains DVDD10, HPD/powerdown/reset GPIOs, maps five dummy I2C clients, powers the chip, validates device ID/version, installs HPD and INTP threaded IRQs, adds the bridge, and powers off if HPD is low. Attach registers AUX, connector, helper functions, encoder link, and connector. Enable calls `anx78xx_start`, which powers TX/RX blocks, enables interrupts, initializes HDMI RX and DP TX, then asserts downstream HPD. HDMI clock/sync interrupts trigger `anx78xx_dp_link_training`; the hardware training-finish interrupt enables video output.

State and persistence: Runtime state is in-memory only: `powered`, cached `drm_edid`, DPCD capabilities, regmaps, and GPIO/IRQ handles. The mutex serializes mode setting, HPD/INTP interrupt handling, and EDID reads. EDID is cached until HPD lost or remove. No disk persistence exists.

Dependencies and integration: Depends on Linux I2C, regmap, regulator, GPIO, threaded IRQs, DRM bridge/connector/EDID helpers, HDMI AVI infoframe helpers, and DP AUX/DPCD helpers. Device-tree compatibles select ANX7808 versus ANX781x I2C address maps. The file includes `analogix-anx78xx.h`, which pulls in the shared I2C DP TX register definitions.

Risks: Power sequencing ignores some regmap errors during `anx78xx_poweron`; a failed regulator disable leaves `powered` true. Bridge attach rejects `DRM_BRIDGE_ATTACH_NO_CONNECTOR`, so it is not compatible with connectorless bridge chains. Link training relies on chip hardware and minimal post-failure recovery. IRQ handlers access hardware only under the mutex, but HPD loss powers off while other code may have already observed `powered`.

Test signals: Useful checks are probe on supported/unsupported IDs, HPD plug/unplug, EDID cache invalidation, AUX DPCD reads, mode rejection above 154 MHz or interlace, HDMI clock/sync interrupt causing link training, training-finish enabling video, and regulator/GPIO error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/analogix/analogix-anx78xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/analogix/analogix-anx78xx.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/analogix/analogix-anx78xx.h

Purpose: Register map header for the ANX78xx HDMI receiver and related TX page definitions used by `analogix-anx78xx.c`.

Important APIs/types/functions: It exports no functions or types. It includes `analogix-i2c-dptx.h` and `analogix-i2c-txcommon.h`, then defines RX_P0, RX_P1, and TX_P1 register addresses and bitfields for software reset, HDMI status, mute, power-down, audio/video auto control, interrupts, TMDS, video status, audio channel status, chip control, HDCP shadow/status, infoframes, control packets, DP TX link-training tuning, and firmware version.

Control flow: There is no executable control flow. The C driver uses these constants to reset HDMI RX blocks, mute/unmute audio/video, detect TMDS clock/data, configure TMDS PHY, send AVI infoframes, mask and clear HDMI interrupts, drive HPD output, and tune DP TX output emphasis.

State and persistence: The header names volatile hardware state only. Register bits reflect or control chip state across power transitions, but the header itself has no runtime memory. Cache and persistence decisions live in the C driver.

Dependencies and integration: Requires Linux `BIT()` definitions through including C files. It is part of the Analogix I2C bridge register namespace and deliberately composes with the DPTX and TX-common headers to cover the multiple I2C pages used by the chip.

Risks: Several definitions target undocumented or reserved hardware behavior, including an explicitly noted undocumented audio sample-change bit and register writes described in the C file as touching reserved bits. Wrong bit masks here can produce silent hardware bring-up failures, not compile-time failures.

Test signals: Compile coverage from `analogix-anx78xx.c`, register-trace comparison against datasheet sequences, interrupt mask/status behavior, AVI infoframe write locations, and TMDS clock/data detection are the practical validation points.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/analogix/analogix-anx78xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/analogix/analogix-i2c-dptx.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/analogix/analogix-i2c-dptx.c

Purpose: Shared AUX transaction helper for Analogix I2C-addressed DP transmitters. It converts DRM DP AUX messages into register writes on the DPTX I2C page.

Important APIs/types/functions: The exported API is `anx_dp_aux_transfer(struct regmap *map_dptx, struct drm_dp_aux_msg *msg)`. Internal helpers are `anx_dp_aux_address`, `anx_dp_aux_wait`, `anx_dp_aux_op_finished`, and `anx_i2c_dp_clear_bits`.

Control flow: `anx_dp_aux_transfer` validates the 16-byte AUX buffer limit, sets address-only or length fields, writes payload bytes for non-read operations, writes the 20-bit AUX address, programs AUX control register 1 with the request, starts the transaction via `SP_AUX_EN`, waits until hardware clears the enable bit, reads status, assigns ACK, bulk-reads data for read operations, clears address-only state, and returns the transferred byte count.

State and persistence: No persistent state is stored in the helper. It mutates only the chip's AUX address/control/data registers through the supplied regmap and modifies `msg->reply` and `msg->buffer`. Timeout state is local jiffies polling.

Dependencies and integration: Depends on regmap and DRM DP AUX request/reply definitions. It is used by `analogix-anx78xx.c` and any other I2C Analogix DPTX user that supplies a TX_P0 regmap.

Risks: All hardware failures collapse mostly to `-ETIMEDOUT` or raw regmap errors. The helper always reports I2C ACK after a clean status; it does not distinguish native AUX ACK from I2C ACK. It uses polling and `usleep_range`, so callers must be sleepable.

Test signals: Exercise native/I2C reads and writes, zero-length address-only transfers, maximum 16-byte payloads, oversized `-E2BIG`, timeout when `SP_AUX_EN` never clears, AUX status error handling, and data-buffer readback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/analogix/analogix-i2c-dptx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/analogix/analogix-i2c-dptx.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/analogix/analogix-i2c-dptx.h

Purpose: Register definitions and exported prototype for the TX_P0 DP transmitter page used by Analogix I2C bridge drivers.

Important APIs/types/functions: Defines HDCP status/control/key/timer registers, DP system-control bits, video/audio controls, packet send controls, link bandwidth/lane/training registers, polling/debug controls, AUX address/control/status/data registers, downspread and M calculation controls, and `ssize_t anx_dp_aux_transfer(...)`.

Control flow: No executable logic. The constants drive control flows in `analogix-anx78xx.c` and `analogix-i2c-dptx.c`: AUX setup, HDCP disabling/timer setup, link bandwidth/lane configuration, enhanced framing, training enable, downspread, packet send updates, and analog power-down.

State and persistence: The header names chip registers whose values persist only as hardware state while the chip is powered. Software persistence is handled by callers.

Dependencies and integration: Consumed with `regmap` accessors and DRM DP helpers. It pairs with `analogix-i2c-txcommon.h` and device-specific headers to cover all I2C pages.

Risks: Some field names encode chip-specific behavior such as hardware link training error codes and AUX status bits; incorrect interpretation can break link training or hide AUX failures. The prototype exposes only a regmap, so caller-side locking and power management are mandatory.

Test signals: Build coverage, AUX transfer behavior, link training register writes, downspread/DPCD compatibility, and HDCP register sequence validation are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/analogix/analogix-i2c-dptx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/analogix/analogix-i2c-txcommon.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/analogix/analogix-i2c-txcommon.h

Purpose: Common TX_P2 register definitions shared by Analogix I2C transmitter drivers.

Important APIs/types/functions: Defines device ID/version, power-down/reset controls, video controls and timing status registers, infoframe packet base registers, audio channel status controls, analog debug/clock-selection controls, common interrupt status/mask registers, DP interrupt status/mask, and interrupt control.

Control flow: There is no code flow. These constants are used to identify supported chips, power register/audio/video/link blocks, reset modules, set HPD output, program video mute/enable, write AVI infoframes, select XTAL timing, mask/clear HPD and DP training interrupts, and configure INT pin polarity.

State and persistence: Hardware-only state. The C driver controls this state during probe, power-on, link training, enable/disable, and interrupt handling.

Dependencies and integration: Included by `analogix-anx78xx.h`; depends on `BIT()` and standard integer usage from kernel includes. It is a low-level bridge between symbolic driver code and the ANX transmitter register map.

Risks: Power bits are active-high power-down controls, so inverted use can leave blocks off. Interrupt masks use device-specific semantics and must match the handler's status clearing. Clock-selection and timer constants affect AUX and HDMI timing stability.

Test signals: Confirm device ID reads, power transition register writes, HPD plug/lost interrupts, DP training-finish interrupt, video enable/mute toggles, and infoframe register offsets under hardware or regmap tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/analogix/analogix-i2c-txcommon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/analogix/analogix_dp_core.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/analogix/analogix_dp_core.c

Purpose: Shared DRM bridge core for MMIO-based Analogix DisplayPort/eDP controllers used by platform drivers such as Exynos and Rockchip. It handles AUX registration, HPD, link training, panel sequencing, video setup, PSR, CRC, runtime PM, and bridge binding.

Important APIs/types/functions: Exported APIs are `analogix_dp_probe`, `analogix_dp_suspend`, `analogix_dp_resume`, `analogix_dp_bind`, `analogix_dp_unbind`, `analogix_dp_start_crc`, `analogix_dp_stop_crc`, `analogix_dp_aux_to_plat_data`, and `analogix_dp_get_aux`. Internal major flows include `analogix_dp_full_link_train`, `analogix_dp_fast_link_train`, `analogix_dp_commit`, `analogix_dp_enable_psr`, `analogix_dp_disable_psr`, `analogix_dp_bridge_atomic_enable`, and `analogix_dpaux_transfer`.

Control flow: Probe allocates `struct analogix_dp_device`, parses platform data, gets optional PHY, clock, MMIO, HPD GPIO/IRQ, initializes AUX, and enables runtime PM. Resume powers clocks/platform/PHY and initializes hardware registers. Bind registers AUX and attaches the DRM bridge. Atomic enable prepares the panel, exits PSR if needed, sets mode-derived video info, detects HPD, trains the link, enables scrambling, configures video, enables the panel, detects fast training and PSR. Disable handles PSR transitions specially, otherwise disables panel/IRQ, powers analog blocks down, and drops runtime PM.

State and persistence: In-memory state includes connector, bridge, AUX, clock/IRQ/MMIO/PHY, video_info, link_train, DPMS mode, HPD force flag, fast-training and PSR flags, and platform data. There is no persistent storage. Link training state machines update `dp->link_train` during each enable.

Dependencies and integration: Depends on DRM bridge/connector/panel/EDID helpers, DP AUX/DPCD helpers, component-style platform drivers, runtime PM, clocks, PHY API, GPIO IRQs, and `analogix_dp_reg.c` register helpers. Platform callbacks in `analogix_dp_plat_data` provide SoC-specific power, attach, and mode hooks.

Risks: `pm_runtime_get_sync` return values are not always checked. Connectorless attach is rejected unless `skip_connector` is set through platform data behavior. Fast training has optional verification disabled by a static false. PSR state is tied to atomic self-refresh and can interact subtly with panel power and link retraining.

Test signals: Link training against sinks with different rates/lanes, HPD GPIO and MMIO interrupt paths, forced HPD eDP panels, EDID mode population, runtime suspend/resume, PSR enter/exit through self-refresh, CRC start/stop, and PHY configure failures are important signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/analogix/analogix_dp_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/analogix/analogix_dp_core.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/analogix/analogix_dp_core.h

Purpose: Internal core header for the MMIO Analogix DP bridge. It defines state structures, link/video enums, DPCD bit helpers, timeouts, and register-helper prototypes shared between the core and register implementation.

Important APIs/types/functions: Key types are `struct video_info`, `struct link_train`, and `struct analogix_dp_device`. Enums cover lane counts, training states, voltage swing, pre-emphasis, training patterns, color space/depth/coefficient, dynamic range, clock recovery M source, video timing source, analog power blocks, and HPD IRQ types. The prototype set exposes register operations for reset, AUX, HPD, training, video, scrambling, PSR, and transfer.

Control flow: No direct code, but it defines the state machine values consumed by `analogix_dp_core.c`: START, CLOCK_RECOVERY, EQUALIZER_TRAINING, FINISHED, and FAILED. It also defines timeout loop counts that bound HPD, PLL, training, and PSR waits.

State and persistence: `struct analogix_dp_device` is the central in-memory state object. It persists for device lifetime and contains bridge/connector/AUX objects, runtime resources, video settings, link training parameters, PHY, DPMS state, HPD flags, PSR/fast-training booleans, and platform data.

Dependencies and integration: Includes DRM DP helper, CRTC, and bridge headers and forward-declares GPIO. It is private to the Analogix DP implementation and its platform wrappers, not a public UAPI.

Risks: Struct layout and enum values are tightly coupled to register bit encodings. Timeout constants are global policy knobs; too short causes false failures, too long stalls modesets. Callers of register helpers must ensure runtime PM and clock/PHY power are active.

Test signals: Compile coverage across all platform drivers, full link-training state transitions, register-helper API consistency, and suspend/resume build coverage validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/analogix/analogix_dp_core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/analogix/analogix_dp_reg.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/analogix/analogix_dp_reg.c

Purpose: MMIO register access layer for Analogix DP controllers. It implements reset, power, interrupt, HPD, AUX, link-training, video, scrambling, and PSR packet helper operations used by `analogix_dp_core.c`.

Important APIs/types/functions: Major functions include `analogix_dp_reset`, `analogix_dp_init_analog_param`, `analogix_dp_init_interrupt`, `analogix_dp_set_analog_power_down`, `analogix_dp_init_analog_func`, `analogix_dp_init_aux`, `analogix_dp_transfer`, `analogix_dp_set_link_bandwidth`, `analogix_dp_set_lane_count`, `analogix_dp_set_lane_link_training`, `analogix_dp_set_training_pattern`, `analogix_dp_config_video_slave_mode`, `analogix_dp_is_video_stream_on`, and `analogix_dp_send_psr_spd`.

Control flow: Initialization resets video and function blocks, writes analog tuning, clears/masks interrupts, initializes HPD/AUX, powers analog blocks, and enables software/AUX functions. Link training helpers set bandwidth/lane registers, call optional PHY configuration, program lane voltage/pre-emphasis, training pattern, macro reset, and enhanced mode. AUX transfer clears the buffer, encodes request type and MOT, writes address/payload, starts hardware, polls for completion and reply, decodes defer/ACK, and resets AUX on error. Video helpers program color/timing, detect input clock/stream, and start output. PSR writes VSC SDP/header/payload registers and optionally polls sink PSR status.

State and persistence: The layer stores no independent software state; it mutates `dp->reg_base` registers and reads `dp->plat_data`, `video_info`, and `link_train`. Optional PHY state is configured through `phy_configure`.

Dependencies and integration: Depends on Linux MMIO `readl/writel`, `readx_poll_timeout`, PHY API, GPIO for HPD, DRM DP helper constants, and `analogix_dp_reg.h` bit definitions. It has Rockchip-specific branches selected by platform `dev_type`.

Risks: AUX request length macro computes `(x - 1)` and is used even for zero-size messages before `ADDR_ONLY`; hardware tolerance matters. Some helpers return after logging PHY configuration failures without propagating them. Rockchip and non-Rockchip power masks differ, so platform type errors can power down the wrong blocks. Polling timeouts can cause modeset latency.

Test signals: MMIO trace comparison, AUX native/I2C read/write/defer/error tests, PHY configure parameter assertions, link training on 1/2/4 lanes, video stream detection, HPD GPIO versus register mode, PSR enter/exit, and Rockchip/non-Rockchip reset paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/analogix/analogix_dp_reg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/analogix/analogix_dp_reg.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/analogix/analogix_dp_reg.h

Purpose: Register-offset and bitfield header for the MMIO Analogix DP controller.

Important APIs/types/functions: It exports no functions. It defines offsets for reset, function enable, video control, PLL/PHY/power, infoframe/PSR SDP, lane map, analog tuning, interrupt status/masks, system control, packet send, link training, AUX, M/N video, SOC general control, and CRC registers. It also defines masks and encoders for color format, lane mapping, AUX command/status, HPD/stream status, scrambling/training patterns, analog power blocks, and PSR CRC.

Control flow: Used by `analogix_dp_reg.c` to implement all hardware register operations. The macros encode how the core transitions between reset, powered AUX, link training, video slave mode, HPD interrupt handling, AUX transactions, and PSR packet send.

State and persistence: The header describes hardware state only. Register values persist in the controller while powered and are reinitialized by resume/enable paths.

Dependencies and integration: Private to the Analogix DP register implementation. The values must remain aligned with SoC integrations using `analogix_dp_plat_data` and platform `dev_type` checks.

Risks: Many masks are active-low function-enable or active-high power-down bits, making accidental inversion dangerous. Some aliases share bit positions for Rockchip versus generic IP. Mistyped register offsets can cause non-obvious display failures.

Test signals: Build coverage, register write traces during reset/link/video/AUX, Rockchip-specific path validation, and AUX error mapping are the main validation points.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/analogix/analogix_dp_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/analogix/anx7625.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/analogix/anx7625.c

Purpose: DRM bridge driver for Analogix ANX7625 MIPI DSI/DPI to DisplayPort/eDP bridge. It handles multi-address I2C access, power sequencing, firmware readiness, AUX/EDID, MIPI timing programming, HPD, optional downstream panel bridge, Type-C status, HDCP 1.4, audio codec registration, and runtime PM.

Important APIs/types/functions: Probe/remove are `anx7625_i2c_probe` and `anx7625_i2c_remove`. Bridge ops include attach/detach, mode_valid, mode_set, atomic_check/enable/disable, detect, EDID read, and HPD enable/disable. Key helpers include `anx7625_aux_trans`, `anx7625_dsi_config`, `anx7625_dpi_config`, `anx7625_power_on_init`, `anx7625_intr_status`, `anx7625_edid_read`, `anx7625_hdcp_enable`, `anx7625_register_audio`, `anx7625_typec_register`, and `anx7625_link_bridge`.

Control flow: Probe checks SMBus block capability, allocates bridge state, gets regulators/GPIOs, initializes mutexes/workqueues/AUX, parses DT input bus and panel, sets up DSI when needed, creates seven dummy I2C clients, enables runtime PM, populates AUX bus or links a bridge directly, initializes HPD for non-low-power mode, registers Type-C/audio, enables IRQ work, and returns. Atomic enable polls HPD, starts DP output, programs MIPI DSI or DPI based on mode timing, and optionally starts HDCP work. Disable flushes HDCP work, updates content protection, stops DP, and runtime-suspends. IRQ work clears interface interrupts, updates Type-C roles, handles HPD transitions, adjusts swing, invalidates EDID, and emits DRM HPD events.

State and persistence: `struct anx7625_data` stores platform data, dummy clients, last I2C client workaround state, cached EDID, HPD status/counter, DP enable flag, HDCP content-protection state, connector pointer, DSI device, Type-C role, workqueues, and locks. EDID is cached until HPD low or runtime suspend without panel bridge. No disk persistence exists.

Dependencies and integration: Depends on I2C/SMBus, regulators, GPIO, runtime PM, DRM bridge/panel/DP AUX/EDID/HDCP helpers, MIPI DSI, DP AUX bus population, Type-C/USB role switch, HDMI codec, V4L2 fwnode bus type parsing, and display timing helpers.

Risks: Large state surface with multiple locks (`lock`, `aux_lock`, `hdcp_wq_lock`) and workqueues makes PM/disable/AUX races important. Several register sequences OR return codes and continue after partial failure. EDID reading is custom 16-byte AUX-over-I2C logic. HDCP state is updated asynchronously after a fixed delay. Remove unconditionally unregisters Type-C even when no connector child registered, so null handling depends on Type-C helpers tolerating it.

Test signals: Probe deferral order, DSI and DPI modes, low-power versus always-on power paths, HPD IRQ and polling paths, AUX transfer under runtime PM, EDID cache invalidation, panel-on-AUX-bus behavior, audio hw_params for I2S/TDM, Type-C role/orientation updates, HDCP desired/enabled transitions, and mode fixup edge cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/analogix/anx7625.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/analogix/anx7625.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/analogix/anx7625.h

Purpose: Private header for the ANX7625 driver, defining register addresses, bitfields, timing constants, audio enums, and driver state structures.

Important APIs/types/functions: Key definitions include I2C page addresses, reserved-address workaround offsets, PLL limits, TCPC/status/interrupt bits, HDCP registers, DP TX timing/audio/swing registers, flash/OCM/firmware registers, AP AUX registers, MIPI PLL/PHY/timing registers, DPCD offsets, audio sample-rate and word-length enums, `struct anx7625_platform_data`, `struct anx7625_i2c_client`, `struct fw_msg`, and `struct anx7625_data`.

Control flow: The header drives code paths in `anx7625.c`: dummy client registration, I2C access workaround, OCM firmware checks, power/HPD configuration, AUX transactions, DSI/DPI timing programming, mode fixup constraints, EDID limits, HDCP key loading, audio channel setup, Type-C status updates, and runtime state handling.

State and persistence: `struct anx7625_data` is the persistent in-memory device state for the driver's lifetime. It contains locks, workqueues, cached EDID, content-protection status, HPD counters, Type-C/audio/DSI/bridge/AUX objects, and I2C clients. Hardware register state is volatile and reinitialized on power/runtime PM transitions.

Dependencies and integration: Uses kernel DRM, I2C, Type-C, USB role, HDMI codec, regulator, GPIO, MIPI DSI, and display timing types through the C file. It is not a public interface.

Risks: The header contains many magic values and duplicated/overlaid register meanings. Typos in constants have runtime-only symptoms. State fields such as `hpd_high_cnt`, `dp_en`, and `connector` are shared across workqueue, bridge, and PM paths and require locking discipline in C code.

Test signals: Compile coverage, DT property parsing, register sequence traces, DSI/DPI timing programming, audio format mapping, AUX/EDID boundaries, HDCP key offsets, and Type-C status bit decoding validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/analogix/anx7625.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/aux-bridge.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/aux-bridge.c

Purpose: Auxiliary-bus helper that creates a transparent DRM bridge device used to fill a bridge-chain position and attach to the next DT-described bridge.

Important APIs/types/functions: Exported API is `drm_aux_bridge_register(struct device *parent)`. Internal state is `struct drm_aux_bridge_data` with the DRM bridge, next bridge, and device pointer. Auxiliary driver probe is `drm_aux_bridge_probe`; bridge attach is `drm_aux_bridge_attach`.

Control flow: Registration allocates an `auxiliary_device`, assigns an ID through `IDA`, names it `aux_bridge`, inherits the parent's OF node, initializes and adds it, and installs a devm cleanup action that deletes/uninitializes it. Probe allocates bridge data, resolves the next bridge with `devm_drm_of_get_bridge(..., port 0, endpoint 0)`, sets passthrough format allowances, and devm-adds the bridge. Attach requires `DRM_BRIDGE_ATTACH_NO_CONNECTOR` and attaches the next bridge after itself.

State and persistence: The IDA tracks allocated auxiliary IDs. The auxiliary device owns OF-node references and is freed in release. Bridge state is devm-managed and has no persistent storage.

Dependencies and integration: Depends on Linux auxiliary bus, OF node lifetime rules, DRM bridge helpers, and `drm/bridge/aux-bridge.h`. Intended for parent drivers that need a simple bridge placeholder.

Risks: Only connectorless chains are supported. OF node reference management must match auxiliary device init/add failure paths. The bridge performs no validation or mode ops, so downstream bridge behavior carries most display constraints.

Test signals: Register/unregister cleanup on parent detach, deferred next-bridge probe, attach with and without NO_CONNECTOR, IDA reuse, and OF refcount leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/aux-bridge.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/aux-hpd-bridge.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/aux-hpd-bridge.c

Purpose: Auxiliary-bus helper for a terminal DisplayPort HPD DRM bridge that can notify hotplug events for bridge chains without a full downstream bridge driver.

Important APIs/types/functions: Exported APIs are `devm_drm_dp_hpd_bridge_alloc`, `devm_drm_dp_hpd_bridge_add`, `drm_dp_hpd_bridge_register`, and `drm_aux_hpd_bridge_notify`. Internal state is `struct drm_aux_hpd_bridge_data`. Probe creates a bridge with `DRM_BRIDGE_OP_HPD` and connector type from auxiliary ID driver data.

Control flow: Allocation creates an auxiliary device named `dp_hpd_bridge`, stores an OF node in platform data, inherits parent OF node, initializes the auxiliary device, and ties uninit to devm cleanup. Add registers the auxiliary device and ties delete to devm cleanup. Probe allocates bridge data, sets bridge OF node, HPD ops, connector type, passthrough allowances, stores driver data, and devm-adds the bridge. Notify converts the device to its auxiliary driver data and calls `drm_bridge_hpd_notify`.

State and persistence: IDA IDs and OF references live for auxiliary-device lifetime. Bridge driver data is devm-managed. No persistent storage exists.

Dependencies and integration: Depends on auxiliary bus, OF, DRM bridge HPD notification, and aux-bridge public helpers. Parent drivers use the returned device to report HPD status from their own detection logic.

Risks: `drm_aux_hpd_bridge_notify` is a no-op before probe driver data exists, so early notifications may be dropped. Only NO_CONNECTOR attach is allowed. Correct OF-node ownership is split between `dev.of_node` and `platform_data`.

Test signals: Allocation/add cleanup paths, HPD notification before/after probe, attach flag validation, connector type propagation, and OF refcount checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/aux-hpd-bridge.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/cadence/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/cadence/Kconfig

Purpose: Kconfig menu for Cadence DRM bridge drivers under the bridge/cadence directory.

Important APIs/types/functions: Defines `DRM_CDNS_DSI`, `DRM_CDNS_DSI_J721E`, `DRM_CDNS_MHDP8546`, and `DRM_CDNS_MHDP8546_J721E`. The DSI option selects KMS helper, MIPI DSI, panel bridge, generic PHY, generic MIPI DPHY, and videomode helpers, and depends on OF. The MHDP8546 DP option selects DP, HDCP, display, KMS, and panel bridge helpers, and depends on OF. J721E wrappers default to `y` under their parent options, with the DP wrapper limited to `ARCH_K3 || COMPILE_TEST`.

Control flow: Kconfig controls compile-time inclusion. Enabling parent symbols exposes the child wrapper options and drives Makefile object composition.

State and persistence: No runtime state. Persistent effect is kernel configuration.

Dependencies and integration: Integrates Cadence DSI and MHDP8546 bridge drivers with DRM, PHY, OF, panel bridge, DP/HDCP helpers, and TI K3/J721E wrappers.

Risks: Selects force helper dependencies on when the bridge is enabled; missing architecture constraints on the parent options may expose compile-test-only paths. Default-y wrapper symbols can include platform wrapper code whenever the parent is enabled.

Test signals: `allyesconfig`, `allmodconfig`, `COMPILE_TEST`, OF-disabled builds, parent-only versus wrapper-enabled builds, and module dependency checks validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/cadence/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/cadence/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/cadence/Makefile

Purpose: Build rules for Cadence DRM bridge drivers.

Important APIs/types/functions: Builds `cdns-dsi.o` when `CONFIG_DRM_CDNS_DSI` is enabled, with `cdns-dsi-core.o` always included and `cdns-dsi-j721e.o` included when `CONFIG_DRM_CDNS_DSI_J721E` is enabled. Builds `cdns-mhdp8546.o` when `CONFIG_DRM_CDNS_MHDP8546` is enabled, with core and HDCP objects always included and J721E wrapper object conditional on `CONFIG_DRM_CDNS_MHDP8546_J721E`.

Control flow: Kbuild combines per-driver composite objects according to Kconfig symbols. There is no runtime control flow.

State and persistence: No runtime state. Persistent effect is the object list included in a kernel build.

Dependencies and integration: Directly mirrors `cadence/Kconfig` symbols and integrates Cadence DSI and MHDP8546 source files into the DRM bridge build.

Risks: Object-list drift from Kconfig or source-file renames causes build failures. Composite object naming must match module expectations.

Test signals: Build each parent as built-in and module, toggle J721E child symbols, and run clean incremental builds to catch stale object dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/cadence/Makefile -->
