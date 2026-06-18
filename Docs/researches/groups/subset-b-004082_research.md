# Research Report: subset-b-004082

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/adv7180.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/adv7180.c

## Purpose
`adv7180.c` is a V4L2 I2C subdevice driver for Analog Devices ADV7180-family SD analog video decoders, including ADV7180/7182 and ADV728x variants with optional MIPI CSI-2 and I2P/VPP blocks. It exposes an analog TV decoder source pad with standard selection/detection, input routing, basic image controls, test patterns on supported chips, power/reset sequencing, interrupt-driven source-change events, and media bus configuration for either BT.656 parallel output or single-lane CSI-2.

## Important APIs, Types, and Functions
- `struct adv7180_state` is the persistent driver state: V4L2 subdev/control handler/media pad, mutex, IRQ and GPIOs, current standard, input, field mode, streaming flag, paged register selection, optional `csi_client`/`vpp_client`, chip info, and `force_bt656_4`.
- `struct adv7180_chip_info` selects chip-specific flags, valid input mask, init routine, standard setter, and input selector.
- `adv7180_read()`/`adv7180_write()` implement paged 16-bit register access through `ADV7180_REG_CTRL`; callers must hold `state->mutex`.
- `adv7180_reset_device()`, `init_device()`, and `adv7180_s_stream()` are the main hardware sequencing paths.
- V4L2 operations include `s_std`, `g_std`, `querystd`, `g_input_status`, `s_routing`, `s_stream`, pad format ops, `get_mbus_config`, and skip-frame reporting.
- `adv7180_irq()` reads/clears ISR3 and emits `V4L2_EVENT_SOURCE_CHANGE` when autodetect changes.

## Control Flow
Probe allocates state, reads chip data from I2C/OF match tables, acquires optional powerdown/reset GPIOs, creates ancillary CSI/VPP I2C clients when the variant flags require them, initializes the V4L2 subdevice, controls, media source pad, and hardware, then optionally requests a threaded IRQ and async-registers the subdevice. Reset toggles GPIOs, issues a software reset, optionally powers down reset-powered devices before configuration, runs the variant init table, programs the current norm and field mode, configures interrupts, and restores power. Streaming always powers the decoder down first; enabling reinitializes controls/standard/field mode and powers up, while disabling leaves the chip powered off.

## State and Persistence
Runtime state is in memory only. `curr_norm`, `input`, `field`, `streaming`, `register_page`, and control values drive later reconfiguration and suspend/resume. Register state is not trusted across reset or resume; `adv7180_resume()` calls `adv7180_reset_device()` and powers the chip back up only if it was streaming. The selected register page cache is an optimization and can be stale after external reset, but reset paths rewrite the page through normal access.

## Dependencies and Integration Points
The driver depends on Linux I2C SMBus byte data, GPIO descriptors, V4L2 subdev/control/event/media APIs, optional OF properties `adv,force-bt656-4` or `adi,force-bt656-4`, and ancillary I2C devices for CSI/VPP pages. It integrates as `MEDIA_ENT_F_ATV_DECODER` with a single source pad and publishes supported chips through I2C and OF match tables.

## Risks
- Many ADI-required register writes ignore return values, especially in CSI/VPP and input-bias programming paths; partial hardware programming can be silent.
- `querystd` temporarily changes the standard register and is correctly blocked while streaming, but any caller expecting live autodetect during streaming gets `-EBUSY`.
- CSI power sequencing uses hard-coded undocumented values and only one data lane, making board/receiver timing regressions hardware-sensitive.
- Interrupt handling assumes ISR3 read succeeds and stores it in `u8`; negative reads would be truncated.
- Variant valid-input masks are critical because invalid routing can write unsupported analog mux selections.

## Test Signals
Useful tests include probe/remove with every matched variant, GPIO reset/powerdown polarity checks, routing invalid/valid inputs, standard set/query across PAL/NTSC/SECAM, streaming enable/disable and suspend/resume while streaming, media bus config for BT.656 vs CSI variants, V4L2 control writes including hue inversion and fast-switch/test-pattern paths, IRQ source-change event delivery, and capture tests that confirm the two initial skipped frames avoid garbage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/adv7180.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/adv7183.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/adv7183.c

## Purpose
`adv7183.c` is a legacy V4L2 I2C subdevice driver for the Analog Devices ADV7183 analog video decoder. It configures a default CVBS input, supports V4L2 standard selection/autodetection, input/output routing, simple image controls, GPIO reset/output-enable handling, and a fixed UYVY BT.656-style media bus format.

## Important APIs, Types, and Functions
- `struct adv7183` stores the V4L2 subdev/control handler, selected standard/input/output, reset and output-enable GPIOs, and active frame format.
- `adv7183_init_regs` is the static register programming sequence for 27 MHz clock, CVBS on AIN5, clamp/filter/ADC settings, and ADI-recommended writes.
- `adv7183_read()`, `adv7183_write()`, and `adv7183_writeregs()` are raw SMBus helpers.
- `adv7183_s_std()` maps V4L2 analog standards to ADV7183 input-control standard bits; `adv7183_querystd()` enables autodetect, reads `STATUS_1`, and restores the configured standard.
- `adv7183_s_routing()` maps public input/output IDs from `<media/i2c/adv7183.h>` to input/output control bits.
- Control, pad, video, and optional debug-register ops provide the V4L2 interface.

## Control Flow
Probe checks SMBus support, allocates state, obtains mandatory reset and output-enable GPIOs, initializes the subdevice and controls, sets PAL/composite4/8-bit defaults, deasserts reset after delays, writes the init register table, programs the default standard and format, and applies default controls. Streaming only toggles the OE GPIO. There is no async media registration in this driver; it relies on legacy subdev registration by the host V4L2 device.

## State and Persistence
`std`, `input`, `output`, and `fmt` are cached in memory. The register table and default controls are only applied at probe, not on runtime stream toggles. The output-enable GPIO is the main stream state, but no explicit `streaming` boolean is stored. EDID, media graph state, and persistent storage are not involved.

## Dependencies and Integration Points
The driver depends on SMBus byte data, descriptor GPIOs named `reset` and `oe`, V4L2 subdev/control APIs, and the public ADV7183 routing constants. The register symbolic names come from `adv7183_regs.h`. It exposes a decoder subdevice to board-level capture drivers rather than creating a full media entity graph.

## Risks
- Register write failures are mostly ignored in `adv7183_writeregs()`, routing, controls, reset, and format setup.
- There is no mutex around register access or state changes, so concurrent controls/routing/streaming depend on upper-layer serialization.
- Probe sets the consumer name for `reset_pin` twice; the OE GPIO name call targets `reset_pin`, which looks like a copy-paste bug.
- `querystd()` intersects the detected value with the caller's incoming mask (`*std &= ...`), so callers must pass a broad mask or may receive zero.
- The brightness negative-value conversion is non-obvious and may not match signed register expectations.

## Test Signals
Test with real ADV7183 hardware or I2C emulation for probe delays, mandatory GPIO polarity, init sequence, input mux selections, 8/16-bit output routing, PAL/NTSC/SECAM standard programming and autodetect restoration, OE toggling on stream start/stop, and V4L2 controls for brightness/contrast/saturation/hue. Static review should also flag missing error propagation in register sequences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/adv7183.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/adv7183_regs.h -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/adv7183_regs.h

## Purpose
`adv7183_regs.h` provides symbolic register offsets for the ADV7183 decoder. It is a pure local header used by `adv7183.c` to make register scripts, log-status dumps, controls, routing, standard detection, and debug access readable.

## Important APIs, Types, and Functions
The file exports preprocessor constants only. Major groups include input/output and autodetect registers (`ADV7183_IN_CTRL`, `ADV7183_VD_SEL`, `ADV7183_OUT_CTRL`, `ADV7183_AUTO_DET_EN`), controls (`CONTRAST`, `BRIGHTNESS`, `HUE`, saturation/offset), status/identity registers, clamp/filter/gain/ADC registers, sync/window/VBI registers, and SD timing/saturation/drive-strength registers.

## Control Flow
There is no runtime control flow. The header is included before use by `adv7183.c`, and constants are compiled into register reads/writes.

## State and Persistence
The header has no state. Its values define the hardware state locations that the driver reads and writes.

## Dependencies and Integration Points
It depends only on inclusion from C code that already has kernel integer types available if needed. The integration point is the ADV7183 register map expected by `adv7183.c`; mismatched constants would directly misprogram the chip.

## Risks
- Constants are untyped macros, so invalid use is not compiler-constrained.
- The header does not define masks or bit shifts for most fields; callers encode magic values in the C file.
- No register access width metadata is present, but the driver assumes all offsets are byte-addressable SMBus byte registers.

## Test Signals
Validation is by compile coverage and hardware behavior: log-status register names should match the datasheet, init-script writes should land on intended offsets, and debug register access should read expected identity/status values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/adv7183_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/adv7343.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/adv7343.c

## Purpose
`adv7343.c` is a V4L2 I2C subdevice driver for the Analog Devices ADV7343 SD/ED/HD video encoder, focused here on SD analog output. It programs video standard subcarrier frequency, selects composite/component/S-Video DAC routing, exposes brightness/hue/gain controls, and optionally consumes platform/OF endpoint properties for DAC power configuration.

## Important APIs, Types, and Functions
- `struct adv7343_state` stores subdev/control handler, platform data, cached register shadows (`reg00`, `reg01`, `reg02`, `reg35`, `reg80`, `reg82`), selected output, and selected V4L2 standard.
- `adv7343_init_reg_val` is the reset/default register table.
- `stdinfo[]` maps V4L2 standards to ADV7343 SD standard bits and 32-bit FSC values.
- `adv7343_setstd()` writes SD mode, input mode, FSC registers, and SD filter bits.
- `adv7343_setoutput()` powers/selects DAC paths and applies platform data for DAC enable maps.
- `adv7343_get_pdata()` reads optional OF endpoint properties such as `adi,dac-enable` and `adi,sd-dac-enable`.
- The V4L2 surface is `s_std_output`, `s_routing`, log-status, and three controls.

## Control Flow
Probe checks SMBus, allocates state, loads platform data, initializes register shadows/default NTSC composite output, initializes V4L2 controls, applies default control values, writes the initialization table, programs output and standard, and async-registers the subdevice. Standard and routing calls short-circuit if state already matches, otherwise write hardware and update cached state on success.

## State and Persistence
The driver maintains shadow copies for registers it modifies so bitfield updates can preserve unrelated fields. Selected `std` and `output` are in-memory only. There is no suspend/resume path, no stream state, and no persistent storage; hardware is initialized at probe and then modified by V4L2 calls.

## Dependencies and Integration Points
It depends on SMBus byte writes, V4L2 async subdevice registration, controls, OF graph endpoint parsing, public platform data from `<media/i2c/adv7343.h>`, and `adv7343_regs.h`. It integrates as a video encoder controlled by an upstream bridge or capture/display pipeline through subdev routing and standard-output operations.

## Risks
- The driver has no locking around register shadows, so concurrent controls/routing/std changes may race.
- `adv7343_setstd()` writes FSC bytes through a pointer to host-endian `u32`; this assumes the intended byte order is little-endian.
- Some platform-data bit clearing expressions are ineffective when the configured value is zero, because they clear by shifting zero.
- It supports no SECAM and returns `-EINVAL` for unsupported standards.
- No runtime PM or reinitialization means external reset/power loss would desynchronize hardware from cached state.

## Test Signals
Test standard selection across NTSC, PAL variants, PAL60, and NTSC443 with oscilloscope/video output validation; output routing for composite/component/S-Video DAC power bits; OF property parsing for DAC maps; brightness/hue/gain register writes; async registration/remove cleanup; and concurrent V4L2 operation stress if used by a multi-threaded bridge.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/adv7343.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/adv7343_regs.h -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/adv7343_regs.h

## Purpose
`adv7343_regs.h` defines the ADV7343 encoder register offsets, reset/default values, bit masks, SD/HD mode constants, output power presets, and V4L2 control ranges used by `adv7343.c`.

## Important APIs, Types, and Functions
- `struct adv7343_std_info` binds an encoder SD standard value, FSC value, and V4L2 standard ID.
- Register macros cover power, mode select, mode register 0, DAC level, soft reset, HD mode registers, SD mode registers, FSC registers, CGMS/WSS, hue, and brightness.
- Bit masks define input mode, RGB/YUV output, soft reset, HD standards/sync/gamma/filter controls, SD standard/filter/pedestal/pixel-valid controls, and DAC disable bits.
- Control range macros define brightness, hue, and gain min/max/default values.

## Control Flow
There is no runtime code. The C driver consumes these constants to assemble init sequences and bitfield updates.

## State and Persistence
The header has no state. Default-value macros seed the driver's register shadows and initialization table, indirectly determining hardware state after probe.

## Dependencies and Integration Points
It expects V4L2 standard types to be visible through the including C file. It is tightly coupled to `adv7343.c` and the public platform data header.

## Risks
- Duplicate `ADV7343_SD_MODE_REG8_DEFAULT` definitions can hide accidental divergence.
- Untyped masks invite incorrect `&` versus `|` use in callers.
- Some HD constants are defined even though the driver path mostly programs SD output, so unused definitions may drift from datasheet expectations.

## Test Signals
Compile coverage plus hardware register dumps after probe are the main signals. Compare the init table and standard/output transitions against datasheet defaults, especially power-mode, SD mode 1/2, and FSC registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/adv7343_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/adv7393.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/adv7393.c

## Purpose
`adv7393.c` is a V4L2 I2C subdevice driver for the Analog Devices ADV7393 video encoder. It is derived from the ADV7343 driver and supports SD analog standards except SECAM, composite/component/S-Video output routing, brightness/hue/gain controls, and initialization of ADV7393-specific SD/HD registers.

## Important APIs, Types, and Functions
- `struct adv7393_state` contains subdev/control handler, register shadows, current output, and V4L2 standard.
- `adv7393_init_reg_val` is the probe-time register initialization sequence.
- `stdinfo[]` maps standards to SD mode values and FSC values.
- `adv7393_setstd()` writes SD standard bits, SD input mode, FSC registers, and NTSC pedestal enable/disable.
- `adv7393_setoutput()` chooses DAC power values and SD DAC output 1 behavior for component versus other outputs.
- V4L2 operations are log-status, `s_std_output`, `s_routing`, and controls for brightness/hue/gain.

## Control Flow
Probe checks SMBus, allocates state, seeds register shadows from header defaults, sets default NTSC composite output, initializes controls and applies them, then writes the init sequence and programs output/standard. Unlike ADV7343, it does not async-register the subdevice in probe; it relies on legacy V4L2 device registration. Remove unregisters the subdevice and frees controls.

## State and Persistence
Cached register shadows are used for bitfield updates. `std` and `output` prevent redundant hardware writes. There is no streaming state, no runtime PM, no reset recovery, and no persistent storage.

## Dependencies and Integration Points
The file depends on SMBus byte writes, V4L2 subdev/control APIs, public IDs from `<media/i2c/adv7393.h>`, and local register definitions. It integrates as a sink-side encoder subdevice controlled by an upstream video pipeline.

## Risks
- No locking protects cached registers or hardware writes.
- Register writes in control setup are applied before `adv7393_initialize()`, so defaults may be overwritten by the later init table and re-applied only if the control handler setup is called again.
- No OF/platform data path exists for board-specific DAC mappings.
- Unsupported standards return `-EINVAL`; SECAM is explicitly unsupported.
- External power/reset events can desynchronize hardware from cached state.

## Test Signals
Validate probe/remove, init register table, composite/component/S-Video DAC routing, standard-to-FSC programming byte order, pedestal changes for NTSC-like modes, V4L2 control ranges and register writes, and behavior under repeated `s_std_output`/`s_routing` calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/adv7393.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/adv7393_regs.h -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/adv7393_regs.h

## Purpose
`adv7393_regs.h` supplies ADV7393 register offsets, defaults, bit masks, output presets, SD timing constants, and control ranges for `adv7393.c`.

## Important APIs, Types, and Functions
- `struct adv7393_std_info` describes the SD standard bits, FSC value, and V4L2 standard ID.
- Register macros cover power/mode/DAC/soft-reset, HD mode, SD mode, SD timing, FSC, CGMS/WSS, hue, and brightness registers.
- Bit masks cover input mode, RGB/YUV output selection, SD brightness/WSS split, soft reset, HD timing/sync/filter controls, SD standard/filter/pedestal/square-pixel/pixel-valid controls, DAC output 1, and control min/max/defaults.

## Control Flow
No executable control flow is present. Constants are expanded into the ADV7393 driver's initialization and update paths.

## State and Persistence
The header has no state; default macros seed `adv7393_state` register shadows and hardware initialization.

## Dependencies and Integration Points
The header is local to the I2C media driver and assumes V4L2 standard ID types are available from the including source. It is coupled to the register semantics in `adv7393.c`.

## Risks
- Untyped macros and magic masks can be combined incorrectly by callers.
- Definitions for HD modes are mostly unused by the current C driver, increasing drift risk.
- Register defaults are a behavior contract; changing them affects probe-time hardware state.

## Test Signals
Compile coverage, register dump comparison after initialization, FSC register byte values for each standard, and checks that SD mode register 2 pedestal/DAC bits match output and standard selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/adv7393_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/adv748x/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/adv748x/Makefile

## Purpose
The ADV748x Makefile defines how the composite `adv748x` driver object is built from its functional modules and gates it behind `CONFIG_VIDEO_ADV748X`.

## Important APIs, Types, and Functions
It declares `adv748x-objs` as `adv748x-afe.o`, `adv748x-core.o`, `adv748x-csi2.o`, and `adv748x-hdmi.o`, then adds `adv748x.o` to the build when the Kconfig symbol is enabled.

## Control Flow
There is no runtime control flow. Build order and object aggregation ensure all module-local symbols are linked into one driver.

## State and Persistence
No runtime state. The file controls build-system state only.

## Dependencies and Integration Points
It integrates with kbuild and the surrounding media I2C driver Kconfig. The object list mirrors the internal source split: core parent driver, analog front end, HDMI receiver, and CSI-2 transmitters.

## Risks
- Omitting any object breaks internal symbol resolution such as `adv748x_hdmi_init()` or `adv748x_tx_power()`.
- Adding a new ADV748x source file requires updating this list.

## Test Signals
Build `CONFIG_VIDEO_ADV748X=m` and `=y`, confirm the linked module exports one I2C driver, and verify no unresolved symbols from the split source files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/adv748x/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/adv748x/adv748x-afe.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/adv748x/adv748x-afe.c

## Purpose
`adv748x-afe.c` implements the ADV748x analog front end and standard definition processor V4L2 subdevice. It handles analog input selection, analog TV standard setting/detection, source format reporting, controls for brightness/contrast/saturation/hue/test pattern, and stream-time power-up of the selected CSI-2 transmitter.

## Important APIs, Types, and Functions
- `struct adv748x_afe` is defined in `adv748x.h` and stores pads, controls, format, selected TX, streaming flag, current norm, and input.
- `adv748x_afe_status()` reads the SDP read-only map and translates lock/standard bits to V4L2 status and standards.
- `adv748x_afe_std()` maps V4L2 analog standards to SDP `VID_SEL` values.
- `adv748x_afe_s_input()` writes the SDP input mux.
- Video ops include `g_std`, `s_std`, `querystd`, `g_tvnorms`, `g_input_status`, and `s_stream`.
- Pad ops report a fixed `MEDIA_BUS_FMT_UYVY8_1X16` source format and propagate a fixed pixel rate to the connected CSI-2 TX.

## Control Flow
Initialization seeds NTSC-M, picks the first declared AIN endpoint as the default input, initializes one source and eight sink pads, and registers controls. Standard queries lock the global mutex, refuse to run while streaming, switch to autodetect, sleep for detection, read status, and restore the previous standard. Streaming locks the parent, optionally reselects input, powers the linked TX through `adv748x_tx_power()`, records streaming state, and logs signal lock.

## State and Persistence
`input`, `curr_norm`, `streaming`, and `tx` are in-memory state. The parent mutex serializes hardware access and control writes. No state persists across driver removal; reset scripts in core reinitialize hardware, and AFE init reapplies defaults.

## Dependencies and Integration Points
This file depends on parent register helpers/macros from `adv748x.h`, the parent `adv748x_state`, V4L2 controls/subdev APIs, media pads, and an enabled media link to a CSI-2 transmitter. It is internally registered by the CSI-2 subdevice when links are built.

## Risks
- `adv748x_afe_s_input()` accepts any unsigned input value; callers depend on endpoint parsing/defaults to avoid invalid mux values.
- Pixel-rate propagation happens during active format get and can fail with `-ENOLINK`; callers may ignore that side effect.
- Control writes first select SDP map 0, but errors from later `sdp_clrset()` chains need hardware testing.
- Streaming requires `afe->tx` to be set by media link setup; a missing link can lead to null dereference unless graph construction prevents stream calls.

## Test Signals
Test endpoint-driven default input, all AIN pads, standard set/query while idle and `-EBUSY` while streaming, input status with/without analog signal, source format height for 525/625-line modes, control writes and test-pattern selection, media links to TXA/TXB, and pixel-rate propagation to the remote CSI-2 control.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/adv748x/adv748x-afe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/adv748x/adv748x-core.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/adv748x/adv748x-core.c

## Purpose
`adv748x-core.c` is the parent I2C driver for the ADV748x HDMI/analog receiver family. It creates page-specific ancillary I2C clients and regmaps, parses OF graph endpoints, resets and initializes hardware, owns global state and media link setup, powers CSI transmitters, and instantiates HDMI, AFE, TXA, and TXB subdevices.

## Important APIs, Types, and Functions
- `struct adv748x_state` in `adv748x.h` is the shared parent state.
- Register helpers `adv748x_read()`, `adv748x_write()`, and `adv748x_write_block()` wrap regmap access for each device page.
- `adv748x_initialise_clients()` and `adv748x_set_slave_addresses()` create and program ancillary page addresses.
- `adv748x_reset()` performs software reset, slave address setup, HDMI/AFE register scripts, default input, TX reset pulse, IO datapath enables, virtual channel setup, and CP freerun configuration.
- `adv748x_tx_power()` sequences TXA/TXB MIPI D-PHY/CSI power-up/down.
- `adv748x_link_setup()` updates internal HDMI/AFE-to-TX routing and IO register 0x10 lane/source bits.
- `adv748x_parse_dt()` records one endpoint per port and validates CSI-2 lane counts.

## Control Flow
Probe allocates parent state, initializes mutex and TX identity fields, parses device-tree endpoints, configures IO regmap, reads chip revision, creates all non-IO page clients/regmaps, resets hardware, initializes HDMI and AFE subdevices, then initializes TXA and TXB subdevices. TX registered callbacks later register internal HDMI/AFE subdevices and create media links. Remove cleans up subdevices, clients, endpoint node references, and mutex. Resume calls `adv748x_reset()` early to restore hardware registers.

## State and Persistence
Endpoint node references, I2C client pointers, regmaps, child subdevice state, active TX source pointers, lane counts, and mutex are held in memory. Hardware register state is reconstructed by reset/resume. Media link state affects `state->afe.tx`, `state->hdmi.tx`, and each `tx->src`; these values drive streaming power decisions.

## Dependencies and Integration Points
The core depends on I2C ancillary device support, regmap, OF graph, V4L2 fwnode endpoint parsing, V4L2 subdev/media APIs, and child modules. Device tree must expose at least one input endpoint and one output endpoint, and TXA/TXB lane counts must follow hardware constraints.

## Risks
- `adv748x_subdev_init()` uses `is_tx(adv748x_sd_to_csi2(sd))` for all subdevices; this relies on structure layout assumptions and is risky for non-TX subdevices.
- Some reset-time writes ignore return values after helper calls, so partial initialization may be missed.
- Link setup forbids multiple sources per TX but does not perform full topology validation beyond media link constraints.
- TX power contains undocumented required writes and a `WARN_ONCE` for an unknown bit; regressions are hardware/firmware sensitive.
- Endpoint parsing stores node refs before lane parse completion, so error cleanup must run to avoid leaks.

## Test Signals
Test OF graphs for ADV7481/ADV7482 variants, invalid duplicate endpoints, missing input/output endpoints, TXA lane counts 1/2/4 and invalid values, TXB one-lane enforcement, chip revision read failure paths, reset register sequence, media link enable/disable permutations, AFE-to-TXA active-lane reduction, HDMI-to-TXA restoration, suspend/resume reset, and module unload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/adv748x/adv748x-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/adv748x/adv748x-csi2.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/adv748x/adv748x-csi2.c

## Purpose
`adv748x-csi2.c` implements TXA/TXB CSI-2 transmitter V4L2 subdevices for ADV748x. It models a sink/source bridge, registers internal links from HDMI/AFE sources, propagates formats, exposes pixel-rate control, reports CSI-2 bus configuration, and delegates stream enablement to the selected upstream source.

## Important APIs, Types, and Functions
- `adv748x_csi2_set_virtual_channel()` writes the CSI virtual-channel register.
- `adv748x_csi2_register_link()` registers source subdevices as needed and creates internal media links.
- `adv748x_csi2_registered()` builds default links: HDMI to TXA enabled by default, AFE to TXB enabled by default when present, and AFE to TXA available.
- `adv748x_csi2_s_stream()` finds the remote sink source and calls its `s_stream`.
- Pad ops enumerate supported bus codes: TXA supports UYVY16 and RGB888; TXB supports UYVY16 only.
- `adv748x_csi2_set_pixelrate()` updates the read-only-style pixel-rate control from upstream format logic.

## Control Flow
Init skips disabled TX ports, initializes the subdevice and internal ops, creates sink/source pads, binds the OF endpoint for async registration, initializes controls, finalizes subdev state with the parent mutex, and async-registers. Once the TX subdevice is registered into a V4L2 device, its registered callback creates internal links to AFE/HDMI. Stream calls flow backward from TX to source subdev, where HDMI/AFE powers the transmitter.

## State and Persistence
Each `struct adv748x_csi2` tracks page, port, configured lane count, active lane count, current source pointer, pixel-rate control, and pad state. Format state is V4L2 subdev active/try state, protected by the parent mutex. Link setup in core mutates `src` and `active_lanes`.

## Dependencies and Integration Points
It depends on parent state/helpers, media entity links, V4L2 async subdev endpoint matching, and upstream HDMI/AFE subdevices. It is the externally registered endpoint for capture drivers consuming MIPI CSI-2.

## Risks
- Streaming without an enabled media link returns `-EPIPE`.
- Pixel-rate control accepts only updates through helper; direct `s_ctrl` is a no-op for valid ID.
- Format propagation is local to TX pads and does not validate remote source compatibility beyond link validation.
- TXA/TXB support different bus codes, so graph negotiation must avoid RGB888 on TXB.

## Test Signals
Test TXA/TXB registration with enabled and disabled endpoints, default link topology, media link switching, stream delegation error when unlinked, format enumeration and fallback for unsupported codes, source-pad format mirroring, `get_mbus_config` lane counts after AFE-to-TXA active-lane reduction, and pixel-rate updates from HDMI/AFE.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/adv748x/adv748x-csi2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/adv748x/adv748x-hdmi.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/adv748x/adv748x-hdmi.c

## Purpose
`adv748x-hdmi.c` implements the ADV748x HDMI receiver/component processor V4L2 subdevice. It supports HDMI signal detection, DV timings query/set/enumeration, RGB888 source format reporting, EDID storage/programming into the repeater/EDID page, picture controls, test patterns, and stream-time power control of the selected CSI-2 transmitter.

## Important APIs, Types, and Functions
- `adv748x_hdmi_timings_cap` and `adv748x_hdmi_video_standards[]` define supported CEA/DMT timings and hardware `VID_STD`/frequency codes.
- `adv748x_hdmi_query_dv_timings()` reads measured HDMI timing registers and pixel clock.
- `adv748x_hdmi_s_dv_timings()` validates timings, programs CP/IO timing registers, updates interlace bits, and caches timings.
- `adv748x_hdmi_set_edid()` caches up to four EDID blocks, writes them in SMBus-sized chunks, updates aspect ratio, and enables/disables repeater EDID.
- `adv748x_hdmi_get_format()` returns RGB888 format from cached timings and propagates pixel rate to the remote TX.
- Controls write CP brightness, contrast, saturation, hue, and pattern generator registers.

## Control Flow
Init seeds default 1280x720p30 timings, sets default 16:9 aspect ratio, initializes the subdevice, sink/source pads, and controls. Timing query returns cached timings when the pattern generator is enabled, otherwise requires signal lock, reads timing registers, fills optional V4L2 fields, and updates cached timings. Streaming locks the parent and powers the selected TX on/off, then logs HDMI lock status.

## State and Persistence
Cached `timings`, `format`, `aspect_ratio`, EDID buffer/presence/block count, selected `tx`, controls, and pads live in memory. EDID is also written into device EDID memory/repeater registers but is not persistent across reset/remove. Timings are updated by set/query and drive format dimensions and pixel rate.

## Dependencies and Integration Points
This file depends on parent regmap helpers, V4L2 DV timings helpers, HDMI/CEA timing definitions, V4L2 EDID pad ops, media links to TXA, and the shared parent mutex. It integrates as the HDMI source feeding TXA in the media graph.

## Risks
- No interrupt handling exists for cable/timing changes; comments note timings should be updated on IRQ in the future.
- `adv748x_hdmi_check_dv_timings()` loops until `stds[i].timings.bt.width` but the standards array has no explicit zero sentinel, risking out-of-bounds reads.
- Pixel-rate propagation ignores the return from `adv748x_hdmi_query_dv_timings()`, so no-signal cases can push stale/zero timing data.
- EDID set validates block count but not EDID CRC/header.
- Stream power requires `hdmi->tx` to be set by media links.

## Test Signals
Test DV timings set/query for every table entry, invalid/out-of-range timings, no-signal `-ENOLINK`, interlaced height handling, format reporting and pixel-rate propagation, EDID set/get/clear with 0-4 blocks and over-limit `-E2BIG`, test pattern query behavior, HDMI-to-TXA stream on/off, and media graph link switching away from HDMI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/adv748x/adv748x-hdmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/adv748x/adv748x.h -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/adv748x/adv748x.h

## Purpose
`adv748x.h` is the shared private header for the ADV748x driver stack. It defines page IDs, OF port numbers, pad layouts, child/parent state structures, helper macros, register offsets/masks, and cross-file function prototypes.

## Important APIs, Types, and Functions
- Enums define register pages, OF ports, CSI-2 pads, HDMI pads, and AFE pads.
- `struct adv748x_csi2`, `struct adv748x_hdmi`, `struct adv748x_afe`, and `struct adv748x_state` are the core private data contracts across source files.
- Macros identify enabled endpoints and TX identity (`is_tx_enabled`, `is_txa`, `is_txb`, `is_afe_enabled`, `is_hdmi_enabled`).
- Register macros cover IO, HDMI timing, repeater/EDID, SDP, CP, and CSI TX maps.
- Helper macros wrap page-specific access (`io_read`, `hdmi_read16`, `sdp_clrset`, `cp_clrset`, `tx_write`).
- Prototypes expose core register access, subdev init, TX power, AFE/CSI2/HDMI init/cleanup, and pixel-rate/virtual-channel helpers.

## Control Flow
The header has no runtime control flow, but it defines inline helpers such as `adv748x_get_remote_sd()` that traverse media pads to remote subdevices.

## State and Persistence
It defines the in-memory state layout for all ADV748x modules. Persistent hardware state is represented by page register offsets and masks, but the header itself stores nothing.

## Dependencies and Integration Points
It depends on Linux I2C declarations and on media/V4L2 types included by each C file before use. It is the coupling layer for `adv748x-core.c`, `adv748x-afe.c`, `adv748x-csi2.c`, and `adv748x-hdmi.c`.

## Risks
- Container macros are powerful and unsafe if used with the wrong subdevice type.
- Register masks and page IDs form an implicit ABI among split source files; mistakes compile but misprogram hardware.
- The endpoint-enabled macros treat endpoint presence as feature enablement, so device-tree correctness is central.

## Test Signals
Compile all ADV748x objects together, exercise media graph creation for every port enum, validate register constants against hardware dumps, and test helper macros through HDMI/AFE/TX format and stream paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/adv748x/adv748x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/adv7511-v4l2.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/adv7511-v4l2.c

## Purpose
`adv7511-v4l2.c` is a V4L2 I2C subdevice driver for the Analog Devices ADV7511 HDMI transmitter, intentionally named to avoid conflict with the DRM ADV7511 driver. It models a digital video encoder sink with HDMI/DVI mode controls, DV timing and media-bus format programming, EDID readout from connected displays, hotplug/RX-sense handling, audio setup, optional CEC adapter support, interrupt handling, infoframe debugfs exposure, and power/stream control.

## Important APIs, Types, and Functions
- `struct adv7511_state` stores platform data, subdev/media pad/control handler, child I2C addresses and clients for EDID/packet memory/CEC, CEC adapter/address state, power/monitor flags, current DV timings and bus format/colorimetry, EDID cache, delayed work, and debugfs state.
- SMBus helpers retry main/CEC writes and main reads; `adv7511_edid_rd()` reads EDID blocks through the EDID I2C client.
- `adv7511_s_power()`, `adv7511_s_stream()`, and `adv7511_setup()` handle power, output enable, reserved-register setup, HDMI mode, audio setup, and infoframe defaults.
- Pad ops implement `get_edid`, bus code enumeration, `get_fmt`/`set_fmt`, `s_dv_timings`/`g_dv_timings`, and timings enumeration/capability.
- `adv7511_check_monitor_present_status()`, `adv7511_edid_handler()`, and `adv7511_check_edid_status()` coordinate hotplug, EDID retries, events, and CEC physical address updates.
- Optional CEC ops support adapter enable, logical address programming, transmit, TX completion, and RX message delivery.

## Control Flow
Probe requires platform data, initializes the V4L2 subdevice/internal ops and controls, creates one sink media pad, verifies chip ID, creates dummy I2C clients for EDID, optional CEC, and packet memory, creates a single-thread workqueue, initializes hardware and interrupt state, optionally allocates the CEC adapter, enables interrupts, and checks monitor presence. Streaming enable clears output-disable bits and checks monitor status; disabling powers down and clears monitor state. Hotplug/MSEN/EDID interrupts disable IRQs, read and clear status, process monitor and EDID state, process CEC status/messages if enabled, and re-enable IRQs. EDID reads are delayed/retried through workqueue and may power-cycle the device on failures.

## State and Persistence
State is in memory. EDID data can cover up to eight 256-byte segments, tracks total blocks, read segments, retries, and completion. `dv_timings`, `fmt_code`, colorimetry, quantization, content type, monitor/power flags, and CEC logical addresses are cached and drive later register programming. Hardware is reinitialized in `adv7511_init_setup()` and on monitor detection; EDID disappears on unplug.

## Dependencies and Integration Points
The driver depends on platform data from `<media/i2c/adv7511.h>` for secondary I2C addresses and CEC clock, V4L2 subdev/control/DV timing/debugfs helpers, media entity pads, HDMI infoframe helpers, workqueues, CEC core when enabled, and SMBus byte/block operations. It integrates with board drivers through subdev notifications `ADV7511_MONITOR_DETECT` and `ADV7511_EDID_DETECT`.

## Risks
- No OF probing path; missing platform data fails probe.
- There is no explicit mutex around state/register operations, while IRQ/workqueue/control/pad paths can interleave.
- Many register writes are `void` helpers or ignore return values, so I2C failures can leave partial configuration.
- EDID retry logic power-cycles the transmitter and depends on hotplug state; flaky displays can cause repeated delayed work.
- CEC adapter registration happens in subdev `registered`; error cleanup must avoid double-free paths, especially when CEC is disabled at compile time.
- `adv7511_s_power()` returns boolean-like values despite `int` signature.

## Test Signals
Test probe failure without platform data, chip-ID mismatch, secondary I2C client creation failures, hotplug/RX-sense transitions, EDID success/failure/CRC/header validation, EDID multi-segment reads, subdev notifications, CEC logical address/transmit/RX paths, HDMI vs DVI mode control, RGB quantization auto/full/limited, bus formats RGB/YUYV/UYVY and AVI infoframe fields, DV timing validation and FPS register programming, audio sample-rate setup, stream enable/disable, IRQ masking/readback retry, debugfs infoframe reads, and remove cleanup with pending EDID work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/adv7511-v4l2.c -->
