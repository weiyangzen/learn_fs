# Research: subset-b-003663

Grouped source research for subset B work item `subset-b-003663`. Each delimited section preserves the source path and can be split into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/adreno/adreno_pm4.xml -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/adreno/adreno_pm4.xml

## Purpose
This XML file is the Freedreno/Adreno PM4 command-stream schema. It defines command processor packet types, event ids, draw initiators, register/memory operation payloads, indirect-buffer formats, shader-state load packets, binning packets, cache/CCU/LRZ events, timestamp and synchronization packets, and generation-specific opcode variants from A2xx through A8xx. It is not executable kernel logic itself; its practical API is the generated C header consumed by MSM Adreno ringbuffer emission code.

## Important APIs, Types, and Functions
The important generated symbols come from enums such as `vgt_event_type`, `pc_di_primtype`, `pc_di_src_sel`, `pc_di_face_cull_sel`, `pc_di_index_size`, `pc_di_vis_cull_mode`, `adreno_pm4_packet_type`, and `adreno_pm4_type3_packets`. Packet payload domains include `CP_LOAD_STATE`, `CP_LOAD_STATE4`, `CP_LOAD_STATE6`, `CP_DRAW_INDX`, `CP_DRAW_INDX_2`, `CP_DRAW_INDX_OFFSET`, `CP_DRAW_INDIRECT`, `CP_DRAW_INDX_INDIRECT`, `CP_DRAW_INDIRECT_MULTI`, `CP_DRAW_AUTO`, predication packets, `CP_SET_DRAW_STATE`, binning packets, register/memory copy and wait packets, `CP_DISPATCH_COMPUTE`, `CP_SET_RENDER_MODE`, `CP_COMPUTE_CHECKPOINT`, `CP_PERFCOUNTER_ACTION`, `CP_EVENT_WRITE`, and A7xx/A8xx additions such as timestamp, thread-control, resource-list, cache, memory-map, and barrier commands. Driver call sites use these as `CP_*`, `*_EVENT`, and field packer macros through `OUT_PKT3`, `OUT_PKT4`, `OUT_PKT7`, and `OUT_RING`.

## Control Flow
Kernel and userspace command submission builds PM4 streams by choosing a packet opcode, packing fields defined here, then placing the words in a ringbuffer or indirect buffer. Older generations use type3 packets for many paths, while A5xx+ use packet7 variants and generation-specific opcodes where numeric ids were reused. Control dependencies are expressed by wait packets, event writes, cache flush/invalidate events, SMMU table update commands, preemption/yield packets, and thread-synchronization packets rather than C control flow in this XML.

## State and Persistence Behavior
This schema defines how command streams mutate GPU state: shader program state, constants, UBO/UAV state, draw state objects, predicate state, binning state, render mode, SMMU context, scratch registers, counters, timestamps, cache/CCU/LRZ contents, and memory writes. The XML itself persists only as source for generated headers, but incorrect field definitions persist into every compiled packet writer and therefore into the ABI between the kernel/userspace command emitters and GPU firmware.

## Dependencies and Integration Points
It imports `adreno/adreno_common.xml` and common Freedreno copyright metadata, and it is consumed by the register generation pipeline that produces Adreno PM4 C macros. Integration points include `a2xx_gpu.c`, `a3xx_gpu.c`, `a4xx_gpu.c`, `a5xx_gpu.c`, `a5xx_preempt.c`, `a6xx_gpu.c`, crashdump/state capture code, Mesa/Freedreno command emitters, GPU firmware packet parsers, ringbuffer submit paths, preemption support, cache management, and SMMU context switching.

## Risks
The highest risk is opcode reuse across generations: a numeric packet or event value may mean different things on A4xx, A5xx, A6xx, A7xx, or A8xx, so missing or wrong `variants` attributes can emit a valid-looking but wrong command. Address field width differences, packet length expectations, predicate side effects, cache event semantics, protected-mode toggles, and SMMU update payloads are all sensitive. Errors here usually fail as GPU hangs, command processor faults, memory corruption, stale cache data, or unhandled preemption.

## Test Signals
Useful signals include generated-header build checks, GPU submit smoke tests on each supported generation, ringbuffer idle and fence completion tests, cache flush timestamp validation, SMMU context-switch tests, preemption/yield stress, IGT/MSM GPU tests, Mesa deqp/piglit coverage, crashdump decoding sanity, and fault-injection around invalid packets or register protection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/adreno/adreno_pm4.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/display/dsi.xml -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/display/dsi.xml

## Purpose
This XML describes the MSM DSI controller register block. It defines video-mode and command-mode programming, MIPI packet formats, triggers, active/total timing registers, DMA command transfer registers, lane status/control, interrupt bits, clocks, test-pattern generation, C-PHY mode, and DSC compression control registers.

## Important APIs, Types, and Functions
Generated APIs include `REG_DSI_*` address macros, bitfield packers for `DSI_CTRL`, `DSI_VID_CFG0`, `DSI_VID_CFG1`, `DSI_CMD_DMA_CTRL`, `DSI_CMD_CFG*`, `DSI_TRIG_CTRL`, lane status/control registers, `DSI_INTR_CTRL`, `DSI_CLK_CTRL`, `DSI_CLK_STATUS`, TPG registers, and compression mode registers. Important enums and bitsets are `dsi_traffic_mode`, `dsi_vid_dst_format`, `dsi_rgb_swap`, `dsi_cmd_trigger`, `dsi_cmd_dst_format`, `dsi_lane_swap`, TPG pattern enums, and `DSI_IRQ`.

## Control Flow
The DSI driver programs this block by enabling clocks and PHY reset, selecting lanes and video or command mode in `CTRL`, writing display timing registers, configuring command DMA or MDP stream packet payloads, selecting trigger sources, enabling error checking, and finally enabling the controller path. Interrupt flow is represented by `DSI_IRQ` status/mask fields for command DMA, command MDP, video done, BTA done, and error handling. Readback and BTA flows use `RDBK`, `RDBK_DATA_CTRL`, lane busy/status, and timeout registers.

## State and Persistence Behavior
Persistent runtime state lives in hardware registers: enabled lanes, current mode, pixel format, video timing, command stream packet words, trigger state, clock gating state, lane stop/ULPS status, TPG configuration, and DSC packetization parameters. The XML contributes no runtime storage, but generated field definitions determine how driver state is encoded across modesets, panel prepare/enable, command transfers, error recovery, and suspend/resume reprogramming.

## Dependencies and Integration Points
It is consumed by MSM DSI host, panel bridge, PHY, and KMS display code through generated register macros. It integrates with MIPI DSI packet construction, DRM display modes, MDSS/MDP output, DSI PHY timing code, runtime PM clock handling, IRQ handlers, panel command sequences, DSC configuration, and debug/test-pattern paths.

## Risks
Bitfield mistakes can corrupt timing or packet format programming and result in blank panels, underruns, failed command transfers, or DSI bus contention. The file contains overlapping offsets such as hardware version versus control naming at offset zero, version-dependent field-width comments, and late additions for C-PHY/DSC; consumers must select the right semantic view for the hardware generation. IRQ mask/status polarity must be handled carefully to avoid lost completions or interrupt storms.

## Test Signals
Signals include generated-header compilation, panel bring-up in video and command mode, command DMA completion tests, BTA/readback tests, IRQ ack/mask behavior, lane stop-state and ULPS transitions, TPG output, DSC-enabled modes, suspend/resume display restore, and underrun/error interrupt logging under stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/display/dsi.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/display/dsi_phy_10nm.xml -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/display/dsi_phy_10nm.xml

## Purpose
This XML describes the 10nm DSI PHY register layout. It covers the common PHY control block, per-lane analog/digital lane registers, and the PLL block used to synthesize DSI bit/byte clocks.

## Important APIs, Types, and Functions
Generated symbols include `REG_DSI_10nm_PHY_CMN_*`, `REG_DSI_10nm_PHY_LN_*`, and `REG_DSI_10nm_PHY_PLL_*`. Important register groups are revision ids, `CLK_CFG*`, `GLBL_CTRL`, `RBUF_CTRL`, `VREG_CTRL`, lane config/control, `PLL_CNTRL`, common timing controls `TIMING_CTRL_0` through `TIMING_CTRL_11`, `PHY_STATUS`, lane status registers, per-lane `CFG*`, `PIN_SWAP`, high/low power TX/RX strength controls, and PLL controls for DSM/feedback dividers, calibration, filters, SSC, lock-detect, and output division.

## Control Flow
The PHY driver typically reads revision ids, enables regulators/buffers, writes PLL divider and calibration values for the desired lane rate, programs common and per-lane timing registers, enables lane control, starts the PLL, polls lock/status, and hands the byte/bit clock to the DSI controller. Per-lane arrays allow identical programming over clock/data lanes while still supporting pin swap and lane-specific electrical tuning.

## State and Persistence Behavior
Runtime state is the PHY's analog configuration: PLL dividers, spread-spectrum values, calibration bands, lane strengths, pin swaps, D-PHY timing values, and status/lock bits. It must be re-created after power collapse or reset; the XML itself persists only the register map used by generated headers.

## Dependencies and Integration Points
This map integrates with the MSM DSI PHY 10nm implementation, common DSI host timing calculations, DRM mode clock selection, regulator and reset control, clock framework PLL registration, and panel enable/disable sequencing. It is close to the 7nm map but has a smaller common/PLL register set and 10nm-specific offsets.

## Risks
PLL and timing register offsets are highly silicon-specific; using 7nm or 14nm values against this map can leave the PLL unlocked or violate MIPI timing. Lane array stride or length mistakes affect clock/data lane addressing. Status polling that assumes another PHY generation's lock bits can cause false success or timeouts.

## Test Signals
Useful tests are generated macro build checks, mode validation across multiple bit rates, PLL lock polling, panel enable/disable loops, ULPS/stop-state transitions, suspend/resume, lane swap configurations, and scope or panel-visible validation for high-speed timing margins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/display/dsi_phy_10nm.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/display/dsi_phy_14nm.xml -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/display/dsi_phy_14nm.xml

## Purpose
This XML defines the 14nm DSI PHY common block, lane block, and PLL registers. It captures the 14nm-specific split between common software/hardware configuration, per-lane D-PHY timing, lane strength, LDO control, and PLL tuning/calibration registers.

## Important APIs, Types, and Functions
Generated symbols include `REG_DSI_14nm_PHY_CMN_*`, `REG_DSI_14nm_PHY_LN_*`, and `REG_DSI_14nm_PHY_PLL_*`. Notable bitfields include common clock-divider bits in `CLK_CFG0`, `DSICLK_SEL`, `BITCLK_HS_SEL`, `PLL_CNTRL_PLL_START`, `LDO_CNTRL_VREG_CTRL`, lane `CFG0_PREPARE_DLY`, `CFG1_HALFBYTECLK_EN`, D-PHY timing fields for `HS_EXIT`, `HS_ZERO`, `HS_PREPARE`, `HS_TRAIL`, `HS_RQST`, `TA_GO`, `TA_SURE`, `TA_GET`, and `TRIG3_CMD`. The PLL map includes trim, reset state machine, KVCO/VCO calibration, lock compare, fractional divider, SSC, TX clock, charge pump, filter, and bandgap registers.

## Control Flow
14nm PHY enable flows program common clock selection and LDO state, configure per-lane timing/strength, program PLL dividers and calibration, assert `PLL_START`, wait for ready/lock status, and then allow the DSI controller to transmit. Disable flows reverse this by stopping the controller, disabling lanes/PLL, and potentially powering down LDO/regulator state.

## State and Persistence Behavior
The live state consists of lane electrical tuning, timing counters, common clock routing, LDO voltage control, and PLL calibration/divider values. This state is volatile across PHY reset and power collapse, so the driver must replay it during every enable or resume sequence.

## Dependencies and Integration Points
The map is used by the 14nm DSI PHY driver, DSI host mode setup, regulator/clock/reset framework, PLL clock provider code, and panel bridge sequencing. It shares conceptual timing fields with 20nm/28nm maps but has different offsets and extra common/PLL controls.

## Risks
The `CLK_CFG0` duplicate field names map both divider halves to the same bit range, so consumers must understand the intended hardware meaning before relying on generated packers. Wrong PLL trim/calibration values can produce unstable clocks. Timing field mismatches appear as intermittent panel failures, lane errors, or high-speed entry/exit violations.

## Test Signals
Signals include generated-header build, PLL lock and rate tests, multiple DSI lane counts and bpp modes, panel enable/disable loops, runtime PM resume, ULPS/low-power transitions, high-speed timing margin validation, and failure logs for lane/PLL status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/display/dsi_phy_14nm.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/display/dsi_phy_20nm.xml -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/display/dsi_phy_20nm.xml

## Purpose
This XML defines the 20nm DSI PHY register map. It is a compact D-PHY map with four data-lane register windows, a separate clock-lane register group, timing controls, control/strength registers, BIST controls, global test control, and LDO control.

## Important APIs, Types, and Functions
Generated symbols include `REG_DSI_20nm_PHY_LN_*`, `REG_DSI_20nm_PHY_LNCK_*`, timing control macros, `REG_DSI_20nm_PHY_CTRL_*`, `REG_DSI_20nm_PHY_STRENGTH_*`, BIST register macros, `REG_DSI_20nm_PHY_GLBL_TEST_CTRL`, and `REG_DSI_20nm_PHY_LDO_CNTRL`. Timing bitfields cover `CLK_ZERO`, `CLK_TRAIL`, `CLK_PREPARE`, high bit `CLK_ZERO_8`, `HS_EXIT`, `HS_ZERO`, `HS_PREPARE`, `HS_TRAIL`, `HS_RQST`, `TA_GO`, `TA_SURE`, `TA_GET`, and `TRIG3_CMD`.

## Control Flow
The enable path programs each data lane via the `LN` array, separately configures the clock lane, writes D-PHY timing controls computed from the mode bit clock, selects strengths/control values, and enables the LDO/test settings required for transmission. Unlike the later 10nm/7nm XML files, this map does not include a PLL domain in the same file, so clock generation is integrated elsewhere or through a different block.

## State and Persistence Behavior
The state described here is volatile PHY register state: lane config, clock-lane config, timing counters, control bits, drive strength, BIST setup, and LDO settings. It must be restored after reset or power loss and kept coherent with the DSI controller's lane count and low/high power transition timing.

## Dependencies and Integration Points
It integrates with MSM DSI PHY 20nm code, DSI host mode timing, regulator/reset control, lane-count setup, and panel bridge lifecycle. It shares many D-PHY timing fields with 28nm and 28nm-8960 maps, enabling common timing calculation with generation-specific register offsets.

## Risks
Clock-lane and data-lane windows are distinct, so array-index assumptions can misprogram the clock lane. Missing or wrong timing high bits, especially for `CLK_ZERO`, can break high-rate modes. BIST/test registers should not be left active during normal display operation.

## Test Signals
Useful signals are panel bring-up on 20nm devices, generated macro compilation, lane-count variants, timing validation at low and high bit rates, power-cycle loops, BIST isolation, and suspend/resume display restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/display/dsi_phy_20nm.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/display/dsi_phy_28nm.xml -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/display/dsi_phy_28nm.xml

## Purpose
This XML describes the standard 28nm DSI PHY, its regulator block, and its PLL block. It covers four data lanes, a clock lane, D-PHY timing/control/strength/BIST registers, regulator calibration/power controls, and PLL programming for the DSI serial clock.

## Important APIs, Types, and Functions
Generated APIs include `REG_DSI_28nm_PHY_*`, `REG_DSI_28nm_PHY_REGULATOR_*`, and `REG_DSI_28nm_PHY_PLL_*`. Important bitfields include timing fields for clock and HS/TA transitions, `GLBL_TEST_CTRL_BITCLK_HS_SEL`, PLL `REFCLK_CFG_DBLR`, `VREG_CFG_POSTDIV1_BYPASS_B`, `GLB_CFG_PLL_PWRDN_B`, `GLB_CFG_PLL_LDO_PWRDN_B`, `GLB_CFG_PLL_PWRGEN_PWRDN_B`, `GLB_CFG_PLL_ENABLE`, SDM divider/dither fields, `TEST_CFG_PLL_SW_RESET`, and `STATUS_PLL_RDY`.

## Control Flow
Driver setup programs regulator control/calibration, configures PLL reference/post-divider/charge-pump/SDM/SSC/lock-detect/calibration registers, enables PLL power bits, polls `PLL_RDY`, then programs PHY lane and timing registers for the desired DSI mode. The DSI host depends on this sequence completing before enabling high-speed transmission.

## State and Persistence Behavior
The register state spans regulator power, PLL tuning, spread spectrum, lock detection, calibration results, lane timing, strength, test/BIST settings, and control flags. All of it is hardware-volatile and must be replayed after PHY reset, regulator disable, or SoC suspend.

## Dependencies and Integration Points
This map is consumed by the 28nm DSI PHY and PLL code, DSI host mode setup, regulator framework, clock framework, panel power sequencing, and common D-PHY timing calculations. It is related to `dsi_phy_20nm.xml` for lane/timing layout and to `dsi_phy_28nm_8960.xml` for earlier 8960-specific differences.

## Risks
PLL power bit polarity and SDM fractional fields are easy to mispack; failures appear as no PLL lock or wrong pixel clock. Regulator and PLL domains are separate, so incomplete programming can pass generated-header tests but fail electrically. Accidentally using 8960 offsets on the standard 28nm map corrupts clock-lane or control programming.

## Test Signals
Signals include PLL rate/lock tests, generated macro build, panels at several refresh rates, high/low lane-count modes, suspend/resume, regulator off/on loops, DSI error counters, and visual stability under high pixel-clock modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/display/dsi_phy_28nm.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/display/dsi_phy_28nm_8960.xml -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/display/dsi_phy_28nm_8960.xml

## Purpose
This XML defines the 28nm DSI PHY variant used by MSM8960-era hardware. It is a reduced/specialized D-PHY map with four data lanes, a clock lane, timing registers, control/strength registers, BIST controls, and LDO control, but without the standard 28nm regulator and PLL domains in this file.

## Important APIs, Types, and Functions
Generated macros use the `DSI_28nm_8960_PHY` domain and include lane array registers `LN_CFG_*`, `LN_TEST_*`, clock-lane `LNCK_*`, timing controls for clock/HS/TA transitions, `CTRL_0` through `CTRL_3`, `STRENGTH_0` through `STRENGTH_2`, BIST controls, and `LDO_CTRL`. Timing fields mirror the older 20nm/28nm-style names such as `CLK_ZERO`, `CLK_TRAIL`, `CLK_PREPARE`, `HS_EXIT`, `HS_ZERO`, `HS_PREPARE`, `HS_TRAIL`, `HS_RQST`, `TA_GO`, `TA_SURE`, `TA_GET`, and `TRIG3_CMD`.

## Control Flow
The 8960 PHY driver programs data lanes, the dedicated clock lane, timing counters, strength values, and LDO control as part of DSI host enable. Since PLL/regulator details are not represented as separate domains here, those controls are either external to this map or handled by 8960-specific code paths.

## State and Persistence Behavior
The described state is volatile lane, timing, strength, BIST, and LDO hardware state. It is tied to the active DSI mode and must be restored whenever the display pipeline is powered back up.

## Dependencies and Integration Points
It integrates with legacy MSM8960 DSI PHY support, DSI host timing calculation, panel enable/disable sequences, and platform-specific clock/regulator setup. It must remain separate from the standard `DSI_28nm_PHY` map because offsets and available registers differ.

## Risks
The similarity to standard 28nm and 20nm maps can hide subtle offset/register-count differences. The missing PLL domain means tests that only validate generated symbols may not cover full clock bring-up. Misprogramming strength or LDO settings can cause marginal panels that fail only under temperature, voltage, or high bit-rate conditions.

## Test Signals
Useful coverage includes generated macro checks, MSM8960 panel bring-up, lane-count modes, repeated power cycles, suspend/resume, DSI command/video mode validation, and timing stress near maximum supported lane rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/display/dsi_phy_28nm_8960.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/display/dsi_phy_7nm.xml -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/display/dsi_phy_7nm.xml

## Purpose
This XML defines the 7nm DSI PHY, including a larger common block, per-lane registers, and an expanded PLL block. It supports modern DSI electrical configuration with global timing controls, strength/pre-emphasis/rescode controls, VREG controls, PHY/lane status, and rich PLL calibration, SSC, rate, and lock programming.

## Important APIs, Types, and Functions
Generated symbols include `REG_DSI_7nm_PHY_CMN_*`, `REG_DSI_7nm_PHY_LN_*`, and `REG_DSI_7nm_PHY_PLL_*`. Important common registers are revision ids, clock/global controls, lane controls, PLL control, timing controls `TIMING_CTRL_0` through `TIMING_CTRL_13`, global HSTX/LPTX/pre-emphasis/rescode controls, VREG, status, and lane status. Per-lane registers cover `CFG*`, `TEST_DATAPATH`, `PIN_SWAP`, `LPRX_CTRL`, and `TX_DCTRL`. PLL registers cover analog controls, DSM/feedback dividers, calibration timers and bands, frequency detect, filters, gain, lock-detect, outdiv, fastlock, pass/core overrides, rate change, decimal/fractional divider sets, MASH, SSC sets, rate-specific lock/gain/band controls, and lock override/delay.

## Control Flow
7nm PHY enable flows program common lane/timing/electrical controls, set per-lane configuration and pin swap, program PLL dividers and calibration for the requested bit clock, optionally configure SSC/rate tables, start or update the PLL, poll lock/status, and then allow the DSI controller to enter high-speed operation. The larger common timing block lets the driver program timing globally instead of repeating all timing fields inside each lane window.

## State and Persistence Behavior
Runtime state includes global timing, lane control, drive strength, pre-emphasis, rescode offsets, VREG state, lane status, PLL calibration bands, divider state, SSC state, and rate-dependent PLL parameters. It is volatile across PHY power collapse and must be rebuilt by the driver during enable and resume.

## Dependencies and Integration Points
It integrates with 7nm DSI PHY and PLL drivers, the MSM clock framework, DSI host mode calculation, panel sequencing, regulator/reset management, and newer SoC display pipelines. It is structurally related to 10nm but has a richer common/PLL register set and different offsets.

## Risks
The expanded PLL block contains many similarly named rate and divider registers; off-by-one offset errors can generate clocks that appear locked but are at the wrong rate. Global timing programming differs from older lane-local timing maps, so shared timing code must branch correctly. Pin swap, pre-emphasis, and rescode values are board- and PHY-sensitive.

## Test Signals
Signals include generated macro build, PLL rate and lock verification, multiple refresh rates and bpp modes, dual-DSI or lane-swap configurations, suspend/resume, ULPS transitions, high bit-rate stress, DSC panel modes, and display stability under repeated power collapse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/display/dsi_phy_7nm.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/display/edp.xml -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/display/edp.xml

## Purpose
This XML describes MSM embedded DisplayPort controller, AUX, interrupt, PHY, and 28nm eDP PLL registers. It covers mainlink enable/reset, link training state, stream timing, M/N video values, DP MISC fields, PHY reset/status, AUX/I2C transactions, hotplug and error interrupts, and PLL programming.

## Important APIs, Types, and Functions
Generated APIs include `REG_EDP_*`, `REG_EDP_PHY_*`, and `REG_EDP_28nm_PHY_PLL_*` macros. Important enums are `edp_color_depth` and `edp_component_format`. Key registers include `MAINLINK_CTRL`, `STATE_CTRL`, `CONFIGURATION_CTRL`, `SOFTWARE_MVID`, `SOFTWARE_NVID`, total/start/sync/active timing registers, `MISC1_MISC0`, `PHY_CTRL`, `MAINLINK_READY`, `AUX_CTRL`, `INTERRUPT_REG_1`, `INTERRUPT_REG_2`, AUX data/transaction/status registers, lane power controls, PHY global controls/status, and PLL power/divider/SDM/SSC/calibration/status registers.

## Control Flow
The eDP driver configures PHY and PLL, powers lanes, enables AUX, performs link training by selecting training patterns and polling readiness, programs M/N and stream timing from the DRM mode, sets color/MISC fields, and finally sends video over the mainlink. AUX control registers drive DPCD/EDID I2C-over-AUX transactions, while interrupt registers expose HPD, AUX completion, timeout/NACK/defer, PLL unlock, ready-for-video, frame-end, and CRC events.

## State and Persistence Behavior
Hardware state includes lane power, PHY/PLL settings, training pattern state, link configuration, video timing, M/N values, AUX transaction state, HPD/interrupt masks, and stream enable. It is volatile across display powerdown and suspend, so link training and timing programming are replayed on resume or modeset.

## Dependencies and Integration Points
This map integrates with DRM DP helpers, eDP bridge/connector code, AUX transfer code, EDID/DPCD reads, clock/PHY/regulator setup, link training, and display timing setup. The PLL subdomain resembles 28nm DSI PLL style controls but is eDP-specific in integration.

## Risks
Wrong training pattern or readiness bits can make link training hang. Interrupt registers use status/ack/enable triplets, so ack polarity errors can lose HPD/AUX events. The `INTERRUPT_REG_2` field positions include suspicious overlap around frame-end and CRC bits, which should be verified against hardware behavior before adding new consumers. Incorrect MISC/color depth encoding can produce wrong colors or sink rejection.

## Test Signals
Useful tests include AUX EDID/DPCD reads, link training across lane counts/rates, HPD plug/unplug events, suspend/resume, CRC/frame-end interrupt behavior, PLL unlock handling, modes with different bpc values, and generated-header compilation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/display/edp.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/display/hdmi.xml -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/display/hdmi.xml

## Purpose
This XML defines the MSM HDMI controller and multiple HDMI PHY/PLL register maps. It covers HDMI core enable, audio packet/ACR/infoframe/generic packet programming, HDCP authentication and DDC handshakes, DDC/I2C transactions, HPD, CEC, video timing, frame control, audio interrupts, PHY reset, legacy PHY variants, 8x74/8996/8998 PHY blocks, and QSERDES common/TX PLL domains.

## Important APIs, Types, and Functions
Generated APIs include `REG_HDMI_*`, `REG_HDMI_8x60_*`, `REG_HDMI_8960_*`, `REG_HDMI_8x74_*`, `REG_HDMI_8996_*`, `REG_HDMI_PHY_QSERDES_*`, and `REG_HDMI_8998_*` macros. Important enums are `hdmi_hdcp_key_state`, `hdmi_ddc_read_write`, `hdmi_acr_cts`, and `hdmi_cec_tx_status`. Key controller registers include `CTRL`, audio packet and ACR controls, VBI/infoframe/generic packet controls, AVI/audio/vendor info arrays, HDCP control/status/DDC/SHA/receiver-port registers, DDC control/status/speed/setup/transaction/data registers, HPD status/control, CEC control/data/status/interrupt registers, timing registers, `FRAME_CTRL`, audio interrupt, and `PHY_CTRL`.

## Control Flow
HDMI modeset flow programs PHY/PLL for the pixel clock, writes video timing and frame polarity/interlace fields, configures AVI/audio/vendor infoframes and audio clock regeneration, then enables the controller. HPD flow uses HPD status/control/interrupt registers, DDC flow sequences I2C transactions through DDC control/data/status registers, and HDCP flow uses the HDCP control/status/DDC/SHA/register-port block for authentication. CEC flow uses transmit/receive data, retry/status, address, timing, and interrupt registers.

## State and Persistence Behavior
Runtime state includes controller enable/encryption mode, active video timings, infoframe payloads, audio clock regeneration values, DDC transaction state, HDCP authentication/key/SHA state, HPD masks/status, CEC transmit/receive state, PHY power/reset/PLL state, and QSERDES calibration/tuning. This hardware state is reprogrammed on hotplug, modeset, audio changes, HDCP transitions, CEC activity, and resume.

## Dependencies and Integration Points
The generated macros are used by `hdmi.c`, `hdmi_bridge.c`, `hdmi_hpd.c`, `hdmi_hdcp.c`, and per-SoC PHY drivers. Integration points include DRM bridge/connector helpers, EDID/DDC, HDMI audio, HDCP core policy, CEC framework, hotplug handling, clock framework, regulator/reset management, and SoC-specific PHY tuning tables.

## Risks
This file has many hardware generations in one XML, so register-name collisions and same-offset aliases must be handled by the correct domain. HDCP and DDC status/ack/mask bits are sequencing-sensitive and can deadlock authentication or EDID reads. Infoframe length/checksum and ACR fields must match HDMI spec expectations. QSERDES PLL fields are dense and generation-specific; wrong values can break high pixel clocks or hotplug recovery.

## Test Signals
Signals include generated-header build, HDMI hotplug and EDID reads, modesets across pixel-clock ranges, AVI/audio/vendor infoframe validation, audio playback and ACR checks, HDCP authentication success/failure paths, DDC timeout/NACK handling, CEC transmit/receive tests, suspend/resume, and PHY lock/status validation for each supported SoC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/display/hdmi.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/display/mdp4.xml -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/display/mdp4.xml

## Purpose
This XML describes the MSM MDP4 display controller register map. It covers overlay mixers, DMA engines, pipes, CSC tables, layer-mixer routing, interrupts, interface selection, LCDC/DTV timing, LVDS control, cursor state, scaling, format packing, flush/kick registers, and gamma/LUT state.

## Important APIs, Types, and Functions
Generated APIs include `REG_MDP4_*` address macros, array helpers for overlay, DMA, pipe, CSC, LUT, LCDC, and DTV blocks, plus bitfield packers for formats, polarity, active/display timing, layer routing, and IRQ masks. Important enums and bitsets include `mdp4_pipe`, `mdp4_mixer`, `mdp4_intf`, `mdp4_cursor_format`, `mdp4_frame_format`, `mdp4_scale_unit`, `mdp4_dma`, `mdp4_layermixer_in_cfg`, `MDP4_IRQ`, `mdp4_ctrl_polarity`, `mdp4_active_hctl`, and display timing bitsets. It imports shared display types from `display/mdp_common.xml`.

## Control Flow
MDP4 KMS code programs source pipes with framebuffer base/stride/format/unpack/scaling/CSC state, routes pipes into mixer stages, programs overlay or DMA output state, flushes changed blocks with `OVERLAY_FLUSH`, then kicks overlay/DMA blocks to latch the update. Encoder paths program LCDC, DTV, LVDS, DSI-video, or DSI-command interface selection and timing registers. IRQ flow uses `INTR_ENABLE`, `INTR_STATUS`, and `INTR_CLEAR` for vblank, overlay done, DMA done, histogram, read-pointer, and underrun events.

## State and Persistence Behavior
Runtime state includes pipe source addresses, strides, formats, scaling phase steps, CSC matrices, mixer-stage routing, alpha/transparency, cursor image/position/blend state, DMA/LUT state, interface timings, LVDS mux/PHY settings, interrupt masks, and pending flush bits. This state is hardware-resident and is reconstructed by atomic modeset/plane update paths after reset, suspend, or display pipeline disable.

## Dependencies and Integration Points
The map is consumed by `disp/mdp4` KMS, plane, CRTCs, IRQ, LCDC/DTV/LVDS encoders, DSI integration, HDMI/DTV output, DRM atomic plane state, framebuffer format handling, and shared MDP helpers. It depends on `mdp_common.xml` for shared pixel-format, bpc, alpha, chroma, unpack, and width/height coordinate types.

## Risks
Layer mixer routing packs many pipes into one register, so stage and mixer-bit mistakes can show the wrong plane or blank output. Format/unpack/fetch-plane fields are sensitive to DRM format and modifier interpretation. Flush/kick ordering controls when register writes latch; missing flushes look like stale frames. IRQ clear/enable mistakes cause lost vblank or underrun storms. Some comments document guessed legacy interface mappings, so changes around DSI/LCDC/DTV selection require hardware verification.

## Test Signals
Useful tests include generated-header build, plane update and format tests, cursor movement/blending, scaling and CSC validation, vblank/overlay-done IRQs, underrun logging, LCDC/DTV/DSI output modes, LVDS mux cases, suspend/resume restore, and atomic modeset stress with multiple pipes and mixers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/display/mdp4.xml -->
