# subset-b-004083 research

Grouped research for the source files in `subset-b-004083`. Each section is source-tree aligned and bounded for reconciliation into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/adv7604.c -->
## sources/distributed-fs/ceph-client/drivers/media/i2c/adv7604.c

### Purpose

`adv7604.c` is a V4L2 I2C subdevice driver for the Analog Devices ADV7604, ADV7610/ADV7611, and ADV7612 HDMI/DVI/component video receiver family. It exposes a media entity with multiple sink pads for HDMI and, on ADV7604, analog VGA/component inputs, plus one source pad carrying decoded video. The driver handles input routing, DV timing detection and programming, output bus format selection, EDID RAM management, hotplug control, cable/power-present reporting, optional CEC, HDMI infoframe debugfs access, and interrupt-driven source-change notification.

### Important APIs, Types, And Data

The driver centers on `struct adv76xx_state`, which owns chip metadata, platform data, GPIOs, the `v4l2_subdev`, media pads, controls, selected input, active timings, active media-bus format, EDID storage, source physical-address bytes, RGB quantization state, delayed HPD work, CEC adapter/address state, per-page I2C clients, and regmaps. `struct adv76xx_chip_info` describes per-chip capabilities and register differences: AFE presence, maximum port, EDID registers, interrupt masks, timing masks, format tables, termination callbacks, HDMI pixel-clock readers, cable-detect readers, register-page mask, and recommended register sequences.

The public integration surface is the V4L2 subdev operation tables: `adv76xx_core_ops` provides status logging, ISR dispatch, event subscription, and optional debug register access; `adv76xx_video_ops` provides `.s_routing` and `.g_input_status`; `adv76xx_pad_ops` provides media-bus format enumeration/get/set, EDID get/set, DV timings query/get/set/cap/enumeration, and selection/crop reporting. Probe registers the I2C driver under the `adv7604` driver name and supports I2C IDs for `adv7604`, `adv7610`, `adv7611`, and `adv7612`, plus OF matches for the ADV761x variants.

Register access is abstracted through one regmap per ADV76XX page. Helpers such as `io_read()`, `hdmi_write_clr_set()`, `cp_read16()`, `rep_write_clr_set()`, and `edid_write_block()` target the chip's IO, HDMI, CP, repeater, EDID, CEC, AFE, infoframe, and other register maps. `adv76xx_dummy_client()` creates ancillary I2C clients for these pages and writes their shifted addresses into the IO map.

### Control Flow

Probe validates SMBus byte-data support, allocates state, selects chip metadata from OF or platform data, requests HPD/reset GPIOs, optionally pulses reset, initializes default 640x480 timings and YUYV8 bus format, then creates the IO regmap and verifies the chip ID. It creates V4L2 controls for brightness, contrast, saturation, hue, volatile IT content type, power-present, RGB quantization, analog sampling phase when an AFE exists, and free-run color. After creating ancillary I2C clients and regmaps, it initializes media pads, calls `adv76xx_core_init()`, requests a threaded IRQ when present, allocates optional CEC, and registers the async subdev.

`adv76xx_core_init()` programs power, output pads, video format, color-space conversion, signal polarities, drive strength, free-run behavior, audio mute policy, AFE setup, HPD policy, and interrupt enables. If a default input is configured, it calls `select_input()` and `enable_input()` around the input mode. Routing goes through `adv76xx_s_routing()`: it validates the requested pad, updates `selected_input`, disables current output/termination, applies analog or HDMI recommended settings, enables the new path, and emits a `V4L2_EVENT_SOURCE_CHANGE` event.

DV timing detection starts with `adv76xx_query_dv_timings()`. It rejects no-signal states, reads STDI/SSPD via `read_stdi()`, then either decodes HDMI register timing and pixel clock or maps analog STDI data through known presets, CVT, and GTF detection in `stdi2dv_timings()`. For unreliable analog STDI reads it performs a one-shot STDI restart using `restart_stdi_once`. `adv76xx_s_dv_timings()` validates requested timings against analog/digital caps, stores them, configures interlace state, chooses predefined prim-mode/video-std registers when possible, otherwise writes custom timing registers, and reapplies RGB quantization.

EDID flow is managed by `adv76xx_set_edid()` and `adv76xx_get_edid()`. Setting EDID disables HPD and EDID DDC access, validates or synthesizes the source physical address, writes per-port SPA registers, patches port A bytes into the EDID image, copies EDID into state, writes up to four 128-byte blocks into EDID RAM through segment selection, waits up to roughly one second for the repeater enable status, updates CEC physical address, and schedules delayed HPD re-enable. Clearing EDID removes the port bit, disables HPD for that port, resets aspect ratio to 16:9 when appropriate, and invalidates CEC physical address when no EDID remains.

Interrupt handling is split between the threaded IRQ wrapper and `adv76xx_isr()`. The ISR reads and clears IO status registers, detects CP/STDI/SSPD and digital format changes, sends V4L2 source-change events, handles HDMI/DVI mode changes by recomputing quantization, dispatches optional CEC RX/TX processing, and updates the power-present control on TX +5V changes.

### State And Persistence Behavior

Runtime state lives in memory and hardware registers; there is no filesystem persistence. Persistent-in-session state includes selected input, active DV timings, active bus format, EDID image and block count, EDID-present bitmask, source physical address bytes, aspect ratio inferred from EDID, RGB quantization mode, CEC logical addresses, CEC enabled flag, delayed HPD work, and `restart_stdi_once`. Hardware state is programmed into the ADV76XX register pages and must be rebuilt after probe or reset. The delayed HPD work intentionally defers hotplug assertion after EDID writes. Remove cancels that work, disables interrupt masks, unregisters the subdev, cleans media entity state, unregisters ancillary I2C clients, and frees controls.

### Dependencies And Integration Points

The driver depends on Linux I2C/regmap, GPIO descriptors, V4L2 subdev/media-controller APIs, V4L2 DV timings helpers, V4L2 controls/events/debugfs infoframe support, HDMI infoframe parsing, optional CEC core support, and board data from `media/i2c/adv7604.h` or device tree. It integrates with bridge/capture drivers through V4L2 async subdev registration, media pads, source-change events, EDID ops, DV timings ops, and controls. Device-tree parsing is partial and focused on the endpoint bus flags and `default-input`; many board-specific fields are hardcoded defaults in `adv76xx_parse_dt()`.

### Risks And Edge Cases

High-risk areas are register sequencing, timing detection, and EDID/HPD races. Several comments note registers that must be written in sequence with no intervening I2C access, so refactors around gain/offset or PLL programming can break hardware behavior. ADV7604 reset GPIO handling contains an explicit warning that the logical reset level is historically inverted and should not be reused as a reset pattern. Analog timing detection depends on STDI/SSPD measurements and has retry/restart logic because LCVS/LCF can be wrong. ADV7612 input B is marked unsupported despite normal hardware support. CEC allocation is conditional; paths such as EDID clearing call CEC helpers and depend on the optional build configuration and adapter lifetime being correct. Many low-level helpers use read-modify-write without locking, so concurrent users of controls, IRQs, and EDID operations can race at the hardware-register level.

### Test Signals

Useful validation signals include probe ID detection for each supported chip, successful creation of ancillary I2C clients and regmaps, V4L2 control creation with no handler errors, media pad count matching chip capabilities, EDID set/get over all supported HDMI ports, HPD toggling after delayed work, `V4L2_CID_DV_RX_POWER_PRESENT` updates on cable-det IRQs, source-change events on format changes, query/set DV timings for HDMI and analog RGB/component, RGB range behavior for HDMI/DVI/analog modes, debugfs infoframe reads on HDMI, CEC transmit/receive callbacks when enabled, and clean remove with no delayed-work or ancillary-client leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/adv7604.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/adv7842.c -->
## sources/distributed-fs/ceph-client/drivers/media/i2c/adv7842.c

### Purpose

`adv7842.c` is a V4L2 I2C subdevice driver for the Analog Devices ADV7842 video decoder. It supports two HDMI inputs, analog component/RGB, and standard-definition CVBS/YC through the SDP block. The driver exposes the receiver as a media-controller DV decoder subdevice with sink pads and one source pad, and implements routing, analog and digital timing detection, SD standard detection, output format programming, EDID RAM management for HDMI and VGA, hotplug control, CEC, interrupts, infoframe debugfs, and a platform ioctl for DDR RAM self-test.

### Important APIs, Types, And Data

`struct adv7842_state` stores platform data, subdev, pads, controls, current mode, current DV timings, current video-standard selector, selected bus format, analog TV norm, separate HDMI and VGA EDID caches, aspect ratio, RGB quantization, CEA-format flag, delayed HPD work, STDI restart state, HDMI port selection, debugfs infoframe handles, one I2C client per register map, and optional CEC adapter state. Unlike `adv7604.c`, this driver does not use regmap; it has SMBus helpers with retry handling and direct per-map `i2c_client` accessors.

The main V4L2 operation tables are `adv7842_core_ops`, `adv7842_video_ops`, and `adv7842_pad_ops`. Core ops include status logging, private ioctl, ISR dispatch, event subscription, and optional debug register access. Video ops include analog TV standard get/set/query, input routing, and input-status reporting. Pad ops include media-bus format get/set/enumeration, EDID get/set, DV timings query/get/set/cap/enumeration. CEC integration is provided by `adv7842_cec_adap_ops` when `CONFIG_VIDEO_ADV7842_CEC` is enabled.

### Control Flow

Probe requires platform data and SMBus byte-data support, allocates state, initializes default 640x480 timings and YUYV8 output, sets the initial mode and HDMI port from platform data, reads the chip revision twice if needed, optionally issues a main reset, initializes controls, updates the power-present control, creates all dummy I2C clients, initializes delayed HPD work and media pads, then calls `adv7842_core_init()`. Unlike the async ADV7604-family driver, probe logs success and returns without calling `v4l2_async_register_subdev()` in this source; it relies on the legacy subdev registration pattern around `v4l2_i2c_subdev_init()`.

`adv7842_core_init()` programs HDMI power-down behavior, EDID access defaults, chip power, output pads, output format, HDMI audio mute policy, drive strength, CP and SDP free-run behavior, CSC, AFE muxing, SDP CSC coefficients, optional SDR/DDR memory interface setup, initial input selection, HPD mode, LLC phase, and interrupt enables. `select_input()` has four major mode paths: SDP programs CVBS/YC, AFE muxing, SDP autodetect, deinterlacer, and comb/TBC settings; component/RGB powers AFE, selects auto graphics, forces color space, and writes digitizer recommendations; HDMI selects port A/B, writes HDMI equalizer/TMDS recommendations, powers down AFE, and configures CP and autodetect color conversion.

Routing through `adv7842_s_routing()` translates input selectors into `mode`, `vid_std_select`, and `hdmi_port_a`, disables the previous input, applies the new input programming, reenables output, and emits a source-change event. `adv7842_g_input_status()` uses SDP signal-detect registers for SDP mode and CP/STDI/TMDS status for analog/digital CP modes.

DV timing query is disabled for SDP mode and otherwise reads STDI via `read_stdi()`. Digital mode builds BT timings directly from HDMI registers and pixel-clock registers, including deep-color adjustment and reduced-FPS flag detection. Analog component/RGB mode maps STDI data through known presets, CVT, and GTF detection, with a one-shot STDI restart if detection fails. `adv7842_s_dv_timings()` validates against analog or digital caps, stores the timings, configures CP interlace, selects predefined prim-mode/video-std values when possible, otherwise writes custom active-video and PLL timing registers, and reapplies RGB quantization.

EDID is split between HDMI and VGA storage. `adv7842_set_edid()` enforces that VGA EDID consumes segment 1 and therefore limits HDMI EDID to two blocks when VGA EDID is installed; conversely VGA EDID cannot be set while HDMI EDID uses more than two blocks. HDMI EDID writes validate the physical address, write RAM blocks with segment switching, program per-port SPA registers, enable repeater EDID bits, wait for enable status, update CEC physical address, and schedule delayed HPD. VGA EDID writes program the VGA segment and enable VGA DDC access. Clearing HDMI EDID updates the present bitmask and invalidates CEC physical address when no HDMI EDID remains.

Interrupt handling disables IRQ masks during status read/clear, clears six IO status groups, reenables masks, then detects CP, SDP, and digital format changes, HDMI/DVI mode changes, optional CEC events, and TX +5V changes. Format changes emit V4L2 source-change events; HDMI/DVI mode changes recompute RGB quantization.

### State And Persistence Behavior

State is volatile and reconstructed at probe. Important state includes platform data, current mode, selected HDMI port, active DV timings, selected bus format, SDP norm, video-standard selector, EDID caches, EDID-present masks, aspect ratio, RGB quantization mode, delayed HPD work, CEC logical addresses, and STDI restart guard. The RAM test ioctl deliberately resets the chip, rewrites I2C page addresses, runs BIST, resets again, reruns core init, reselects input, restores EDID, and reapplies saved timings. Remove disables IRQs, cancels HPD work, unregisters the subdev, cleans media entity and controls, and unregisters all dummy clients.

### Dependencies And Integration Points

The driver depends on platform data from `media/i2c/adv7842.h`; it has no OF match table. It integrates with V4L2 subdev/media-controller APIs, V4L2 controls/events/DV timings, analog TV standards, HDMI infoframe parsing, optional CEC, and I2C SMBus dummy devices. Platform data controls I2C map addresses, reset policy, initial input/mode, AFE muxing, output bus flags, drive strength, free-run modes, SDP CSC coefficients, SDP sync adjustment, RAM type/size, HPD policy, and LLC phase.

### Risks And Edge Cases

The largest risks are platform-data correctness, mode-specific register programming, and global EDID layout constraints. All ancillary map addresses must be supplied and valid or probe fails. Many helpers perform read-modify-write via masks named `*_and_or()` where the mask is the preserved-bits mask, not the clear mask, so call sites are easy to misuse. EDID HDMI/VGA sharing has non-obvious constraints and can return `-EBUSY` or `-E2BIG` depending on current cached state. The RAM test resets hardware and replays state, making it sensitive to incomplete restoration. Timing detection excludes SDP and has analog STDI restart behavior similar to ADV7604. IRQ handling disables and reenables masks around status reads; missed or coalesced events need hardware testing. The driver is legacy platform-data-only, so new DT-based boards cannot bind without additional work.

### Test Signals

Validation should cover revision detection, failure on missing platform data, creation and cleanup of all dummy clients, initial route setup for HDMI A/B, VGA RGB/component, CVBS, and YC, status reporting for SDP and CP paths, SD standard query/set for NTSC/PAL variants, DV timing query/set for HDMI and component/RGB, SDP format reporting as fixed 720x480/576 YUYV, EDID set/get for HDMI A/B and VGA including block-limit edge cases, HPD delayed enable, CEC RX/TX if configured, source-change events from CP/SDP/HDMI IRQs, RGB quantization on HDMI/DVI changes, RAM-test ioctl restore behavior, and remove-time IRQ/work/client cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/adv7842.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ak7375.c -->
## sources/distributed-fs/ceph-client/drivers/media/i2c/ak7375.c

### Purpose

`ak7375.c` is a compact V4L2 lens subdevice driver for Asahi Kasei AK7345 and AK7375 voice-coil motor focus actuators. It exposes a single `V4L2_CID_FOCUS_ABSOLUTE` control, handles regulator power sequencing, smooth lens parking/restoration during runtime and system PM, and registers as a media entity with function `MEDIA_ENT_F_LENS`.

### Important APIs, Types, And Data

`struct ak73xx_chipdef` describes per-chip register layout and motion characteristics: position register, control register, position shift, active/standby values, standby support, maximum focus position, focus step granularity, smooth-move step size, inter-step delay, and power-on delay. Two definitions are present: AK7345 uses 9-bit focus values shifted by 7 with no standby mode and a 20 ms power delay; AK7375 uses 12-bit focus values shifted by 4, supports standby mode `0x40`, and has a 10 ms power delay.

`struct ak7375_device` holds the chip definition, V4L2 control handler, subdev, focus control pointer, bulk regulators for `vdd` and `vio`, and an `active` flag. The V4L2-facing operations are minimal: empty subdev ops, internal `.open` and `.close` hooks that resume and release runtime PM, and a control op `ak7375_set_ctrl()` that writes focus position over I2C.

### Control Flow

Probe allocates state, obtains the OF match data chip definition, initializes the two regulator descriptors, gets regulators, initializes the I2C subdev, marks it as having a devnode, assigns internal ops, sets media entity function to lens, creates the focus control with chip-specific maximum/step values, initializes a zero-pad media entity, registers the subdev asynchronously, and enables runtime PM. The device is marked active and then idled, allowing runtime suspend to park/power-down it.

Control writes go through `ak7375_set_ctrl()`: for `V4L2_CID_FOCUS_ABSOLUTE`, the requested value is shifted according to the chip definition and written as a two-byte position value with `ak7375_i2c_write()`. That helper constructs one- or two-byte register writes using `i2c_master_send()` and converts partial sends to `-EIO`.

Runtime/system suspend first returns if the device is already inactive. Otherwise it walks the current focus value downward in `ctrl_steps` increments, writing each intermediate position and sleeping for `ctrl_delay_us`, optionally writes standby mode, disables both regulators, and clears `active`. Resume enables regulators, waits for `power_delay_us`, writes active mode, walks upward from the nearest low partial step to the saved focus value in `ctrl_steps` increments, and sets `active`.

### State And Persistence Behavior

The driver does not persist data outside memory. The saved focus value is the V4L2 control's current value; suspend/resume uses it to park and restore the lens smoothly. Hardware power state is represented by the `active` boolean and regulators. The control value can be set while active; open/close manage runtime PM references, so user access powers the actuator. Remove unregisters the subdev, frees controls, cleans media entity state, disables runtime PM, and marks the device suspended.

### Dependencies And Integration Points

The driver depends on OF device matching for chip data, the regulator consumer API, runtime PM, Linux I2C, and V4L2 control/subdev/media APIs. Compatible strings are `asahi-kasei,ak7345` and `asahi-kasei,ak7375`. It integrates with camera sensor pipelines as a lens subdevice, usually controlled by userspace or a camera stack through `V4L2_CID_FOCUS_ABSOLUTE`.

### Risks And Edge Cases

`device_get_match_data()` is assumed to return a valid chip definition; a non-OF binding without match data would lead to invalid dereferences. In `ak7375_vcm_resume()`, if writing active mode fails after regulators are enabled, the function returns without disabling regulators or setting `active`, leaving power cleanup to later PM/remove paths. Suspend logs I2C failures during gradual parking but continues the loop and may still power down. The smooth-step arithmetic assumes `ctrl_steps` is a power of two, as documented in the chip definition comment. Focus writes are not explicitly blocked while inactive, so correct runtime-PM sequencing depends on subdev open/close and control framework usage.

### Test Signals

Useful tests include probe with both compatible strings, regulator acquisition failure paths, focus control range/step correctness for AK7345 and AK7375, one-byte control register writes and two-byte position writes, runtime resume enabling regulators and restoring saved focus, runtime suspend gradually parking and optionally entering standby, open/close PM reference behavior, remove cleanup after active and suspended states, and I2C partial-send/error handling from `ak7375_i2c_write()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ak7375.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ak881x.c -->
## sources/distributed-fs/ceph-client/drivers/media/i2c/ak881x.c

### Purpose

`ak881x.c` is a V4L2 I2C subdevice driver for AKM AK8813/AK8814 TV encoders. It accepts a YUYV media-bus stream and drives analog TV output, supporting NTSC and PAL-family output-standard selection, composite or component DAC enablement based on platform flags, basic pad format reporting, and optional debug register access.

### Important APIs, Types, And Data

`struct ak881x` contains the V4L2 subdev, platform data pointer, active line count, and chip revision. Platform data from `media/i2c/ak881x.h` supplies flags for field mode, BT.656/master/slave interface mode, and component output. Register helpers `reg_read()`, `reg_write()`, and `reg_set()` wrap SMBus byte-data access.

The subdev operation tables expose optional ADV debug register get/set, video ops `.s_std_output` and `.s_stream`, and pad ops `.enum_mbus_code`, `.get_fmt`, `.set_fmt`, and `.get_selection`. Only pad 0 and `MEDIA_BUS_FMT_YUYV8_2X8` are supported. Crop bounds and format height depend on the current standard-derived line count.

### Control Flow

Probe verifies SMBus byte-data support, allocates state, initializes the subdev, reads `AK881X_DEVICE_ID`, accepts IDs `0x13` and `0x14`, reads revision, stores platform data, programs interface mode when platform data is present, defaults line count to 480 for NTSC-M hardware default, and logs detection. Interface mode combines field flag, BT.656/master/slave selection, and a fixed line-blanking value of 20 into `AK881X_INTERFACE_MODE`.

Output standard selection in `ak881x_s_std_output()` maps exact or masked V4L2 standards to the low nibble of `AK881X_VIDEO_PROCESS1` and updates `lines` to 480 or 576. It supports NTSC, NTSC-443, PAL-M, PAL-60, and PAL; SECAM and PAL_N/Nc are rejected. Streaming in `ak881x_s_stream()` writes `AK881X_DAC_MODE`: enable uses DAC value `3` for component output or `4` for composite output, while disable writes zero. It logs the chip status register after each transition.

Pad format filling bounds width to an aligned maximum of 720 and height to the current `lines`, sets interlaced field, YUYV8 2X8 bus code, and SMPTE170M colorspace. Selection only supports active crop bounds covering 720 by current line count.

### State And Persistence Behavior

The driver keeps only volatile in-memory state: platform data pointer, current line count, and revision. Hardware state is programmed directly through small SMBus writes. There is no runtime PM, regulator, async registration, EDID, or persistent storage. Remove unregisters the subdev. Because `lines` is updated by output-standard selection, later format and crop queries reflect the most recently selected standard.

### Dependencies And Integration Points

The driver depends on I2C SMBus byte-data support, V4L2 subdev/media-bus APIs, and board platform data. It is a legacy non-DT driver with I2C IDs `ak8813` and `ak8814`. It integrates with a video output pipeline through subdev pad format negotiation and `.s_stream()`, and with TV-output configuration through `.s_std_output()`.

### Risks And Edge Cases

The warning message on missing SMBus byte support says `I2C_FUNC_SMBUS_WORD` although the code checks byte-data support. If platform data is absent, probe still succeeds but interface mode and output kind are not configured; later `ak881x_s_stream()` dereferences `ak881x->pdata`, so streaming without platform data can crash. `ak881x_s_std_output()` ignores the return value from `reg_set()`, so I2C failures are hidden. Format set/get uses `v4l_bound_align_image()` with a minimum width/height of zero, so callers can negotiate zero dimensions unless higher layers constrain them. There is no power management or explicit output-off action in remove.

### Test Signals

Validation should cover accepted and rejected chip IDs, revision read, platform flag combinations for field and interface mode, no-platform-data behavior, standard selection for NTSC/PAL variants and rejection of SECAM/PAL_N, line count changes reflected in get_fmt and crop bounds, stream enable/disable DAC writes for composite and component outputs, debug register bounds under `CONFIG_VIDEO_ADV_DEBUG`, and I2C error propagation gaps in standard selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ak881x.c -->
