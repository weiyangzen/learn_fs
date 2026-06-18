# Research Report: subset-b-004086

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ccs/smiapp-reg-defs.h -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/ccs/smiapp-reg-defs.h

## Purpose
This header is a register and bit-definition catalog for SMIA/SMIA++/MIPI CCS compliant camera sensors. It does not implement behavior; it standardizes typed CCI register identifiers used by the CCS camera driver stack. The macros encode register width through `CCI_REG8`, `CCI_REG16`, and `CCI_REG32`, with a few floating-point capability registers carrying `CCS_FL_FLOAT_IREAL`.

## Important APIs, Types, And Constants
The primary API is the `SMIAPP_REG_*` macro namespace. Names encode width and semantic purpose, such as model identity, frame format descriptors, gain controls, streaming mode, CSI-2 format/lane setup, integration timing, PLL dividers, crop/scaler geometry, binning, data-transfer interfaces, defect correction, EDOF, flash, actuator, and bracketing LUT capability registers. Important bit definitions include image orientation flip bits, data-transfer interface control/status bits, reset, flash capability bits, CSI signaling modes, DPHY modes, compression modes, stream/standby mode values, scaler/crop/binning capability values, Bayer pixel-order constants, and frame-format descriptor masks/shifts.

## Control Flow
There is no executable control flow. The only dependency behavior is compile-time substitution of register constants into code that performs CCI reads and writes. Parameterized macros such as `SMIAPP_REG_U16_FRAME_FORMAT_DESCRIPTOR_2(n)` and `SMIAPP_REG_U8_BINNING_TYPE_n(n)` derive contiguous table addresses from an index.

## State And Persistence
The file holds no runtime state. Persistent effects occur only when users of these macros write sensor registers, for example switching `SMIAPP_MODE_SELECT_STREAMING`, changing crop/scaler values, or issuing `SMIAPP_SOFTWARE_RESET`.

## Dependencies And Integration Points
It depends on `<linux/bits.h>` for `BIT()` and `<media/v4l2-cci.h>` for typed CCI register encoding. Integration is with the CCS/SMIA camera sensor driver and any helper code that interprets MIPI CCS capability/register layouts.

## Risks
Risks are specification drift and address/width mismatch: a wrong width macro can make CCI access corrupt adjacent registers or fail reads. Indexed macros rely on callers honoring the documented ranges. The long flat list is hard to audit manually, especially for adjacent table/register ranges.

## Test Signals
Useful validation is compile coverage from CCS drivers, sensor probe tests that read identity and capability registers, runtime streaming tests that program mode/crop/CSI registers, and static checks comparing macro addresses to the CCS specification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ccs/smiapp-reg-defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/cs3308.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/cs3308.c

## Purpose
This is a small V4L2 I2C subdevice driver for the Cirrus Logic CS3308 8-channel analog volume controller. It detects the chip over SMBus byte-data transactions, initializes sane gain/mute/power defaults, and exposes only optional advanced debug register access.

## Important APIs, Types, And Functions
`cs3308_write()` and `cs3308_read()` wrap `i2c_smbus_write_byte_data()` and `i2c_smbus_read_byte_data()` using the `v4l2_subdev` client binding. Under `CONFIG_VIDEO_ADV_DEBUG`, `cs3308_g_register()` and `cs3308_s_register()` provide one-byte raw register inspection/mutation. `cs3308_probe()` and `cs3308_remove()` are the I2C driver lifecycle hooks. `cs3308_core_ops`, `cs3308_ops`, and `cs3308_driver` wire the subdevice into V4L2 and I2C.

## Control Flow
Probe first checks `I2C_FUNC_SMBUS_BYTE_DATA`, then reads register `0x1c` and requires its high nibble to be `0xe0`. It allocates a standalone `struct v4l2_subdev`, initializes it with `v4l2_i2c_subdev_init()`, powers all channels, sets master power and device configuration, programs channels 1 through 8 to `0xd2`, and unmutes all channels. Remove unregisters and frees the subdevice.

## State And Persistence
The driver keeps no private state beyond the allocated `v4l2_subdev` and the I2C client data set by V4L2. Hardware state is persistent in CS3308 registers until reset or power loss: power, channel volume, master power, configuration, and mute are all programmed during probe.

## Dependencies And Integration Points
It depends on Linux I2C, V4L2 subdev support, module infrastructure, and SMBus byte-data support from the adapter. It integrates as an auxiliary audio-control subdevice for capture boards that instantiate a `"cs3308"` I2C device.

## Risks
Initialization writes ignore return values, so partial I2C failures after detection can leave the chip in a partially configured state while probe still succeeds. The chip check is a narrow register-nibble test and could misdetect on a bad bus. The driver exposes no standard V4L2 volume controls, so normal operation depends on board-specific users or defaults.

## Test Signals
Probe should log chip detection at the expected address, register `0x1c` should match the ID pattern, and debug register reads should reflect programmed defaults. Fault-injection tests around SMBus writes would expose the lack of error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/cs3308.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/cs5345.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/cs5345.c

## Purpose
This file implements a V4L2 I2C subdevice driver for the Cirrus Logic CS5345 stereo audio ADC. It provides audio input routing, mute and volume controls, status logging, optional raw register debug access, and probe-time hardware default setup.

## Important APIs, Types, And Functions
`struct cs5345_state` embeds `struct v4l2_subdev` and `struct v4l2_ctrl_handler`. `cs5345_write()` and `cs5345_read()` wrap SMBus byte register access. `cs5345_s_routing()` selects an input using registers `0x09` and `0x05`. `cs5345_s_ctrl()` implements `V4L2_CID_AUDIO_MUTE` and `V4L2_CID_AUDIO_VOLUME`. `cs5345_log_status()` reports input, mute, and signed dB volume. Probe/remove manage the V4L2 control handler and subdevice lifecycle.

## Control Flow
Probe checks SMBus byte-data functionality, allocates devm-managed state, initializes the V4L2 I2C subdev, creates mute and volume controls, assigns the handler, applies control defaults with `v4l2_ctrl_handler_setup()`, then writes initial chip registers `0x02`, `0x04`, and `0x09`. Routing rejects inputs whose low nibble exceeds 6. Control changes write mute bit `0x80` to register `0x04` and mirror six-bit volume to left/right registers `0x07` and `0x08`.

## State And Persistence
State is split between the V4L2 control handler cache and hardware registers. The state allocation is devm-managed, while `cs5345_remove()` explicitly unregisters the subdevice and frees controls. Register programming persists in the chip until changed or reset.

## Dependencies And Integration Points
The driver depends on Linux I2C/SMBus, V4L2 subdev audio operations, and V4L2 controls. It is integrated by bridge drivers that instantiate `"cs5345"` and call subdev audio routing/control operations.

## Risks
Probe has no device-ID validation beyond successful I2C access, so board descriptions must be accurate. Most register writes ignore return values, making failed configuration silent. `cs5345_s_routing()` encodes both low and high input bits from the `input` value, so callers must understand the board-specific bit layout.

## Test Signals
Expected signals include successful control registration, mute/volume writes visible through debug registers, route changes reflected in `log_status()`, and adapter rejection on missing SMBus byte-data support. Hardware tests should cover all valid input values and invalid input rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/cs5345.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/cs53l32a.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/cs53l32a.c

## Purpose
This V4L2 I2C subdevice driver supports the Cirrus Logic CS53L32A audio ADC, historically used by Adaptec AVC boards. It handles audio source selection, volume and mute controls, status logging, and board-specific register initialization.

## Important APIs, Types, And Functions
`struct cs53l32a_state` embeds the V4L2 subdev and control handler. `cs53l32a_write()` and `cs53l32a_read()` perform SMBus byte-data register access. `cs53l32a_s_routing()` maps logical input 0 through 2 onto register `0x01`. `cs53l32a_s_ctrl()` implements volume and mute controls. `cs53l32a_log_status()` reports selected input and V4L2 control state. `cs53l32a_probe()` and `cs53l32a_remove()` manage I2C driver lifecycle.

## Control Flow
Probe checks SMBus byte-data support, sets a fallback client name when no I2C ID is present, allocates devm state, initializes the V4L2 I2C subdevice, optionally logs current registers 1 through 7, creates volume and mute controls, writes the Adaptec setup values to registers 1 through 7, and logs the post-write values under debug. Routing rejects inputs above 2 because the second physical input has two PGA/bypass modes. Mute writes `0xf0` or `0x30` to register `0x03`; volume is mirrored to registers `0x04` and `0x05`.

## State And Persistence
Software state is the V4L2 control handler plus subdev object. Hardware state consists of seven initialized device registers and later routing/control writes. The state structure is devm-managed, but controls are explicitly freed on remove.

## Dependencies And Integration Points
The file depends on Linux I2C, V4L2 subdev/control APIs, and SMBus byte-data functionality. It integrates as a board-managed audio subdevice whose controls are surfaced through the parent V4L2 device.

## Risks
There is no chip-ID verification, and initialization writes do not propagate errors. The hard-coded Adaptec setup may be inappropriate for non-Adaptec boards using the same chip. Debug reads cast negative SMBus errors into `u8` values during logging, potentially obscuring bus failures.

## Test Signals
Tests should verify invalid routing returns `-EINVAL`, volume/mute controls update registers, debug logs show expected initialized values `0x21,0x29,0x30,0,0,0,0`, and probe fails cleanly when SMBus byte-data support is missing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/cs53l32a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/cx25840/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/cx25840/Kconfig

## Purpose
This Kconfig entry exposes the `VIDEO_CX25840` build option for Conexant CX2584x audio/video decoder support. It lets the driver be built in, built as a module, or omitted.

## Important APIs, Types, And Functions
The relevant symbol is `config VIDEO_CX25840`, declared as `tristate "Conexant CX2584x audio/video decoders"`. It depends on `VIDEO_DEV && I2C`. The help text documents that the module name is `cx25840`.

## Control Flow
There is no runtime control flow. At configuration time, Kconfig uses the dependency expression to decide whether the symbol is visible/selectable. At build time, the selected value is consumed by the Makefile through `obj-$(CONFIG_VIDEO_CX25840)`.

## State And Persistence
The only state is the kernel build configuration value. It persists in `.config` and determines whether `cx25840.o` is compiled and linked.

## Dependencies And Integration Points
It integrates with the media I2C driver build. `VIDEO_DEV` supplies V4L2 core infrastructure and `I2C` supplies the bus layer required by the driver.

## Risks
The prompt text names only CX2584x, while the implementation also supports related CX23885/7/8, CX231xx AV core, and CX25836/7 variants. Users may miss the broader hardware coverage.

## Test Signals
Configuration tests should confirm the symbol is unavailable without I2C or video device support, builds as `cx25840.ko` when set to module, and includes all component objects declared by the Makefile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/cx25840/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/cx25840/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/cx25840/Makefile

## Purpose
This Makefile composes the CX25840 driver module from its core, audio, firmware, VBI, and IR implementation files and binds the result to `CONFIG_VIDEO_CX25840`.

## Important APIs, Types, And Functions
`cx25840-objs` lists `cx25840-core.o`, `cx25840-audio.o`, `cx25840-firmware.o`, `cx25840-vbi.o`, and `cx25840-ir.o`. `obj-$(CONFIG_VIDEO_CX25840) += cx25840.o` connects the composite object to the Kconfig tristate.

## Control Flow
There is no runtime control flow. Kbuild expands `cx25840-objs` into the linked `cx25840.o` composite whenever `CONFIG_VIDEO_CX25840` is enabled.

## State And Persistence
The file contributes build-system state only. It determines which translation units are linked together and therefore which internal symbols are available to the module.

## Dependencies And Integration Points
It integrates with the kernel media I2C build tree and relies on the corresponding Kconfig symbol. The object list matches declarations in `cx25840-core.h`: core register helpers, firmware loading, audio controls, VBI operations, and IR operations are all linked into one module.

## Risks
Omitting any listed object would produce unresolved references or silently remove a V4L2 operation family. Adding new internal implementation files requires updating this list, because the module is not built from a wildcard.

## Test Signals
Build tests should show all five objects compiled and linked into `cx25840.o`, and module metadata should report a single `cx25840` module when configured as `m`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/cx25840/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/cx25840/cx25840-audio.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/cx25840/cx25840-audio.c

## Purpose
This file implements audio clock, routing path, and audio control support for the CX25840 family driver. It programs PLL/SRC registers for 32 kHz, 44.1 kHz, and 48 kHz sample rates, switches between serial and tuner/demod audio paths, and maps V4L2 audio controls onto chip registers.

## Important APIs, Types, And Functions
`cx25840_s_clock_freq()` is the V4L2 audio clock entry point. `cx25840_audio_set_path()` is called by core input routing to reset and reconfigure the audio path. `cx25840_audio_ctrl_ops` exposes `cx25840_audio_s_ctrl()` for volume, balance, bass, and treble. Internal helpers include `cx25840_set_audclk_freq()`, `cx23885_set_audclk_freq()`, `cx231xx_set_audclk_freq()`, `set_audclk_freq()`, `set_volume()`, and `set_balance()`.

## Control Flow
Clock changes first validate the frequency, select the chip-family-specific setter, and write PLL/SRC constants. For non-serial analog inputs, `cx25840_audio_set_path()` asserts soft reset, stops the audio microcontroller, mutes outputs, writes `PATH1` routing for serial or analog demod, sets the clock, optionally restarts the microcontroller for tuner audio, and deasserts reset. Direct `s_clock_freq` follows the same mute/stop/program/restart pattern. Audio controls scale V4L2 ranges to chip-specific volume, EQ, and balance fields.

## State And Persistence
`state->audclk_freq` caches the selected sample rate and is reused when routes change. `state->aud_input`, `state->volume`, and `state->mute` influence path and volume programming. Hardware state persists in PLL, SRC, path, mute, EQ, and balance registers until reset or another V4L2 call changes it.

## Dependencies And Integration Points
The file depends on register helpers and model predicates from `cx25840-core.h`, V4L2 control IDs, and media driver interface constants from `media/drv-intf/cx25840.h`. It is linked into the composite `cx25840` module and called by `cx25840-core.c` during input routing, probe control setup, and audio subdev ops.

## Risks
Several chip/frequency combinations are documented as unknown and intentionally avoid programming registers while still caching the requested rate. PLL constants contain FIXME notes about reference frequency mismatch and out-of-range AUX PLL operation at 32 kHz. Control writes generally ignore I2C errors. Volume scaling preserves legacy mappings but is non-obvious and can surprise callers expecting linear dB behavior.

## Test Signals
Tests should cover valid and invalid sample rates, serial versus analog path setup, mute-cluster behavior, volume/balance register mappings, and regression audio capture at all supported rates on each chip family. Hardware logging should confirm the microcontroller restarts for tuner audio and stays stopped for serial inputs where intended.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/cx25840/cx25840-audio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/cx25840/cx25840-core.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/cx25840/cx25840-core.c

## Purpose
This is the main Conexant CX25840-family audio/video decoder driver. It provides low-level I2C register access, chip identification, model-specific initialization, video standard and input routing, V4L2 controls, pad format scaling, tuner status/audio mode handling, IRQ dispatch, and I2C driver probe/remove.

## Important APIs, Types, And Functions
Exported internal helpers include `cx25840_write()`, `cx25840_write4()`, `cx25840_read()`, `cx25840_read4()`, `cx25840_and_or()`, `cx25840_and_or4()`, and `cx25840_std_setup()`. Major internal flows are `cx25840_initialize()`, `cx23885_initialize()`, `cx231xx_initialize()`, `cx25836_initialize()`, `set_input()`, `input_change()`, `set_v4lstd()`, `cx25840_set_fmt()`, `cx25840_reset()`, and `cx25840_probe()`. V4L2 op tables provide core, tuner, audio, video, VBI, pad, and IR operations.

## Control Flow
Probe checks SMBus byte-data support, reads chip ID registers, handles ID-less CX2388x detection by probing known registers, allocates `struct cx25840_state`, initializes media pads if enabled, sets defaults, registers controls, applies control defaults, consumes platform data for the PVR150 workaround, and probes IR. Firmware is not loaded at probe; `load_fw` or `reset` triggers initialization. Reset dispatches to a model-specific initializer, which programs PLLs, DLLs, analog front-end, DIF, VBI, audio, and firmware loader sequences before starting the microcontroller. Standard and input V4L2 calls update cached state and then write the relevant register sets.

## State And Persistence
`struct cx25840_state` caches model, revision, standard, radio mode, selected video/audio inputs, audio clock, tuner audio mode, VBI line offset/register offset, generic-mode output config, initialization status, firmware work/waitqueue, optional IR state, and V4L2 controls. Hardware persistence is extensive: PLLs, routing muxes, ADC settings, video timing/scaler, audio microcontroller state, VBI registers, DIF coefficients, and output pin configuration remain programmed until reinitialized.

## Dependencies And Integration Points
The file depends on Linux I2C, V4L2 common/subdev/control APIs, media controller pads, `media/drv-intf/cx25840.h`, and the sibling audio, firmware, VBI, and IR files through `cx25840-core.h`. Bridge drivers integrate by instantiating the I2C client, calling subdev operations, optionally providing platform data, and handling IRQ callbacks.

## Risks
The driver is register-heavy and has many chip-family branches, so regressions can be board-specific. Many register writes ignore transfer errors. Firmware loading is synchronous from the caller's perspective but uses a temporary workqueue to avoid blocking bit-banged I2C inside the loader. `cx25840_read()` returns zero on I2C failure, which can be confused with valid register values. Some generic-mode and media-controller paths are explicitly partial or TODO-backed. DIF and standard setup contain large coefficient tables and assumptions about tuner IF.

## Test Signals
Strong signals include successful probe logs for each supported model, firmware load messages, stable `log_status()` output, standard detection through `querystd`, correct no-signal reporting, route changes for composite/S-Video/component/DIF, pad scaling register updates, audio mode/tuner behavior, IRQ handling on CX23885/7/8, and VBI decode tests. Regression testing needs real hardware coverage across CX2583x, CX2584x, CX23885/7/8, and CX231xx variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/cx25840/cx25840-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/cx25840/cx25840-core.h -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/cx25840/cx25840-core.h

## Purpose
This internal header defines the shared data model and function contracts for the composite CX25840 driver. It lets the core, audio, firmware, VBI, and IR translation units share chip-family predicates, private state, and internal register helper declarations.

## Important APIs, Types, And Functions
`enum cx25840_model` identifies CX23885/7/8 AV cores, CX2310X AV, CX25840/1/2/3, and CX25836/7. `enum cx25840_media_pads` defines the optional media-controller sink/source pads. `struct cx25840_state` is the central per-device state. Inline helpers `to_state()`, `to_sd()`, `is_cx2583x()`, `is_cx2584x()`, `is_cx231xx()`, `is_cx2388x()`, `is_cx23885()`, `is_cx23887()`, and `is_cx23888()` are used throughout. Function declarations expose register helpers, firmware loading, audio path/clock ops, VBI format/decode ops, and IR ops.

## Control Flow
The header itself has no runtime control flow, but its predicates drive nearly every branch in the implementation. The shared `struct cx25840_state` is recovered from subdev/control callbacks and feeds model-specific initialization, audio programming, VBI offsets, and IRQ support.

## State And Persistence
The state struct persists for the I2C device lifetime and stores both software cache and hardware intent: selected standards/routes, audio clock and mode, generic-mode output configuration, firmware initialization status, VBI offsets, platform workaround flag, and IR substate. Its fields are the source of truth used to reapply hardware setup after resets or route changes.

## Dependencies And Integration Points
It includes V4L2 device/control headers and Linux I2C. It also depends on public media driver-interface definitions for video/audio input enums through included implementation files. The header is included by all CX25840 component files and forms the private ABI of the composite module.

## Risks
Because this is a private cross-file ABI, changing `struct cx25840_state` semantics can silently break sibling files. Model predicates are simple enum checks; any new model must be added consistently to all predicates and switch statements. Optional media-controller fields are compiled conditionally, so code must respect `CONFIG_MEDIA_CONTROLLER`.

## Test Signals
Build coverage across media-controller enabled/disabled configurations, all object files including this header, and runtime paths for every model predicate are key signals. Static analysis can catch missing declarations or stale function prototypes after refactors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/cx25840/cx25840-core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/cx25840/cx25840-firmware.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/cx25840/cx25840-firmware.c

## Purpose
This file implements firmware loading for CX25840-family devices. It selects the right firmware image, streams it over I2C in small chunks, toggles the chip download interface, verifies the downloaded size, and preserves CX2388x GPIO state across the load.

## Important APIs, Types, And Functions
The exported internal entry point is `cx25840_loadfw()`. `get_fw_name()` chooses between an override module parameter and the default firmware names `v4l-cx23885-avcore-01.fw`, `v4l-cx231xx-avcore-01.fw`, and `v4l-cx25840.fw`. `start_fw_load()`, `end_fw_load()`, `fw_write()`, and `check_fw_load()` implement the transfer protocol. `MODULE_FIRMWARE()` advertises the required images.

## Control Flow
`cx25840_loadfw()` optionally snapshots CX2388x GPIO output-enable/data registers, limits transfer size to 16 bytes for CX231xx or 48 bytes otherwise, calls `request_firmware()`, enables download mode, sends firmware chunks prefixed with register address bytes `0x08,0x02`, disables download mode, releases firmware, restores GPIOs on CX2388x, and verifies that the device download-address registers match the firmware size.

## State And Persistence
The firmware image is not cached in driver memory. Persistent effects are in the chip microcontroller memory and related download-control registers. The module parameter `firmware` persists as the selected firmware name for the module lifetime.

## Dependencies And Integration Points
The file depends on Linux firmware loading, I2C master sends, V4L2 logging, and model predicates/register helpers from `cx25840-core.h`. It is invoked by the core initializer through a temporary workqueue and by the subdev `load_fw` path.

## Risks
Firmware transfer is sensitive to I2C adapter message-size limits, which is why `FWSEND` is only 48 bytes and CX231xx is capped at 16. `i2c_master_send()` short writes are treated as failures, but register writes around download setup are not checked. Failure to load firmware leaves audio standard detection degraded. The size check detects some failed transfers but does not validate firmware contents.

## Test Signals
Expected tests include missing firmware error reporting, successful load log with exact byte count, CX231xx short-chunk operation, CX2388x GPIO preservation, and audio standard detection working after reset/load. Firmware request paths should be validated for built-in and modular driver deployments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/cx25840/cx25840-firmware.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/cx25840/cx25840-ir.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/cx25840/cx25840-ir.c

## Purpose
This file implements the integrated consumer infrared controller support for CX23885/CX23887 AV cores inside the CX25840 driver. It provides V4L2 subdevice IR operations, receive FIFO draining, parameter programming, status logging, and partial transmit scaffolding.

## Important APIs, Types, And Functions
`struct cx25840_ir_state` stores I2C client, Rx/Tx parameter caches, locks, atomic clock/invert values, and the Rx kfifo. `union cx25840_ir_fifo_rec` maps hardware FIFO words to `struct ir_raw_event` payloads. External entry points are `cx25840_ir_ops`, `cx25840_ir_log_status()`, `cx25840_ir_irq_handler()`, `cx25840_ir_probe()`, and `cx25840_ir_remove()`. Helpers convert carrier frequencies, pulse widths, filter widths, and hardware counters.

## Control Flow
Probe only initializes IR for CX23885/CX23887, allocates state, allocates the Rx kfifo, masks interrupts, and applies default Rx/Tx parameters. Rx parameter setting disables interrupts and receiver, configures demodulation, carrier window or max pulse width, low-pass filter, resolution, edge detection, inversion, interrupt enables, and finally re-enables hardware if requested. IRQ handling checks enabled status bits, drains hardware Rx FIFO into the kfifo on service request or timeout, reports software/hardware overruns and end-of-receive events, and clears hardware overrun/timeout by toggling control bits. `rx_read` converts FIFO counts into `ir_raw_event` durations. Tx write is intentionally incomplete and only enables a service interrupt while pretending to consume the buffer.

## State And Persistence
Runtime state includes cached parameter structs protected by mutexes, atomic dividers used during read conversion, and a spinlock-protected receive kfifo. Hardware state persists in IR control, clock, duty, filter, stats, IRQ, and FIFO registers. Shutdown paths disable interrupts and slow/disable counters.

## Dependencies And Integration Points
It depends on `kfifo`, mutex/spinlock primitives, V4L2 subdev IR APIs, rc-core raw events, and core register helpers/model predicates. The core IRQ handler delegates IR interrupts for CX23885/7 and `cx25840_log_status()` includes IR status.

## Risks
Transmit support is a stub, so callers may believe data was accepted though no waveform is emitted. Only CX23885/CX23887 are supported; CX23888 returns no IR support. IRQ enable bits are inverted for CX23885/7, which is easy to break. Rx kfifo overrun drops data and only reports an event. Timing conversions depend on a fixed 108 MHz video-clock-derived reference.

## Test Signals
Useful signals include Rx event delivery for RC-5/RC-6-like defaults, timeout/end-of-receive notifications, hardware and software FIFO overrun handling, parameter round trips, shutdown disabling registers, and IRQ dispatch through the parent core. Tx tests should assert current stub limitations rather than expecting real transmit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/cx25840/cx25840-ir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/cx25840/cx25840-vbi.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/cx25840/cx25840-vbi.c

## Purpose
This file implements vertical blanking interval support for the CX25840 driver. It configures raw and sliced VBI capture, reports the current sliced service map, and decodes VBI payload headers into V4L2 sliced VBI line metadata.

## Important APIs, Types, And Functions
External entry points are `cx25840_s_raw_fmt()`, `cx25840_s_sliced_fmt()`, `cx25840_g_sliced_fmt()`, and `cx25840_decode_vbi_line()`. Internal helpers `odd_parity()` and `decode_vps()` validate closed-caption parity and decode VPS biphase coding. The file uses V4L2 service identifiers for Teletext B, WSS 625, Caption 525, and VPS.

## Control Flow
Raw format setup re-applies the selected video standard, sets the PAL/NTSC VBI offset register, and programs output control for raw VBI. Sliced format setup clears invalid line ranges for PAL or NTSC, translates requested service lines into line-control-register nibbles, writes the correct register range using `state->vbi_regs_offset`, sets ancillary/VBI control registers, and adjusts timing for PAL/NTSC and CX23888 differences. `g_sliced_fmt()` reads line-control registers back and maps nibbles to V4L2 service bits. `decode_vbi_line()` validates the packet prefix, computes line number with `state->vbi_line_offset`, maps service IDs, and validates parity or VPS biphase data.

## State And Persistence
The file uses `state->std`, `state->vbi_line_offset`, and `state->vbi_regs_offset` from the core state. Hardware line-control and output-control registers persist until the next VBI/standard setup. The decode function mutates the caller's `v4l2_decode_vbi_line` result fields and advances `vbi->p` to payload data.

## Dependencies And Integration Points
It depends on core register helpers and `cx25840_std_setup()`, V4L2 VBI structures, and media driver interface constants. It is wired into `cx25840_vbi_ops` in core and is used by bridge drivers exposing VBI capture.

## Risks
Generic-mode VBI is marked as TODO, so behavior may not match newer output configuration paths. Service-line mapping is register-nibble based and easy to misalign across PAL/NTSC/CX23888 offsets. Decode validation is intentionally minimal for some services and returns success even when it clears type/line on invalid data.

## Test Signals
Tests should set/get sliced formats for PAL and NTSC line ranges, verify raw VBI register programming, decode known caption and VPS sample lines, reject malformed prefixes/parity, and validate CX23888 offset handling separately from older chips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/cx25840/cx25840-vbi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ds90ub913.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/ds90ub913.c

## Purpose
This is a V4L2 subdevice driver for the Texas Instruments DS90UB913 FPD-Link III video serializer. It bridges a parallel sensor/source bus to an FPD-Link output, exposes a streams-aware media entity, manages serializer GPIOs, initializes local I2C timing, registers a divided clock output, and creates a remote I2C adapter through I2C ATR platform data.

## Important APIs, Types, And Functions
`struct ub913_data` stores the I2C client, regmap, input clock, GPIO chip, V4L2 subdev/pads/notifier, bound source subdev and pad, enabled stream mask, clkout provider, platform data, and PCLK polarity. Format support is declared by `ub913_formats[]`, mapping 8-bit 2X8 YUV input codes to 1X16 output codes. Key functions include `ub913_read/write/update_bits()`, GPIO callbacks, `ub913_enable_streams()`, `ub913_disable_streams()`, routing/format operations, async notifier registration/bound handling, `ub913_register_clkout()`, `ub913_i2c_master_init()`, `ub913_add_i2c_adapter()`, `ub913_parse_dt()`, `ub913_hw_init()`, and probe/remove.

## Control Flow
Probe allocates state, requires platform data with ATR context/port, initializes regmap, gets `clkin`, parses the sink endpoint for PCLK sampling edge, checks hardware mode stabilization, programs I2C master timing and PCLK polarity, registers the GPIO chip, registers a fixed-factor clkout at `clkin / 2`, initializes the V4L2 subdev/media pads/default route/notifier, registers the subdev asynchronously, and adds an ATR-backed remote I2C adapter if an `i2c` child node exists. Bound notifier handling finds the remote source pad and creates an immutable enabled media link. Stream enable/disable translates source-pad streams back to sink streams and forwards calls to the upstream source subdev.

## State And Persistence
The driver caches enabled source streams to block active routing/format changes. Register state persists for GPIO local output configuration, I2C SCL high/low timings, PCLK polarity, and CRC reset toggling. The remote source binding and media link persist until subdev unregistration. The ATR adapter persists until remove calls `i2c_atr_del_adapter()`.

## Dependencies And Integration Points
It depends on regmap, common clock framework, GPIO framework, firmware-node graph parsing, V4L2 subdev streams/routing APIs, media controller links, and `i2c-atr`. It integrates with DS90UB9xx deserializer infrastructure through `ds90ub9xx_platform_data`, especially the ATR object and serializer port number.

## Risks
The driver requires platform data and external `clkin`; standalone device-tree probing without deserializer-provided data fails. Only two GPIOs are supported and only output direction is implemented. Format support is limited to four YUV 8-bit mappings despite the comment about limited payload support. Active stream state blocks format/routing changes, so leaked stream state would cause persistent `-EBUSY`. Remote I2C adapter setup depends on a child node and ATR lifecycle outside this file.

## Test Signals
Good signals include probe success with valid platform data, mode-up-to-date validation, correct SCL timing writes from `clkin`, PCLK polarity programming from endpoint flags, GPIO output register updates, clkout provider registration at half rate, immutable media link creation when the source binds, format propagation from sink to source code, stream forwarding to the source subdev, CRC counter logging/reset, ATR adapter creation/removal, and clean error unwinding at each probe stage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ds90ub913.c -->
