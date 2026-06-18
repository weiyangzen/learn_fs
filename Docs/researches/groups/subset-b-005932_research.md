# subset-b-005932 Research

Grouped source research for Linux media framework headers and media I2C device contract headers under `sources/distributed-fs/ceph-client/include/media`. Each source file has a separate marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/frame_vector.h -->
# sources/distributed-fs/ceph-client/include/media/frame_vector.h

## Purpose
Defines `struct frame_vector`, the small container used by media memory paths to store pinned user virtual memory as either `struct page *` entries or raw PFNs. The source was read as a complete header.

## Important APIs, Types, and Functions
Exports `frame_vector_create()`, `frame_vector_destroy()`, `get_vaddr_frames()`, `put_vaddr_frames()`, `frame_vector_to_pages()`, `frame_vector_to_pfns()`, and inline accessors `frame_vector_count()`, `frame_vector_pages()`, and `frame_vector_pfns()`. The core fields are `nr_allocated`, `nr_frames`, `got_ref`, `is_pfns`, and flexible array `ptrs[]`.

## Control Flow
Callers allocate a vector, pin or collect frames with `get_vaddr_frames()`, convert between PFN and page views as needed, then release pins with `put_vaddr_frames()` and destroy the vector. The inline accessors lazily convert representation before returning typed pointers.

## State and Persistence Behavior
State is transient per pinning operation. `got_ref` tracks whether page references were obtained and therefore whether release work is required. `is_pfns` tracks the current interpretation of `ptrs[]`.

## Dependencies and Integration Points
Integrates with memory management, page/PFN conversion, and media/videobuf paths that need user-memory frame pinning without permanently committing to page-backed storage.

## Risks
Misinterpreting `ptrs[]`, leaking pinned pages, converting invalid PFNs to pages, or using the vector after `put_vaddr_frames()` can corrupt memory-management state. Callers must respect partial pin counts and error pointers from `frame_vector_pages()`.

## Test Signals
Compile coverage for media memory users, pin/unpin tests for writable and read-only ranges, PFN-only mapping tests, conversion failure tests, and leak/refcount checks around short pins and error unwinds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/frame_vector.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/adp1653.h -->
# sources/distributed-fs/ceph-client/include/media/i2c/adp1653.h

## Purpose
Defines register constants, intensity conversion macros, platform data, and driver-private state for the ADP1653 V4L2 flash LED subdevice.

## Important APIs, Types, and Functions
Important macros cover ADP1653 I2C address, output-select/config/strobe/fault registers, fault bits, flash/torch/indicator min-step-max ranges, and register-to-current conversion. `struct adp1653_platform_data` supplies power callback, maximum flash timeout/current limits, indicator current, and optional enable GPIO. `struct adp1653_flash` embeds `v4l2_subdev`, V4L2 controls, `power_lock`, `power_count`, and cached `fault`.

## Control Flow
The C driver uses platform limits to create controls, powers the chip through callback/GPIO, writes intensity and timeout registers, starts software strobe, reads fault state, and maintains power reference counting under `power_lock`.

## State and Persistence Behavior
Header-defined state persists per flash subdevice. Control handler state mirrors user-visible V4L2 controls, while hardware register settings persist until power-off or reprogramming. `fault` caches device fault flags.

## Dependencies and Integration Points
Depends on I2C, mutexes, V4L2 controls, and V4L2 subdev. Integrates with camera sensor/flash pipelines through subdev operations and flash-class controls.

## Risks
Current conversion macros assume unit and range discipline; off-by-one range changes can overdrive LEDs. Power-count imbalance can leave hardware enabled. Fault bit handling must not hide over-temperature, timeout, over-voltage, or short-circuit conditions.

## Test Signals
Build with the ADP1653 driver, V4L2 flash control enumeration, min/max/current conversion checks, power on/off balance, software strobe behavior, fault injection/readback, and probe paths with callback versus GPIO power control.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/adp1653.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/adv7183.h -->
# sources/distributed-fs/ceph-client/include/media/i2c/adv7183.h

## Purpose
Defines board-facing input and output selector constants for the Analog Devices ADV7183 analog video decoder.

## Important APIs, Types, and Functions
Constants enumerate composite inputs `ADV7183_COMPOSITE0..10`, S-Video inputs `ADV7183_SVIDEO0..2`, component inputs `ADV7183_COMPONENT0..1`, and output widths `ADV7183_8BIT_OUT` and `ADV7183_16BIT_OUT`.

## Control Flow
No executable flow is present. Bridge drivers pass these selector values to routing or initialization code in the ADV7183 driver.

## State and Persistence Behavior
No state is owned. The constants describe hardware mux selections that become persistent only when the driver writes ADV7183 registers.

## Dependencies and Integration Points
Used by board files or bridge drivers that instantiate the ADV7183 subdevice and configure analog input routing and bus width.

## Risks
Selector values are hardware ABI. A wrong mapping connects the wrong AIN pins or programs the wrong output bus mode, producing missing or distorted video.

## Test Signals
Route each composite/S-Video/component input on supported boards, verify 8-bit and 16-bit output capture, and compile-test routing call sites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/adv7183.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/adv7343.h -->
# sources/distributed-fs/ceph-client/include/media/i2c/adv7343.h

## Purpose
Provides platform-data definitions for the ADV7343 video encoder, including DAC power and SD output configuration.

## Important APIs, Types, and Functions
Constants identify composite, component, and S-Video outputs. `struct adv7343_power_mode` controls sleep mode, PLL/oversampling power, and six DAC power states. `struct adv7343_sd_config` selects SD DAC outputs. `struct adv7343_platform_data` groups both.

## Control Flow
No flow is implemented. The ADV7343 driver consumes platform data during probe or mode setup to program power and SD output registers.

## State and Persistence Behavior
The header carries declarative board configuration. Persistent state resides in chip registers after the driver writes the selected power and DAC settings.

## Dependencies and Integration Points
Used by bridge/platform code that binds the ADV7343 encoder into V4L2 output pipelines.

## Risks
Incorrect DAC array values can enable wrong outputs or waste power. Sleep/PLL controls affect register accessibility and output stability.

## Test Signals
Probe with platform data, switch composite/component/S-Video outputs, validate DAC enable map against board schematic, and suspend/resume with sleep/PLL settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/adv7343.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/adv7393.h -->
# sources/distributed-fs/ceph-client/include/media/i2c/adv7393.h

## Purpose
Defines output selector IDs for the ADV7393 video encoder.

## Important APIs, Types, and Functions
Constants `ADV7393_COMPOSITE_ID`, `ADV7393_COMPONENT_ID`, and `ADV7393_SVIDEO_ID` identify supported output types.

## Control Flow
No executable flow. These IDs are consumed by encoder routing/configuration code.

## State and Persistence Behavior
No software state is owned. The IDs become persistent only through downstream register programming.

## Dependencies and Integration Points
Integrates board output-routing descriptions with the ADV7393 V4L2 subdevice driver.

## Risks
Mismatched IDs can route video to the wrong connector or format path.

## Test Signals
Build all ADV7393 users and verify each output type on hardware or register traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/adv7393.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/adv7511.h -->
# sources/distributed-fs/ceph-client/include/media/i2c/adv7511.h

## Purpose
Defines notification payloads and platform data for the ADV7511 HDMI transmitter subdevice.

## Important APIs, Types, and Functions
Notification IDs are `ADV7511_MONITOR_DETECT` and `ADV7511_EDID_DETECT`. `struct adv7511_monitor_detect` reports hotplug presence. `struct adv7511_edid_detect` reports EDID presence, segment, and physical address. `struct adv7511_platform_data` supplies secondary I2C addresses for EDID, CEC, packet memory, and the CEC clock.

## Control Flow
The driver reports monitor/EDID events to the V4L2 device notification path and uses platform I2C addresses during probe to access ADV7511 register pages.

## State and Persistence Behavior
No state is stored in the header. Runtime state is hotplug/EDID status and page-address configuration in the driver/chip.

## Dependencies and Integration Points
Depends on integer types and V4L2 subdevice notification conventions. Integrates HDMI transmitter events with bridge drivers and EDID/CEC handling.

## Risks
Wrong secondary addresses break EDID, CEC, or packet memory access. Event payloads are kernel-internal contracts; mismatched interpretation can hide hotplug or EDID changes.

## Test Signals
Hotplug interrupt tests, EDID read across segments, physical-address propagation, CEC clock configuration, and I2C page access failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/adv7511.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/adv7604.h -->
# sources/distributed-fs/ceph-client/include/media/i2c/adv7604.h

## Purpose
Defines platform configuration, pad layout, custom controls, and notification IDs for ADV7604/ADV7611 HDMI/analog video receiver drivers.

## Important APIs, Types, and Functions
Enums describe analog input muxing, RGB bus order, input color space, output format mode, drive strength, INT1 behavior, register pages, and media pads. `struct adv76xx_platform_data` includes power/cable-detect pin options, default input, analog mux, bus order, output mode, interrupt mode, sync/data polarity bits, drive strengths, output bit order, free-run mode, and per-page I2C addresses. Custom V4L2 controls configure analog sampling phase and free-run color; `ADV76XX_HOTPLUG` is the notification event.

## Control Flow
Probe consumes platform data to configure multi-page I2C clients and IO/AFE/HDMI/CP registers. Runtime routing selects pads and input modes, while control handlers adjust sampling/free-run behavior and hotplug notifications inform the bridge.

## State and Persistence Behavior
Platform data is static board policy; register programming persists in the receiver until changed or reset. Pad constants define the media-controller topology.

## Dependencies and Integration Points
Depends on Linux integer types and V4L2 control IDs. Integrates with V4L2 subdev pads, DV timing controls, EDID/hotplug handling, and board-specific I2C page addressing.

## Risks
Register-page address errors can make only some functional blocks unreachable. Bus order, polarity, and drive-strength mismatches cause corrupted video. Pad numbering differs between ADV7604 and ADV7611 source pads and must match topology code.

## Test Signals
Probe with default and overridden page addresses, HDMI hotplug/EDID, analog VGA/component routing, free-run controls, DV timing detection, bus-order validation, and media graph pad enumeration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/adv7604.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/adv7842.h -->
# sources/distributed-fs/ceph-client/include/media/i2c/adv7842.h

## Purpose
Provides the board/platform contract for the ADV7842 multi-input video decoder/receiver, including analog, HDMI, SDP, CSC, sync adjustment, EDID pad, and RAM-test controls.

## Important APIs, Types, and Functions
Enums cover analog input muxing, RGB bus order, input color space, output format mode, operation mode, video standard, selected input, and drive strength. `struct adv7842_sdp_csc_coeff` holds manual SDP color-space conversion coefficients. `struct adv7842_sdp_io_sync_adjustment` holds timing adjustment fields. `struct adv7842_platform_data` controls reset, power pins, muxing, default mode/input/standard, output formatting, LLC phase, external RAM, HDMI/SDP free-run, HPA, CSC, 525/625 sync adjustments, and many I2C page addresses. Custom V4L2 controls match ADV receiver sampling/free-run controls; `ADV7842_CMD_RAM_TEST` is a private kernel ioctl.

## Control Flow
The driver reads platform data during probe to set default mode, page clients, output bus, free-run behavior, and optional SDP timing/Csc values. Runtime routing selects HDMI/VGA/SDP inputs and may issue the RAM-test ioctl for deinterlacer memory validation.

## State and Persistence Behavior
Static platform data drives persistent chip register initialization. EDID port constants and source pad constant shape the media graph and userspace-facing topology.

## Dependencies and Integration Points
Integrates with V4L2 DV timings, media pads, EDID/hotplug handling, analog SDP/CP processing, and board-specific register-page address wiring.

## Risks
This is an ABI-heavy board contract. Wrong page addresses, mode/input defaults, external RAM settings, or timing adjustment fields can break entire receiver blocks. The private RAM-test ioctl must stay kernel-internal.

## Test Signals
HDMI/VGA/CVBS/S-Video routing, EDID port tests, free-run controls, RAM test, sync timing on 525/625-line sources, external RAM/deinterlacer operation, and media topology validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/adv7842.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/ak881x.h -->
# sources/distributed-fs/ceph-client/include/media/i2c/ak881x.h

## Purpose
Defines platform flags for AK8813/AK8814 TV encoder interface mode and output options.

## Important APIs, Types, and Functions
Macros encode interface mode mask and values for BT.656, master, and slave; `AK881X_FIELD` selects field behavior; `AK881X_COMPONENT` selects component output. `struct ak881x_pdata` contains the `flags` bitmask.

## Control Flow
No flow is present. The encoder driver reads `flags` and programs interface/output registers.

## State and Persistence Behavior
Flags are static board state and become persistent in chip registers after initialization.

## Dependencies and Integration Points
Used by board code connecting AK881x encoders to V4L2 output pipelines.

## Risks
Wrong mode bits can create bus-master conflicts, missing sync, or connector/output mismatch.

## Test Signals
Build users, validate BT.656/master/slave operation, field signaling, and component/composite output on board hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/ak881x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/bt819.h -->
# sources/distributed-fs/ceph-client/include/media/i2c/bt819.h

## Purpose
Defines internal V4L2 device notification ioctls for the BT819 decoder FIFO reset line.

## Important APIs, Types, and Functions
`BT819_FIFO_RESET_LOW` and `BT819_FIFO_RESET_HIGH` are `_IO('b', n)` kernel-internal commands used when changing input or video standard.

## Control Flow
Bridge drivers notify the BT819 subdevice to drive FIFO reset low/high around routing or standard changes.

## State and Persistence Behavior
No state is stored here. The reset state is transient hardware control.

## Dependencies and Integration Points
Depends on `linux/ioctl.h` and V4L2 device notification routing. It is not userspace ABI despite using ioctl encoding.

## Risks
Calling these in the wrong order or exposing them to userspace would create unstable capture behavior or ABI confusion.

## Test Signals
Input/standard switching while capturing, FIFO-reset register traces, and compile checks for bridge notification callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/bt819.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/cs5345.h -->
# sources/distributed-fs/ceph-client/include/media/i2c/cs5345.h

## Purpose
Defines input selector and master-clock constants for the CS5345 audio ADC.

## Important APIs, Types, and Functions
Input constants cover microphone and inputs 1 through 6. `CS5345_MCLK_*` constants encode supported master-clock ratios.

## Control Flow
No flow. Audio bridge drivers pass selectors and clock constants to the CS5345 subdevice.

## State and Persistence Behavior
The constants are declarative; actual input and clock state persists in CS5345 registers.

## Dependencies and Integration Points
Used by V4L2 analog capture boards with CS5345 audio digitizers.

## Risks
Wrong input selection yields silent or wrong audio; wrong MCLK ratio can cause invalid sampling.

## Test Signals
Audio input routing, sample-rate/clock validation, and compile coverage for callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/cs5345.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/cs53l32a.h -->
# sources/distributed-fs/ceph-client/include/media/i2c/cs53l32a.h

## Purpose
Defines input selectors for the CS53L32A audio ADC, including the second physical input's bypass/PGA modes.

## Important APIs, Types, and Functions
Macros `CS53L32A_IN0`, `CS53L32A_IN1`, and `CS53L32A_IN2` identify the three logical input modes.

## Control Flow
No flow. Routing code passes these values to the CS53L32A driver.

## State and Persistence Behavior
No state is owned by the header; selected input state persists in hardware registers.

## Dependencies and Integration Points
Used by analog capture bridge drivers that expose audio routing controls.

## Risks
Confusing logical input 1 and 2 changes whether the PGA is in path, affecting level and noise.

## Test Signals
Audio routing tests on both physical inputs, gain-path validation, and compile coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/cs53l32a.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/ds90ub9xx.h -->
# sources/distributed-fs/ceph-client/include/media/i2c/ds90ub9xx.h

## Purpose
Defines platform data for TI DS90UB9xx FPD-Link serializers connected behind a deserializer.

## Important APIs, Types, and Functions
Forward-declares `struct i2c_atr`. `struct ds90ub9xx_platform_data` contains deserializer RX `port`, I2C address translator pointer `atr`, and back-channel clock rate `bc_rate`.

## Control Flow
Deserializer/serializer drivers pass this platform data when creating serializer clients so the serializer can use the correct RX port, ATR, and back-channel timing.

## State and Persistence Behavior
The data is static relationship state between deserializer port, remote serializer, and ATR. Back-channel rate persists in link configuration after programming.

## Dependencies and Integration Points
Depends on I2C ATR infrastructure and FPD-Link media topology drivers. Integrates remote I2C devices with media graph endpoints.

## Risks
Wrong port or ATR pointer can route remote transactions to the wrong serializer. Incorrect back-channel rate can destabilize link control.

## Test Signals
Multi-port deserializer probing, remote serializer I2C access through ATR, back-channel rate changes, and link recovery after unplug/reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/ds90ub9xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/ir-kbd-i2c.h -->
# sources/distributed-fs/ceph-client/include/media/i2c/ir-kbd-i2c.h

## Purpose
Defines the shared state and initialization contract for legacy I2C infrared keyboard/remote receivers and transmitters.

## Important APIs, Types, and Functions
`DEFAULT_POLLING_INTERVAL` is 100 ms. `struct IR_i2c` stores keymap name, RX/TX I2C clients, `rc_dev`, last key byte, polling interval, delayed work, physical path, `get_key` callback, TX lock, carrier, and duty cycle. `enum ir_kbd_get_key_fn` selects built-in decoder variants. `struct IR_i2c_init_data` provides keymap, device name, protocol mask, polling interval, custom/built-in get-key choice, and optional preallocated `rc_dev`.

## Control Flow
The driver periodically polls the I2C receiver with delayed work, calls `get_key()` to decode protocol/scancode/toggle, reports through rc-core, and uses the mutex to avoid polling while transmitting IR.

## State and Persistence Behavior
Runtime state persists for the I2C IR client: polling work, previous byte for repeat suppression, rc-core device, carrier/duty settings, and callback selection.

## Dependencies and Integration Points
Depends on rc-core, I2C clients, mutexes, delayed work, and board-provided init data. Integrates legacy capture cards with the Linux input/RC subsystem.

## Risks
Polling interval and `old` repeat suppression can drop legitimate keys or flood repeats. Custom callbacks must fill protocol/scancode/toggle consistently. TX/RX locking is required to avoid bus conflicts.

## Test Signals
Polling and key repeat behavior, built-in get-key variants, custom callback devices, rc-map selection, IR transmit while receive polling is active, and module unload cancelling delayed work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/ir-kbd-i2c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/lm3560.h -->
# sources/distributed-fs/ceph-client/include/media/i2c/lm3560.h

## Purpose
Defines constants and platform data for TI LM3559/LM3560 dual LED flash devices.

## Important APIs, Types, and Functions
Macros define names, I2C address, flash brightness range/conversion, timeout range/conversion, and torch brightness range/conversion. Enums identify LEDs and peak current settings. `struct lm3560_platform_data` contains peak current, maximum flash timeout, per-LED flash brightness, and per-LED torch brightness.

## Control Flow
The driver uses platform limits to initialize V4L2 flash controls and converts requested currents/timeouts into register values before programming LEDs.

## State and Persistence Behavior
Platform data is static per board. Hardware brightness, timeout, and peak-current state persists until changed or power-cycled.

## Dependencies and Integration Points
Depends on V4L2 subdev declarations and integrates camera flash controls with LED current limits.

## Risks
Conversion macros clamp below-min values to zero but do not validate above-max by themselves. Wrong peak current or LED array ordering can exceed board limits.

## Test Signals
Control min/max/step checks, register conversion round trips, dual-LED operation, timeout behavior, and peak-current programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/lm3560.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/lm3646.h -->
# sources/distributed-fs/ceph-client/include/media/i2c/lm3646.h

## Purpose
Defines constants and platform data for TI LM3646 LED flash controllers.

## Important APIs, Types, and Functions
Macros provide device name, revision-specific I2C addresses, total flash and torch brightness ranges/conversions, strobe timeout ranges/conversions, and LED limits. The platform-data type records torch/flash current limits and timeout policy for the driver.

## Control Flow
The driver detects address/revision, creates V4L2 flash controls from platform limits, and programs total current and timeout registers using conversion macros.

## State and Persistence Behavior
Configuration is static board policy plus persistent chip register state while powered.

## Dependencies and Integration Points
Depends on V4L2 subdev and camera flash control integration.

## Risks
Total-current limits apply across LED outputs; treating them as independent per-channel limits can overrun the package or power supply. Revision address mismatch can fail probe.

## Test Signals
Probe both revision addresses, control range validation, flash/torch current conversion tests, timeout tests, and thermal/current-limit fault behavior in the implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/lm3646.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/m52790.h -->
# sources/distributed-fs/ceph-client/include/media/i2c/m52790.h

## Purpose
Defines routing constants for the Mitsubishi M52790 A/V switch used on analog capture boards.

## Important APIs, Types, and Functions
The header declares input selector constants for tuner, line, S-Video, and component-like paths plus output selector/control constants used by `s_routing`.

## Control Flow
Bridge drivers call routing operations with these constants; the M52790 driver maps them to switch register fields.

## State and Persistence Behavior
No state is stored here. The selected A/V route persists in the hardware switch until changed.

## Dependencies and Integration Points
Used by V4L2 bridge drivers that route analog audio/video through the M52790 subdevice.

## Risks
Input/output selector drift breaks board routing and may mix audio/video from different sources.

## Test Signals
Exercise all routed inputs and outputs, compare audio/video source pairing, and compile-test bridge call sites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/m52790.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/mt9t112.h -->
# sources/distributed-fs/ceph-client/include/media/i2c/mt9t112.h

## Purpose
Defines platform flags for the MT9T112 camera sensor.

## Important APIs, Types, and Functions
The header exposes sensor flags and `struct mt9t112_platform_data`, which carries board-specific flags such as bus signal polarity or orientation choices consumed by the sensor driver.

## Control Flow
The MT9T112 driver reads platform data during probe and format setup to configure sensor output behavior.

## State and Persistence Behavior
Platform data is static; resulting orientation/bus state persists in sensor registers.

## Dependencies and Integration Points
Integrates board files with a V4L2 camera sensor subdevice.

## Risks
Wrong flags can invert sync, select an incompatible bus mode, or produce flipped images unexpectedly.

## Test Signals
Probe with platform data, stream start, frame orientation checks, and parallel bus signal validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/mt9t112.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/mt9v011.h -->
# sources/distributed-fs/ceph-client/include/media/i2c/mt9v011.h

## Purpose
Defines platform data for the MT9V011 image sensor.

## Important APIs, Types, and Functions
`struct mt9v011_platform_data` supplies an external clock frequency to the sensor driver.

## Control Flow
Probe or initialization code reads the clock value and programs timing/PLL assumptions.

## State and Persistence Behavior
The clock setting is static board state; sensor timing registers persist while the device is configured.

## Dependencies and Integration Points
Used by V4L2 sensor drivers on boards without firmware-described clocks.

## Risks
Wrong clock frequency breaks frame timing and exposure calculations.

## Test Signals
Frame-rate validation, pixel clock checks, sensor probe, and capture stability across requested modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/mt9v011.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/ov2659.h -->
# sources/distributed-fs/ceph-client/include/media/i2c/ov2659.h

## Purpose
Defines platform data for the OV2659 camera sensor.

## Important APIs, Types, and Functions
`struct ov2659_platform_data` contains only `link_frequency`, documented as the target pixel clock frequency.

## Control Flow
The driver uses the link frequency during probe or mode setup to configure and advertise output timing to the bridge.

## State and Persistence Behavior
The link frequency is static integration state; the header owns no runtime state.

## Dependencies and Integration Points
Integrates the OV2659 V4L2 sensor with CSI/parallel receiver timing.

## Risks
Incorrect link frequency causes receiver timing mismatch and can make advertised pixel/link rate controls wrong.

## Test Signals
Probe, stream start/stop, link-frequency control exposure, and receiver timing validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/ov2659.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/ov7670.h -->
# sources/distributed-fs/ceph-client/include/media/i2c/ov7670.h

## Purpose
Defines platform configuration for the OV7670 camera sensor.

## Important APIs, Types, and Functions
`struct ov7670_config` carries minimum width/height, clock speed, PLL bypass, clock divider, and optional power/reset GPIO behavior for board integration.

## Control Flow
Probe and mode setup consume the config to constrain supported formats and program sensor clocking.

## State and Persistence Behavior
Configuration is static board policy; clocking and mode state persist in sensor registers.

## Dependencies and Integration Points
Used by V4L2 camera bridges using OV7670 on parallel buses.

## Risks
Clock/divider mismatches create invalid frame timing. Minimum geometry constraints must match bridge crop/format expectations.

## Test Signals
Probe, format enumeration, frame-rate verification, power/reset sequence, and capture at minimum and common VGA/QVGA modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/ov7670.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/ov772x.h -->
# sources/distributed-fs/ceph-client/include/media/i2c/ov772x.h

## Purpose
Defines platform and image-processing configuration for OV772x camera sensors.

## Important APIs, Types, and Functions
Flags `OV772X_FLAG_VFLIP` and `OV772X_FLAG_HFLIP` set orientation. `struct ov772x_edge_ctrl` stores edge enhancement parameters. Macros build automatic or manual edge-control values. `struct ov772x_camera_info` carries flags and edge-control policy.

## Control Flow
The sensor driver reads orientation and edge-control settings during initialization or control setup, then programs sensor registers.

## State and Persistence Behavior
Board policy is static; programmed flip and edge settings persist until changed.

## Dependencies and Integration Points
Integrates OV772x subdevices with board orientation and image tuning.

## Risks
Manual edge parameters are bitfield-packed and mask-sensitive; invalid strength/threshold bits can produce poor image quality. Orientation flags must align with physical mounting.

## Test Signals
Image orientation tests, automatic/manual edge control, register masks, and streaming with expected sharpness/noise behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/ov772x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/rj54n1cb0c.h -->
# sources/distributed-fs/ceph-client/include/media/i2c/rj54n1cb0c.h

## Purpose
Defines platform data for the RJ54N1CB0C camera sensor.

## Important APIs, Types, and Functions
`struct rj54n1_pdata` supplies `mclk_freq` and `ioctl_high`, a boolean controlling the sensor IOCTL signal level.

## Control Flow
Probe/mode setup reads the master clock frequency and IO control polarity, then programs or sequences the sensor accordingly.

## State and Persistence Behavior
Static board data persists indirectly through sensor register and signal programming.

## Dependencies and Integration Points
Used by V4L2 camera sensor integration where board files provide clock and IO-control polarity.

## Risks
Incorrect clock frequency or IOCTL polarity can prevent probe/streaming or leave the sensor in the wrong electrical state.

## Test Signals
Sensor probe, stream start, frame timing, and `ioctl_high` polarity validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/rj54n1cb0c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/saa6588.h -->
# sources/distributed-fs/ceph-client/include/media/i2c/saa6588.h

## Purpose
Defines kernel-internal command structure and ioctls for the SAA6588 RDS decoder.

## Important APIs, Types, and Functions
`struct saa6588_command` carries `block_count`, nonblocking flag, result, userspace buffer pointer, file instance, poll table, and poll mask. Internal ioctls are `SAA6588_CMD_CLOSE`, `SAA6588_CMD_READ`, and `SAA6588_CMD_POLL`.

## Control Flow
Radio bridge drivers issue internal commands to close an RDS instance, read decoded RDS blocks, or poll for readiness.

## State and Persistence Behavior
RDS data and poll state are transient stream/file-instance state maintained by the driver/device. The header does not own storage.

## Dependencies and Integration Points
Integrates analog radio capture drivers with an I2C RDS decoder through V4L2 internal notifications.

## Risks
Structure layout, userspace buffer pointer handling, and command IDs are internal ABI between bridge and decoder; mismatches yield corrupted RDS data, bad poll masks, or unsafe copies.

## Test Signals
RDS receive tests, blocking and nonblocking read behavior, poll readiness, close cleanup, buffer copy error paths, and no-userspace-exposure checks for the internal ioctls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/saa6588.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/saa7115.h -->
# sources/distributed-fs/ceph-client/include/media/i2c/saa7115.h

## Purpose
Defines routing, clock, and optional initialization overrides for SAA7111/3/4/5-compatible analog video decoders.

## Important APIs, Types, and Functions
Macros enumerate composite/S-Video inputs, I-port output state, SAA7111-specific output formats, IDQ polarity flag, crystal frequencies, and audio-clock flags. Enums configure SAA7113 horizontal time constant, output format selection, and RTS pin functions. `struct saa7115_platform_data` allows pointer-based overrides for SAA7113 initialization table choices and register fields.

## Control Flow
The driver uses routing constants for `s_routing`, applies crystal frequency and audio-clock flags, and optionally overrides default SAA7113 init-table register fields via platform data.

## State and Persistence Behavior
Platform overrides are static board policy; routing/clock/output settings persist in decoder registers.

## Dependencies and Integration Points
Used by V4L2 analog capture bridge drivers and decoder initialization code.

## Risks
Pointer fields must remain valid for driver use. Wrong crystal frequency or RTS/output settings can break sync, VBI, audio clocking, or data format.

## Test Signals
Composite/S-Video input routing, SAA7111 and SAA7113 variant builds, crystal-frequency programming, GM7113C init override, RTS pin behavior, and VBI/output format checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/saa7115.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/saa7127.h -->
# sources/distributed-fs/ceph-client/include/media/i2c/saa7127.h

## Purpose
Defines input and output type enums for SAA7126/7/8/9 video encoders.

## Important APIs, Types, and Functions
`enum saa7127_input_type` selects normal input or test image. `enum saa7127_output_type` selects both, composite, S-Video, RGB, YUV-C, or YUV-V output modes.

## Control Flow
Encoder routing/control code consumes these enum values to program input source and output format.

## State and Persistence Behavior
No state is stored here; selected modes persist in hardware registers.

## Dependencies and Integration Points
Used by bridge drivers and the SAA7127 encoder subdevice implementation.

## Risks
Wrong output type can energize the wrong analog connector or produce incompatible signal levels.

## Test Signals
Switch output types, enable test image, verify composite/S-Video/RGB/YUV outputs, and compile all callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/saa7127.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/tc358743.h -->
# sources/distributed-fs/ceph-client/include/media/i2c/tc358743.h

## Purpose
Defines board configuration for the Toshiba TC358743 HDMI-to-CSI-2 bridge.

## Important APIs, Types, and Functions
Enums configure DDC 5V debounce and HDMI/DVI detection delay. `struct tc358743_platform_data` supplies REFCLK frequency, debounce, HDCP enable, FIFO level, PLL divisors, CSI timing counters, HDMI detection delay, and PHY auto-reset behavior.

## Control Flow
Probe and stream setup use platform data to program PLL, CSI D-PHY timing, FIFO behavior, HDMI detection, and optional HDCP/PHY reset features. The driver later adjusts CSI lane use based on pixel clock.

## State and Persistence Behavior
Platform data is static board policy. PLL, FIFO, HDMI, and CSI timing settings persist in bridge registers until reprogrammed or reset.

## Dependencies and Integration Points
Integrates HDMI receiver state with V4L2 subdev/DV timings and a downstream MIPI CSI-2 receiver.

## Risks
CSI timing values are board- and resolution-sensitive; wrong counters cause link failures. FIFO level and PLL divisors affect high-resolution stability. HDCP enablement has policy and interoperability implications.

## Test Signals
Probe with valid REFCLKs, HDMI hotplug, DVI/HDMI mode switching, high pixel-clock streaming, CSI lane negotiation, FIFO underrun/overrun behavior, and PHY auto-reset on TMDS transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/tc358743.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/tda1997x.h -->
# sources/distributed-fs/ceph-client/include/media/i2c/tda1997x.h

## Purpose
Defines platform data for NXP TDA1997x HDMI receivers.

## Important APIs, Types, and Functions
`struct tda1997x_platform_data` supplies video output bus type, width, nine port configuration bytes, DE/HS/VS/PCLK polarity inversion, per-signal clock delays, sync selections, audio output format, MCLK multiplier, audio width, layout mode, automatic layout flag, BCLK inversion, and hardware audio auto-mute.

## Control Flow
The driver consumes platform data during probe to initialize video output formatting/timing and audio output behavior.

## State and Persistence Behavior
Static platform data is converted into persistent chip register configuration for video and audio outputs.

## Dependencies and Integration Points
Integrates TDA1997x receiver subdevices with V4L2 media-bus output configuration, DV timing, and audio output routing.

## Risks
Wrong bus width, port map, polarity, delay, or sync selection corrupts captured video. Wrong audio layout/width/clock settings break embedded or external audio capture.

## Test Signals
DV timing detection, output bus format validation, DE/HS/VS/PCLK polarity and delay tests, audio layout/clock tests, and media topology checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/tda1997x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/ths7303.h -->
# sources/distributed-fs/ceph-client/include/media/i2c/ths7303.h

## Purpose
Defines platform data for the THS7303 three-channel video amplifier.

## Important APIs, Types, and Functions
`struct ths7303_platform_data` contains channel bias values `ch_1`, `ch_2`, and `ch_3`.

## Control Flow
The THS7303 driver reads per-channel bias settings during initialization and programs the amplifier accordingly.

## State and Persistence Behavior
No header-owned state; channel bias settings persist in hardware registers while configured.

## Dependencies and Integration Points
Used by analog video output pipelines needing board-specific amplifier bias control.

## Risks
Wrong channel bias values can distort output levels or leave a channel incorrectly biased for the board.

## Test Signals
Probe with platform data, per-channel signal-level validation, and compile coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/ths7303.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/tvaudio.h -->
# sources/distributed-fs/ceph-client/include/media/i2c/tvaudio.h

## Purpose
Defines I2C addresses and input selector constants for legacy TV audio decoder/control subdevices.

## Important APIs, Types, and Functions
Macros define supported chip addresses such as TDA8425, TDA9840, TDA9874/9875, TDA985x, TEA6300, TEA6420, and PIC16C54, plus input selectors `TVAUDIO_INPUT_TUNER`, `RADIO`, `EXTERN`, and `INTERN`. `tvaudio_addrs()` returns the shifted I2C probe address list terminated by `I2C_CLIENT_END`.

## Control Flow
Bridge drivers use the address list to probe supported audio chips and use input selectors to configure audio routing.

## State and Persistence Behavior
No local state. Probe and selected input state persists in the selected I2C audio chip.

## Dependencies and Integration Points
Integrates legacy analog TV capture drivers with common tvaudio I2C subdevice probing and input routing.

## Risks
Duplicate address macros and shared addresses reflect chip-family overlap; probing or routing the wrong chip can produce silent audio or wrong-source capture.

## Test Signals
Address probing, tuner/radio/external/internal input routing, chip autodetect, and compile coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/tvaudio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/tvp514x.h -->
# sources/distributed-fs/ceph-client/include/media/i2c/tvp514x.h

## Purpose
Defines input/output selectors and platform data for TI TVP514x analog video decoders.

## Important APIs, Types, and Functions
Macros define module name, BT.656 clock, and NTSC/PAL active dimensions. `enum tvp514x_input` lists composite/S-Video/component and test inputs. `enum tvp514x_output` lists output interface modes. `struct tvp514x_platform_data` supplies clock and platform-specific routing.

## Control Flow
The driver programs input mux, output bus mode, and timing according to platform data and runtime routing.

## State and Persistence Behavior
Static board data and runtime routing persist in chip registers. Standard-specific active dimensions inform format negotiation.

## Dependencies and Integration Points
Used by V4L2 bridge drivers with TVP514x decoders on BT.656-style capture buses.

## Risks
Wrong input/output constants produce no video or invalid embedded sync. Clock mismatch breaks BT.656 capture timing.

## Test Signals
Composite/S-Video/component routing, NTSC/PAL format dimensions, BT.656 sync capture, and output mode switching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/tvp514x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/tvp7002.h -->
# sources/distributed-fs/ceph-client/include/media/i2c/tvp7002.h

## Purpose
Defines platform configuration for the TI TVP7002 video decoder.

## Important APIs, Types, and Functions
`TVP7002_MODULE_NAME` identifies the driver. `struct tvp7002_config` contains clock, HS/VS polarity, and related board settings for component/RGB capture.

## Control Flow
The driver consumes config during probe and DV timing setup to program sync handling and clock expectations.

## State and Persistence Behavior
Platform configuration becomes persistent register state during operation.

## Dependencies and Integration Points
Integrates TVP7002 subdevices with V4L2 bridge drivers and analog HD video capture paths.

## Risks
Sync polarity or clock errors cause unstable or missing capture.

## Test Signals
DV timing detection, component/RGB capture, sync polarity validation, and probe on supported boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/tvp7002.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/tw9910.h -->
# sources/distributed-fs/ceph-client/include/media/i2c/tw9910.h

## Purpose
Defines board configuration for the TW9910 video decoder, especially MPOUT pin function.

## Important APIs, Types, and Functions
`enum tw9910_mpout_pin` enumerates MPOUT functions. `struct tw9910_video_info` carries bus width and MPOUT selection.

## Control Flow
Probe/configuration code programs output interface and MPOUT according to board data.

## State and Persistence Behavior
The selected output and pin mode persist in decoder registers.

## Dependencies and Integration Points
Used by V4L2 analog decoder integration on embedded boards.

## Risks
Wrong MPOUT function can break clock/sync routing. Bus-width mismatch corrupts capture data.

## Test Signals
Stream capture, MPOUT signal verification, bus-width validation, and input standard switching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/tw9910.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/uda1342.h -->
# sources/distributed-fs/ceph-client/include/media/i2c/uda1342.h

## Purpose
Defines input selector constants for the UDA1342 audio codec.

## Important APIs, Types, and Functions
The header enumerates UDA1342 input choices consumed by audio routing code.

## Control Flow
No flow. Bridge/audio drivers use the constants to program codec input routing.

## State and Persistence Behavior
No state is owned; selected input persists in codec registers.

## Dependencies and Integration Points
Used by V4L2 analog capture boards with UDA1342 audio paths.

## Risks
Wrong selector values produce silent or wrong-source audio.

## Test Signals
Audio input routing, level checks, and compile coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/uda1342.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/upd64031a.h -->
# sources/distributed-fs/ceph-client/include/media/i2c/upd64031a.h

## Purpose
Defines mode bit constants for the NEC uPD64031A ghost reduction and 3D Y/C separation chip.

## Important APIs, Types, and Functions
Macros encode ghost reduction on/off/through, 3D Y/C separation disable/composite/S-Video, composite external input, and vertical external input flags.

## Control Flow
Bridge drivers configure the subdevice with a bitmask; the chip driver writes filter/separation mode registers.

## State and Persistence Behavior
No state here; selected filter mode persists in hardware.

## Dependencies and Integration Points
Used by analog video capture pipelines that include the uPD64031A preprocessing chip.

## Risks
Wrong bitmask can bypass filters, select wrong input, or degrade composite/S-Video quality.

## Test Signals
Mode switching, composite and S-Video capture quality, ghost-reduction behavior, and register traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/upd64031a.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/upd64083.h -->
# sources/distributed-fs/ceph-client/include/media/i2c/upd64083.h

## Purpose
Defines mode constants for the NEC uPD64083 video noise-reduction/processing chip.

## Important APIs, Types, and Functions
The header provides bitfield constants for 3D noise reduction, Y/C separation, and input/output processing modes used by the subdevice driver.

## Control Flow
Bridge drivers pass mode bits to the uPD64083 driver, which programs processing registers accordingly.

## State and Persistence Behavior
No state is owned. Mode bits persist in hardware until changed.

## Dependencies and Integration Points
Used in analog video capture chains with external video processing.

## Risks
Bitfield overlap or wrong mode selection can noticeably degrade image quality or disable required processing.

## Test Signals
Enable/disable each processing mode, compare capture quality, and verify register programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/upd64083.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/wm8775.h -->
# sources/distributed-fs/ceph-client/include/media/i2c/wm8775.h

## Purpose
Defines input selector constants and platform data for the WM8775 audio ADC/mixer.

## Important APIs, Types, and Functions
Macros `WM8775_AIN1`, `AIN2`, `AIN3`, and `AIN4` are bit values that can be multiplexed into 16 input combinations. `struct wm8775_platform_data` contains `is_nova_s`, a board quirk flag.

## Control Flow
The WM8775 driver maps selector bitmasks to hardware mux registers and applies the Nova-S quirk when platform data requests it.

## State and Persistence Behavior
No local state; selected audio route and board quirk effects persist in the codec driver/hardware configuration.

## Dependencies and Integration Points
Used by analog TV/capture bridge drivers with WM8775 audio input, including boards that need Nova-S-specific settings.

## Risks
Incorrect bitmask selectors can mix unexpected inputs or produce silence; missing `is_nova_s` can use settings tuned for another board family.

## Test Signals
Single and multi-input route changes, Nova-S quirk coverage, capture audio validation, and compile coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/i2c/wm8775.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/imx.h -->
# sources/distributed-fs/ceph-client/include/media/imx.h

## Purpose
Provides a thin shared include point for i.MX media drivers.

## Important APIs, Types, and Functions
The header contains an include guard and includes `<linux/imx-media.h>`, re-exporting the platform i.MX media definitions to media drivers.

## Control Flow
No executable flow.

## State and Persistence Behavior
No state.

## Dependencies and Integration Points
Used by i.MX media source files that include the media-layer header while relying on Linux i.MX media definitions.

## Risks
Because it is a wrapper, risk is mainly include-order churn or divergence from `<linux/imx-media.h>`.

## Test Signals
Compile coverage for i.MX media drivers and include-order checks with `<linux/imx-media.h>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/imx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/ipu-bridge.h -->
# sources/distributed-fs/ceph-client/include/media/ipu-bridge.h

## Purpose
Declares the Intel IPU camera sensor bridge data model used to describe ACPI-discovered camera sensors, clocks, GPIOs, software nodes, and V4L2 async integration.

## Important APIs, Types, and Functions
The header defines constants for sensor names/properties, lane/link-frequency limits, clock names, and GPIO naming. Structures model sensor config, per-sensor instance data, software-node properties, clock data, GPIO mapping, and the bridge object. It declares helpers for initializing the IPU bridge, parsing firmware, creating software nodes, and registering async subdevices where supported.

## Control Flow
At probe, IPU drivers use bridge helpers to discover ACPI sensors, synthesize missing firmware graph/software-node properties, register clocks/GPIO lookup tables, and build V4L2 async notifiers for sensor binding.

## State and Persistence Behavior
Bridge state persists for the lifetime of the IPU device and owns synthesized property arrays, software nodes, clock/GPIO lookup state, and async match data. It does not persist across reboot.

## Dependencies and Integration Points
Integrates ACPI, software nodes, GPIO lookup, clock providers, V4L2 async notifiers, and Intel IPU camera pipeline drivers.

## Risks
Firmware synthesis is fragile: wrong lane counts, link frequencies, clock names, or GPIO polarity can prevent sensors from binding or streaming. Lifetime of software-node properties must outlive async registration.

## Test Signals
ACPI camera enumeration on IPU platforms, sensor async binding, generated graph endpoints, clock lookup, GPIO reset/power sequencing, and failure cleanup when only some sensors initialize.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/ipu-bridge.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/ipu6-pci-table.h -->
# sources/distributed-fs/ceph-client/include/media/ipu6-pci-table.h

## Purpose
Provides PCI ID table entries and device-data references for Intel IPU6-family PCI camera devices.

## Important APIs, Types, and Functions
The header defines IPU6 PCI device IDs and table rows mapping them to IPU6 device data used by the PCI driver.

## Control Flow
The PCI core matches device IDs against the table, then the driver uses the associated data to select IPU6 variant behavior.

## State and Persistence Behavior
No runtime state is owned; the table is compile-time driver match data.

## Dependencies and Integration Points
Integrates Intel IPU6 PCI probe with kernel PCI matching and variant-specific media driver data.

## Risks
Wrong ID-to-data mapping can bind a supported device with incompatible register/firmware assumptions or fail to bind a valid platform.

## Test Signals
PCI modalias matching, probe on each listed IPU6 variant, lspci ID checks, and build coverage when variant data changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/ipu6-pci-table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/jpeg.h -->
# sources/distributed-fs/ceph-client/include/media/jpeg.h

## Purpose
Declares shared JPEG marker constants for media drivers.

## Important APIs, Types, and Functions
The header defines marker byte constants for TEM, SOF0, DHT, RST, SOI, EOI, SOS, DQT, DRI, DHP, APP0, and COM.

## Control Flow
Codec or capture drivers compare JPEG marker bytes against these constants while parsing or generating JPEG headers.

## State and Persistence Behavior
No persistent state is owned.

## Dependencies and Integration Points
Integrates V4L2 codec drivers and JPEG-capable capture devices with common marker definitions.

## Risks
Marker constants must match the JPEG bitstream spec; downstream parsers must still handle truncated or malformed buffers safely.

## Test Signals
Compile coverage and codec/capture parser tests for valid headers, truncated buffers, unknown marker skipping, and marker generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/jpeg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/media-dev-allocator.h -->
# sources/distributed-fs/ceph-client/include/media/media-dev-allocator.h

## Purpose
Declares a global refcounted media-device allocator for USB devices shared by multiple drivers.

## Important APIs, Types, and Functions
When media controller and USB support are enabled, `media_device_usb_allocate()` allocates/initializes a shared `media_device`, and `media_device_delete()` drops its kref. Disabled configurations return `NULL` or no-op.

## Control Flow
USB media drivers request a shared media device during probe and delete it during disconnect/remove. The implementation manages a system-wide media-device list and releases the instance on the last put.

## State and Persistence Behavior
State persists per shared USB media device through krefs and global allocator bookkeeping. The header provides conditional stubs when unavailable.

## Dependencies and Integration Points
Depends on `CONFIG_MEDIA_CONTROLLER` and USB. Integrates composite USB media functions that need one media graph across multiple drivers.

## Risks
Reference imbalance leaks or prematurely frees the media graph. Stub behavior means callers must tolerate `NULL` when media controller or USB support is disabled.

## Test Signals
Multi-driver USB device probe/remove, repeated bind/unbind, kref leak checks, disabled-config builds, and shared graph registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/media-dev-allocator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/media-device.h -->
# sources/distributed-fs/ceph-client/include/media/media-device.h

## Purpose
Defines the top-level media-controller device object, registration API, graph object lists, media-device operations, request hooks, and device-specific initialization helpers.

## Important APIs, Types, and Functions
`struct media_device_ops` provides `link_notify`, request allocation/free/validate/queue callbacks. `struct media_device` owns parent `dev`, `media_devnode`, model/driver/serial/bus info, topology version, graph-object IDs, entity/interface/pad/link lists, notify callbacks, `graph_mutex`, source enable/disable hooks, request queue mutex/counters, debugfs directory, and request ID allocator. APIs include `media_device_init()`, cleanup/register/unregister, entity register/unregister, entity notify register/unregister, iteration macros, PCI/USB init helpers, and `media_set_bus_info()`.

## Control Flow
Drivers initialize `media_device`, register entities and links, then register the media device as the final step. Link changes may call `link_notify` under `graph_mutex`. Request queueing validates under `req_queue_mutex`, queues non-buffer objects before buffers, and must not fail after queue callback starts. Entity registration populates graph lists and invokes notify callbacks.

## State and Persistence Behavior
`media_device` is long-lived per physical media device. It persists graph topology, object IDs, request counters, source ownership hooks, and debugfs state until unregister/cleanup. Topology version is monotonic for graph changes.

## Dependencies and Integration Points
Depends on media devnodes and media entities plus Linux device, PCI, platform, mutex, atomic, and list APIs. Integrates V4L2/DVB/RC/media drivers with `/dev/media*`, media controller ioctls, request API, and board-level source arbitration.

## Risks
Registration ordering matters: exposing the device before the graph is complete can race userspace. Link and source handlers require `graph_mutex`. Request queue ordering is critical because queuing buffers can start hardware processing. Unregistering an unregistered media device is documented unsafe except for the safe wrapper path.

## Test Signals
Media graph enumeration, entity/link add/remove, topology version changes, request allocate/queue/complete, link notifications, source enable/disable arbitration, PCI/USB bus-info formatting, disabled `CONFIG_MEDIA_CONTROLLER` stub builds, and cleanup after partial probe failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/media-device.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/media-devnode.h -->
# sources/distributed-fs/ceph-client/include/media/media-devnode.h

## Purpose
Defines media character-device nodes and file operation wrappers used to expose `/dev/media*`.

## Important APIs, Types, and Functions
`struct media_file_operations` mirrors read/write/poll/ioctl/compat/open/release callbacks with an owner. `struct media_devnode` contains the owning `media_device`, fops, embedded `device`, `cdev`, parent, minor, flags, and release callback. APIs include `media_devnode_register()`, `media_devnode_unregister_prepare()`, `media_devnode_unregister()`, `media_devnode_data()`, and `media_devnode_is_registered()`.

## Control Flow
Registration allocates a dynamic minor and registers the cdev/device. Unregister is two-stage: prepare clears the registered bit to block future opens, then unregister removes the node.

## State and Persistence Behavior
The devnode persists for the registered lifetime of a media device node. `MEDIA_FLAG_REGISTERED` tracks availability and must only be changed by core helpers.

## Dependencies and Integration Points
Depends on Linux file, cdev, device, poll, and debugfs APIs. Integrates media controller core with character-device userspace access.

## Risks
Open/unregister races are avoided only if prepare is called before unregister. Registration failure does not call release, so callers own failure cleanup.

## Test Signals
Open/ioctl through `/dev/media*`, unregister while open attempts race, compat ioctl on 64-bit kernels, release callback execution, minor allocation exhaustion, and disabled graph cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/media-devnode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/media-entity.h -->
# sources/distributed-fs/ceph-client/include/media/media-entity.h

## Purpose
Defines the media-controller graph model: graph objects, entities, pads, links, interfaces, graph traversal, pipeline streaming state, entity operations, and link creation/removal helpers.

## Important APIs, Types, and Functions
Core types are `media_gobj`, `media_entity_enum`, `media_graph`, `media_pipeline`, `media_pipeline_pad`, iterators, `media_link`, `media_pad`, `media_entity_operations`, `media_entity`, `media_interface`, and `media_intf_devnode`. Helpers generate/type-decode graph IDs, test V4L2 entity subclasses, manage entity enums, initialize pads, create pad/interface/ancillary links, setup links, find remote pads, walk graphs, start/stop pipelines, iterate pipeline pads/entities, and remove links. Macros include `media_entity_for_each_pad()`, `media_entity_call()`, and `for_each_media_entity_data_link()`.

## Control Flow
Drivers initialize pads, register entities, create links, and use `media_entity_setup_link()` to enable/disable mutable links. Pipeline start walks enabled links from an origin pad, validates links, assigns a `media_pipeline` to all connected pads, and supports nested starts via `start_count`; stop unwinds the same association. Graph-walk helpers perform depth-first traversal but are deprecated in favor of pipeline iterators.

## State and Persistence Behavior
Entities, pads, interfaces, and links are persistent graph objects owned by a `media_device`. `internal_idx` supports bitmap enumeration and can be reused after unregister. `pad->pipe` and pipeline pad lists are runtime streaming state. `use_count` is signed to catch negative-use bugs.

## Dependencies and Integration Points
Depends on bitmap, fwnode, lists, UAPI media flags, and the media device. Integrates V4L2 subdevices/video devices, firmware endpoints, media ioctls, and pipeline-aware stream validation.

## Risks
Graph mutation must be serialized by the media device graph mutex. Link flags and backlink pairs must remain consistent. `MEDIA_ENTITY_ENUM_MAX_DEPTH` limits traversal stack depth. Pad interdependency defaults to all pads interdependent when no callback exists, which can over-lock configuration. Pipeline start/stop nesting requires identical pipeline pointers.

## Test Signals
Entity/pad/link registration, mutable and immutable link setup, link validation failures, remote-pad uniqueness errors, firmware endpoint pad lookup, pipeline nested start/stop, graph traversal depth, interface link removal, and disabled media-controller builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/media-entity.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/media-request.h -->
# sources/distributed-fs/ceph-client/include/media/media-request.h

## Purpose
Defines the media request API used to bundle controls, buffers, and driver objects into an atomic-ish queueable media operation.

## Important APIs, Types, and Functions
`enum media_request_state` covers idle, validating, queued, complete, cleaning, and updating. `struct media_request` stores owning media device, kref, debug string, state, updating/access counters, object list, incomplete count, manual completion flag, poll waitqueue, and spinlock. Request APIs include lock/unlock for access/update, get/put, get by fd, allocate, manual completion marking, and completion. `struct media_request_object_ops` supplies prepare/unprepare/queue/unbind/release. `struct media_request_object` stores object ops/private pointer/request/list/kref/completed state. Object APIs initialize, bind, find, unbind, complete, get, and put objects.

## Control Flow
Userspace allocates a request fd, drivers bind objects while the request is idle/updating, queueing validates and queues objects, and completion occurs when all bound objects complete or manual completion is explicitly called. Buffer objects are appended to the end of the object list so non-buffer dependencies queue first.

## State and Persistence Behavior
Request state is refcounted and protected by `req->lock`; access locks are allowed only after complete, update locks only while idle/updating. Object refs protect embedded objects after dropping the request lock. Incomplete object count gates poll/completion.

## Dependencies and Integration Points
Depends on media-device request ops, list/slab/spinlock/refcount infrastructure, vb2 buffer request integration, and media-controller configuration.

## Risks
Incorrect state transitions return `-EBUSY` or can deadlock request updates. Failing to complete or unbind every object leaves requests permanently incomplete. Calling manual completion before all objects complete triggers warnings and delayed completion. Disabled media-controller stubs change behavior to errors/no-ops.

## Test Signals
Request fd allocation/get/put, update/access lock rejection in wrong states, object bind ordering, prepare/unprepare failure unwinds, queue callback ordering with vb2 buffers last, poll completion, manual completion, object find refcounts, and disabled-config builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/media-request.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/mipi-csi2.h -->
# sources/distributed-fs/ceph-client/include/media/mipi-csi2.h

## Purpose
Defines MIPI CSI-2 data type constants for media bus users.

## Important APIs, Types, and Functions
The header enumerates CSI-2 short packet types for frame/line start/end and generic short packets, and long packet types for null/blanking/embedded data, generic long packets, YUV420/422 variants, RGB444/555/565/666/888, RAW6/7/8/10/12/14/16/20/24/28, and user-defined types.

## Control Flow
No runtime flow. CSI-2 receiver/transmitter drivers use the constants when validating media bus formats and packet data types.

## State and Persistence Behavior
No state. Constants mirror CSI-2 protocol values.

## Dependencies and Integration Points
Integrates V4L2 media bus format negotiation and MIPI CSI-2 hardware drivers.

## Risks
Protocol constant drift breaks packet filtering or format negotiation. Generic and user-defined macros rely on callers passing values in documented ranges.

## Test Signals
CSI-2 format negotiation, RAW/YUV/RGB packet capture, embedded data routing, and compile checks for all users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/mipi-csi2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/rc-core.h -->
# sources/distributed-fs/ceph-client/include/media/rc-core.h

## Purpose
Defines the remote-controller core device model, key reporting APIs, raw IR event APIs, LIRC per-file state, and helpers for scancode extraction/encoding.

## Important APIs, Types, and Functions
`enum rc_driver_type` distinguishes scancode, raw IR RX, and raw IR TX drivers. `rc_scancode_filter`, `rc_filter_type`, `lirc_fh`, and the large `rc_dev` model device identity, rc-map, locks, raw state, input device, users, protocols, filters, key state, timers, LIRC chardev state, and driver callbacks. APIs include allocate/register/unregister/free, managed variants, `rc_keydown()`, `rc_keydown_notimeout()`, `rc_keyup()`, `rc_repeat()`, keycode lookup, raw event storage/filtering/timeout/idle, raw encoding, overflow helper, `ir_extract_bits()`, and `ir_nec_bytes_to_scancode()`.

## Control Flow
Drivers allocate an `rc_dev`, fill identity/protocol/callback fields, register it, then report decoded scancodes or raw pulse/space events. The core manages input keydown/repeat/keyup timers, protocol changes, filters, LIRC queues, and optional transmit operations.

## State and Persistence Behavior
`rc_dev` persists per remote device and owns keypress state, protocol masks, filters, input child device, timers, user count, raw decoder state, and optional LIRC file handles. `keylock` protects key state; `lock` serializes protocol setup/show/store behavior.

## Dependencies and Integration Points
Depends on spinlocks, cdev, kfifo, timers, input, LIRC UAPI, and rc-map. Integrates IR receivers/transmitters, CEC RC, input events, sysfs protocol controls, and LIRC character devices.

## Risks
Timer/key state races can leave keys stuck or repeats wrong. Protocol bitmasks must match decoder availability. Raw event duration limits and timeout handling affect decoder correctness. NEC byte helper intentionally distinguishes NEC, NECX, and NEC32 based on complement checks.

## Test Signals
Register/unregister, keydown/repeat/keyup timing, protocol enable changes, wakeup filters, LIRC open/poll/read/write, raw event overflow/timeout, NEC scancode decoding variants, transmit carrier/duty/mask callbacks, and suspend wakeup filtering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/rc-core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/rc-map.h -->
# sources/distributed-fs/ceph-client/include/media/rc-map.h

## Purpose
Defines remote-controller protocol bitmasks, scancode construction macros, keymap structures, keymap registration APIs, and the canonical names of in-kernel keymaps.

## Important APIs, Types, and Functions
Macros map `enum rc_proto` values to `RC_PROTO_BIT_*` masks and build aggregate encoder/decoder masks based on enabled Kconfig decoders. Scancode helpers cover NEC, NECX, NEC32, RC5, RC5_SZ, RC6_0, and RC6_6A. `struct rc_map_table`, `struct rc_map`, and `struct rc_map_list` define scancode/keycode tables. APIs are `rc_map_register()`, `rc_map_unregister()`, and `rc_map_get()`. Many `RC_MAP_*` string constants name built-in keytables.

## Control Flow
RC drivers set a default map name or register maps; rc-core looks up maps by name and translates scancodes into Linux input keycodes.

## State and Persistence Behavior
Registered `rc_map_list` entries persist globally while modules are loaded. Individual `rc_map` entries carry spinlock-protected table state and protocol identity.

## Dependencies and Integration Points
Depends on input keycodes and LIRC protocol UAPI. Integrates rc-core with individual keymap modules and media drivers that select default remotes.

## Risks
Keymap names are string ABI within the kernel/module ecosystem; typos break autoload/default selection. Aggregate protocol masks depend on Kconfig and must not advertise unavailable decoders.

## Test Signals
Keymap module registration/unregistration, default map lookup by every referenced name, protocol mask exposure for enabled/disabled decoders, scancode macro tests, and sorted-name maintenance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/rc-map.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/rcar-fcp.h -->
# sources/distributed-fs/ceph-client/include/media/rcar-fcp.h

## Purpose
Declares the Renesas R-Car Frame Compression Processor helper API used by display/video drivers.

## Important APIs, Types, and Functions
The header forward-declares `struct rcar_fcp_device` and exposes `rcar_fcp_get()`, `rcar_fcp_put()`, `rcar_fcp_get_device()`, `rcar_fcp_enable()`, `rcar_fcp_disable()`, and `rcar_fcp_soft_reset()`. Stubs return `ERR_PTR(-ENOENT)`, `NULL`, or success/no-op when `CONFIG_VIDEO_RENESAS_FCP` is disabled.

## Control Flow
Client drivers obtain the FCP from a device-tree node, enable it before using dependent processing/display hardware, optionally soft-reset it, disable it afterward, and release the reference during teardown.

## State and Persistence Behavior
FCP device state is owned by the implementation and persists with platform device/runtime PM lifetime. The header is a client contract.

## Dependencies and Integration Points
Integrates Renesas VSP/display/media drivers with a shared FCP block.

## Risks
Enable/disable imbalance can break power management or shared hardware access. Clients must handle `-ENOENT` and `NULL` stub behavior gracefully when FCP support is absent.

## Test Signals
Probe with and without FCP, runtime PM transitions, repeated enable/disable, soft reset behavior, stream/display start-stop, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/rcar-fcp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/tpg/v4l2-tpg.h -->
# sources/distributed-fs/ceph-client/include/media/tpg/v4l2-tpg.h

## Purpose
Defines the V4L2 test pattern generator state, supported patterns, color tables, configuration setters, geometry helpers, and buffer fill APIs.

## Important APIs, Types, and Functions
Types include RGB color structs, `enum tpg_color`, `tpg_pattern`, `tpg_quality`, video/pixel aspect enums, movement mode, color encoding, and the large `struct tpg_data`. External tables provide colors and transfer-function conversion data. APIs include `tpg_init()`, `tpg_alloc()`, `tpg_free()`, source reset, status logging, font/text generation, buffer fill, fourcc selection, crop/compose, color order, movement update, and many inline setters/getters for pattern, quality, color controls, colorspace, quantization, planes, line sizes, field, fill percentage, aspect, border/square, SAV/EAV, HDMI guard band, movement, and flips.

## Control Flow
Drivers initialize and allocate the TPG, configure format/color/geometry/pattern, then call fill helpers per plane/buffer. Setters mark `recalc_colors`, `recalc_lines`, or `recalc_square_border`, causing implementation code to rebuild cached lines/colors before generating frames. Movement counters update per frame/field.

## State and Persistence Behavior
`struct tpg_data` is persistent per generator instance and owns geometry, color configuration, format layout, recalc flags, allocated line buffers, random/contrast/black lines, and movement counters. State resets through explicit init/reset/free calls.

## Dependencies and Integration Points
Depends on V4L2 UAPI types, random/slab/vmalloc, and errno. Used by virtual/video test drivers to synthesize deterministic capture/output frames across many pixel formats.

## Risks
Plane/line-size math is format-sensitive; wrong downsampling or bytesperline handling can overrun buffers. Recalc flags must be set whenever dependent controls change. Movement and flip interaction affects static-pattern optimization.

## Test Signals
All pattern generation, RGB/YUV/HSV/luma formats, multiplanar/interleaved layouts, crop/compose scaling, h/v flip, moving square/border, text rendering, SAV/EAV and HDMI guard-band insertion, noise/static detection, and buffer-size boundary tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/tpg/v4l2-tpg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/tuner-types.h -->
# sources/distributed-fs/ceph-client/include/media/tuner-types.h

## Purpose
Defines numeric `TUNER_*` model identifiers for analog TV/radio tuner devices.

## Important APIs, Types, and Functions
The file is a large list of tuner type constants used by tuner-core, board tables, EEPROM parsers, and bridge drivers to identify exact tuner models and families.

## Control Flow
No runtime flow. Probe/configuration code stores or compares these IDs to select tuner operations and frequency ranges.

## State and Persistence Behavior
No state. Numeric IDs are compile-time internal ABI and often appear in board/eeprom mappings.

## Dependencies and Integration Points
Used by `tuner.h`, tuner-simple, bridge card tables, and EEPROM parsing such as Hauppauge TV EEPROM support.

## Risks
Renumbering or reusing IDs breaks board mappings. Adding IDs must preserve existing values and keep driver support aligned.

## Test Signals
Build all tuner users, EEPROM-to-tuner mapping checks, board-table probe on legacy devices, and no renumbering in diffs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/tuner-types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/tuner.h -->
# sources/distributed-fs/ceph-client/include/media/tuner.h

## Purpose
Defines tuner-core setup contracts, tuner mode masks, and includes the tuner model ID namespace.

## Important APIs, Types, and Functions
Includes `tuner-types.h`. `enum tuner_mode` maps radio and analog-TV modes to V4L2 tuner-type bits. `struct tuner_setup` contains I2C address, tuner type, allowed mode mask, optional tuner-specific config, and callback for bridge-controlled side effects such as GPIO reset.

## Control Flow
Bridge drivers broadcast `tuner_setup` to tuner subdevices, which accept commands only for compatible address/mode masks. Callbacks let tuner drivers ask bridges to perform component-specific actions.

## State and Persistence Behavior
Setup data is transient command payload; selected tuner mode/type persists in tuner driver state and hardware after configuration.

## Dependencies and Integration Points
Depends on kernel-only V4L2 tuner definitions and `tuner-types.h`. Integrates analog TV/radio bridge drivers, tuner-core, and tuner-simple.

## Risks
Wrong `mode_mask` causes radio-only or TV-only tuners to accept the wrong commands. `config` is untyped and must match the selected tuner. Callback component/cmd values are bridge-specific.

## Test Signals
Radio/TV mode switching, multi-tuner boards, address-specific setup, tuner callback paths, and tuner ID mapping to implementation support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/tuner.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/tveeprom.h -->
# sources/distributed-fs/ceph-client/include/media/tveeprom.h

## Purpose
Defines structures and helpers for reading and parsing Hauppauge analog TV EEPROMs.

## Important APIs, Types, and Functions
`enum tveeprom_audio_processor` identifies audio processor class. `struct tveeprom` stores parsed radio/IR/MAC presence, primary/secondary tuner type/formats/model, audio/decoder processor, model, revision, serial, revision string, and MAC address. APIs are `tveeprom_hauppauge_analog()` and `tveeprom_read()`.

## Control Flow
Bridge drivers read EEPROM bytes over I2C using `tveeprom_read()`, then parse 256-byte Hauppauge data with `tveeprom_hauppauge_analog()` to fill board configuration fields.

## State and Persistence Behavior
Parsed data is stored in caller-owned `struct tveeprom`; EEPROM contents are persistent device manufacturing data.

## Dependencies and Integration Points
Depends on I2C client and Ethernet address sizing. Integrates Hauppauge card autodetection with tuner type IDs, analog standards, IR support, and optional MAC address setup.

## Risks
Short reads or malformed EEPROM data can misconfigure tuners, standards, IR, or network MAC. `len` should be at least 256 for Hauppauge parsing.

## Test Signals
EEPROM read success/failure, known EEPROM image parsing, tuner and format mapping, MAC extraction, IR capability bits, and handling truncated data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/tveeprom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/v4l2-async.h -->
# sources/distributed-fs/ceph-client/include/media/v4l2-async.h

## Purpose
Defines the V4L2 asynchronous subdevice matching and notifier API used to bind sensors/subdevices to bridge drivers when probe order is not fixed.

## Important APIs, Types, and Functions
`enum v4l2_async_match_type` supports I2C and firmware-node matching. `struct v4l2_async_match_desc`, `v4l2_async_connection`, notifier operations, `v4l2_async_notifier`, and `v4l2_async_subdev_endpoint` model waiting/done lists and parent/child notifiers. APIs initialize root/subdev notifiers, add fwnode/remote/I2C connections, add subdev endpoints, find a unique connection, register/unregister/cleanup notifiers, register sensor subdevices, and unregister subdevices.

## Control Flow
Bridge drivers initialize a notifier, add expected async connections, and register it. Subdevices register asynchronously; the framework matches them by fwnode or I2C, calls `bound`, moves entries between waiting/done lists, and calls root `complete` once all dependencies bind. Unregister invokes `unbind`; cleanup releases allocated connection resources.

## State and Persistence Behavior
Notifiers own waiting/done lists and parent relationships for the binding lifetime. Connection structs must embed `v4l2_async_connection` first when driver-specific types are used. Fwnode references acquired during add are released during cleanup.

## Dependencies and Integration Points
Depends on lists/mutexes, firmware nodes, I2C identity, V4L2 devices, and subdevices. It is central to camera sensor, bridge, and firmware graph integration.

## Risks
Forgetting cleanup leaks fwnode refs/connections. Incorrect first-member embedding breaks casts. Duplicate or non-unique subdevice connections cause ambiguous binding. Complete only runs for the root notifier, so child-notifier expectations must be explicit.

## Test Signals
Out-of-order bridge/sensor probe, fwnode remote matching, I2C matching, nested notifiers, endpoint list cleanup via `v4l2_subdev_cleanup()`, unbind on driver remove, and partial-bind failure unwinds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/v4l2-async.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/v4l2-cci.h -->
# sources/distributed-fs/ceph-client/include/media/v4l2-cci.h

## Purpose
Declares MIPI Camera Control Interface register encoding and regmap-backed access helpers for camera sensor drivers.

## Important APIs, Types, and Functions
`struct cci_reg_sequence` stores encoded register/value pairs. Macros encode register address, width, little-endian flag, private bits, and helpers to extract address/width. Constructors include `CCI_REG8/16/24/32/64` and little-endian variants. APIs include `cci_read()`, `cci_write()`, `cci_update_bits()`, `cci_multi_reg_write()`, and optional `devm_cci_regmap_init_i2c()`.

## Control Flow
Drivers encode each register with width metadata, then call CCI helpers. If an optional error pointer already contains an error, operations are skipped, allowing compact sequential setup code. Multi-register writes handle heterogenous register widths.

## State and Persistence Behavior
No persistent state is owned; register state persists in the target sensor. Optional error accumulator carries transient failure state across a sequence.

## Dependencies and Integration Points
Depends on bitfield/bits/types, regmap, and optionally I2C CCI regmap support. Integrates modern camera sensor drivers with width-aware register access.

## Risks
Using raw addresses instead of `CCI_REG*()` loses width metadata. `cci_update_bits()` is read-modify-write and explicitly not atomic against other CCI accesses. Endianness flag must match device register layout.

## Test Signals
Read/write for every width, little-endian register tests, error-accumulator skip behavior, multi-register write sequences, update-bits races under locking, and I2C regmap init with 8/16-bit register addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/v4l2-cci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/v4l2-common.h -->
# sources/distributed-fs/ceph-client/include/media/v4l2-common.h

## Purpose
Defines shared internal V4L2 helper APIs for logging, control query filling, I2C/SPI subdevice creation, tuner address probing, image alignment, nearest-size selection, stream parameter helpers, pixel-format metadata, link-frequency/lane discovery, sensor clock lookup, timestamp conversion, and colorimetry validation.

## Important APIs, Types, and Functions
Logging macros include `v4l_*`, `v4l2_*`, and debug-level variants. APIs include `v4l2_ctrl_query_fill()`, I2C helpers such as `v4l2_i2c_new_subdev*()`, `v4l2_i2c_subdev_init()`, tuner address lists, SPI subdev helpers, legacy `TUNER_SET_CONFIG` and `VIDIOC_INT_RESET`, `v4l_bound_align_image()`, nearest-size macros/backing function, `v4l2_g_parm_cap()`, `v4l2_s_parm_cap()`, `V4L2_FRACT_COMPARE`, `struct v4l2_format_info`, format classification helpers, `v4l2_format_info()`, pixfmt fill helpers, media-controller link frequency/lane helpers, fraction helpers, `v4l2_link_freq_to_bitmap()`, sensor clock helpers, buffer timestamp get/set, and colorimetry validity helpers.

## Control Flow
Bridge drivers use bus helpers to instantiate subdevices, format helpers to negotiate pixel layouts, alignment helpers to clamp requested dimensions, and link helpers to query transmitter pad configuration or controls. Sensor drivers use clock helpers to bridge firmware/ACPI clock description gaps.

## State and Persistence Behavior
Most helpers are stateless. Subdevice creation registers I2C/SPI client/subdev state elsewhere. Sensor clock helpers may register devm-managed fixed clocks for ACPI cases. Timestamp helpers translate between legacy timeval fields and nanoseconds.

## Dependencies and Integration Points
Depends on V4L2 dev/subdev/video types, I2C, SPI, clocks, media-controller pads, firmware properties, and V4L2 UAPI pixel/colorimetry structures. It is a broad integration header for low-level V4L2 drivers.

## Risks
Helper stubs return `NULL` or no-op when I2C/SPI/media-controller support is disabled, so callers must handle missing support. Nearest-size macros require width/height fields to be `u32`. Link-frequency fallback depends on valid transmitter controls. Timestamp conversion preserves 32-bit userspace compatibility by truncating `tv_usec` to `u32`.

## Test Signals
I2C/SPI subdevice probe/unregister, tuner address probing, image alignment edge cases, nearest-size with and without predicate, streamparm get/set through subdevs, format-info fill for planar/packed formats, link frequency from mbus config/control/pixel rate, active data lane validation, ACPI sensor clock fallback, timestamp round trips, and colorimetry validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/media/v4l2-common.h -->
