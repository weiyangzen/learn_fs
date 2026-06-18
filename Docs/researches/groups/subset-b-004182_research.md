# subset-b-004182 research

Grouped research report for the requested Silicon Labs radio transmitter/receiver helpers, Philips tuner helpers, and Linux rc-core remote-control drivers. Each section is keyed by original source path for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/si470x/radio-si470x.h -->
# sources/distributed-fs/ceph-client/drivers/media/radio/si470x/radio-si470x.h

Purpose: common private header for Silicon Labs Si470x FM radio receiver drivers. It centralizes register numbers and bit masks, the shared `struct si470x_device`, firmware/frequency constants, and common function declarations used by the USB and I2C Si470x implementations.

Important APIs and types: `struct si470x_device` embeds `v4l2_device`, `video_device`, a V4L2 control handler, cached 16-bit register image, RDS circular buffer state, completion and lock primitives, and transport-specific fields under `CONFIG_USB_SI470X` or `CONFIG_I2C_SI470X`. Export-facing declarations are `si470x_viddev_template`, `si470x_ctrl_ops`, `si470x_disconnect_check`, `si470x_set_freq`, `si470x_start`, and `si470x_stop`. Register macros cover `DEVICEID`, `POWERCFG`, `CHANNEL`, `SYSCONFIG*`, `STATUSRSSI`, `READCHAN`, and RDS blocks.

Control flow: this file has no executable code, but it defines the shared state and register contract that source-specific drivers use when starting/stopping the chip, tuning, reading RDS data, and exposing V4L2 radio ioctls. Transport callbacks in `struct si470x_device` abstract register get/set and file-operation overrides.

State and persistence: state is volatile kernel driver state. The `registers[]` array caches hardware register values; the RDS buffer uses read/write indices plus a wait queue and mutex; completion/status flags coordinate asynchronous hardware or USB/I2C activity. Hardware configuration persists only in the Si470x chip while powered.

Dependencies and integration points: depends on Linux kernel, input, mutex, unaligned helpers, and V4L2 device/control/event/ioctl headers. Integrates with USB and I2C Si470x transport drivers through conditional members and common function prototypes. The frequency scale `FREQ_MUL` matches V4L2 low-frequency units.

Risks: the header uses `#define FREQ_MUL (1000000 / 62.5)`, which relies on floating constant conversion in preprocessor-facing C and can be surprising in integer contexts. Because transport-specific members are conditional, code using `struct si470x_device` must be built with matching Kconfig symbols. Register cache consistency depends on all writers using the common helpers.

Test signals: compile coverage for both USB and I2C Si470x builds, V4L2 capability/frequency/RDS behavior, RDS buffer wrap tests under interrupt load, and hardware tune/seek tests confirming register masks and frequency scaling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/si470x/radio-si470x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/si4713/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/radio/si4713/Kconfig

Purpose: defines build-time configuration for the Silicon Labs Si4713 FM transmitter stack.

Important APIs and symbols: `USB_SI4713` enables the USB development-board wrapper and selects `I2C_SI4713`; `PLATFORM_SI4713` enables the platform/I2C V4L2 radio wrapper and selects `I2C_SI4713`; `I2C_SI4713` builds the core Si4713 I2C subdevice driver. All depend on `RADIO_SI4713` and I2C as appropriate, with USB support additionally depending on USB.

Control flow: selected symbols drive the Makefile: core command/control support lives in `si4713.o`, while USB and platform entry points wrap the same subdevice through different bus exposure paths.

State and persistence: no runtime state. Kconfig choices persist in the kernel build configuration and determine whether modules `si4713`, `radio-usb-si4713`, and `radio-platform-si4713` exist.

Dependencies and integration points: integrates with the media radio Kconfig tree, V4L2 radio support, I2C, USB, and the parent `RADIO_SI4713` menu symbol. The select relationships ensure wrappers get the core I2C command driver.

Risks: selecting `I2C_SI4713` from wrappers means invalid or partial module combinations are avoided, but `I2C_SI4713` remains user-selectable on its own and then provides only a subdevice unless another driver instantiates or registers it.

Test signals: `allmodconfig`/`allyesconfig` build coverage, module dependency inspection, and menuconfig visibility with and without USB/I2C/radio prerequisites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/si4713/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/si4713/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/radio/si4713/Makefile

Purpose: maps Si4713 Kconfig symbols to the objects built by kbuild.

Important APIs and entries: `obj-$(CONFIG_I2C_SI4713) += si4713.o`, `obj-$(CONFIG_USB_SI4713) += radio-usb-si4713.o`, and `obj-$(CONFIG_PLATFORM_SI4713) += radio-platform-si4713.o`.

Control flow: kbuild links each selected object as its own module or built-in unit according to the resolved tristate value. The USB and platform objects are wrappers around the core I2C subdevice.

State and persistence: no runtime state. The file defines build artifact shape only.

Dependencies and integration points: depends on symbols declared in the adjacent `Kconfig`. The object boundaries align with driver registration boundaries: I2C driver, USB driver, and platform driver.

Risks: new source files added to the Si4713 stack must be represented here or functionality will silently not build. Wrapper modules depend on the core module relationship expressed by Kconfig rather than Makefile ordering.

Test signals: targeted kbuilds with each symbol enabled as `m` and built-in, plus module load tests confirming dependencies resolve.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/si4713/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/si4713/radio-platform-si4713.c -->
# sources/distributed-fs/ceph-client/drivers/media/radio/si4713/radio-platform-si4713.c

Purpose: platform-device V4L2 radio wrapper for an Si4713 I2C subdevice. It registers a `/dev/radio*` transmitter node and forwards user-facing V4L2 modulator/frequency/private ioctl operations to the Si4713 subdevice.

Important APIs and functions: module parameter `radio_nr` selects the radio minor. `struct radio_si4713_device` owns `v4l2_device`, `video_device`, and a mutex. File ops use `v4l2_fh_open`, `v4l2_fh_release`, `v4l2_ctrl_poll`, and `video_ioctl2`. Ioctl callbacks include `radio_si4713_querycap`, `g/s_modulator`, `g/s_frequency`, `vidioc_default`, event subscription, and control log status. Platform lifecycle is `radio_si4713_pdriver_probe` and `radio_si4713_pdriver_remove`.

Control flow: probe requires `struct radio_si4713_platform_data` containing the I2C client. It allocates wrapper state, registers a V4L2 device, obtains the subdevice via `i2c_get_clientdata`, registers the subdev with the wrapper V4L2 device, initializes a `video_device` from a template, attaches the subdev control handler, sets TX/RDS capabilities, and registers a radio node. Ioctls use `v4l2_device_call_until_err` to dispatch to subdevice tuner/core ops. Remove unregisters the video node and V4L2 device.

State and persistence: wrapper state is transient and devm-managed. Persistent hardware state remains in the I2C subdevice and Si4713 chip. The wrapper mutex serializes video-device access while the core driver maintains chip/control state.

Dependencies and integration points: depends on platform devices, I2C client data, V4L2 device/video/fh/control/event APIs, and `si4713.h`. It is instantiated either by board/platform data or by the core I2C driver allocating a `radio-si4713` platform device.

Risks: probe cannot proceed without platform data, so device-tree or board flows must create the expected handoff. `platform_get_drvdata` relies on `v4l2_device_register` setting drvdata through the device model; unexpected changes in V4L2 registration behavior would break remove. The wrapper has no direct hardware recovery path; subdevice errors propagate to userspace.

Test signals: platform probe/remove, `/dev/radio*` creation, `VIDIOC_QUERYCAP`, frequency/modulator get/set propagation, RDS control event polling, and teardown with the underlying I2C client removed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/si4713/radio-platform-si4713.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/si4713/radio-usb-si4713.c -->
# sources/distributed-fs/ceph-client/drivers/media/radio/si4713/radio-usb-si4713.c

Purpose: USB wrapper for Silicon Labs Si4713 FM transmitter development boards. It reverse-engineers the board's HID control protocol into an emulated I2C adapter, instantiates the common Si4713 I2C subdevice, and exposes a V4L2 radio transmitter node.

Important APIs and functions: `struct si4713_usb_device` owns USB interface/device pointers, V4L2 video/device state, a subdevice pointer, mutex, I2C adapter, and a shared 64-byte buffer. USB setup uses `si4713_start_seq`, `si4713_send_startup_command`, `start_seq`, `command_table`, `send_command`, `si4713_i2c_read`, `si4713_i2c_write`, `si4713_transfer`, and `si4713_register_i2c_adapter`. V4L2 ioctls forward querycap, modulator, frequency, log status, and control events. USB lifecycle is `usb_si4713_probe` and `usb_si4713_disconnect`.

Control flow: probe validates the USB ID/interface, allocates state and buffer, stores V4L2 data in the USB interface, sends the required startup command sequence, registers a V4L2 device, registers the synthetic I2C adapter, creates the Si4713 I2C subdevice with board info at `SI4713_I2C_ADDR_BUSEN_HIGH`, binds the subdevice control handler into the video device, and registers a radio transmitter node. I2C writes map the first command byte to USB framing metadata, while reads poll USB control responses until status is valid or a long USB timeout expires. Disconnect unregisters the video device, marks the V4L2 device disconnected, and drops the final reference so the release callback removes the I2C adapter and frees memory.

State and persistence: runtime state is in `si4713_usb_device` and the shared control buffer. The emulated I2C adapter is persistent only for the USB device lifetime. The startup sequence changes board firmware/device state so later Si4713 power-up commands succeed; no settings survive driver unload except device firmware state.

Dependencies and integration points: depends on USB core, V4L2 device/video/control/event APIs, I2C adapter emulation, and the common `si4713` I2C subdevice. It binds `10c4:8244` HID-class devices and exposes `V4L2_CAP_MODULATOR | V4L2_CAP_RDS_OUTPUT`.

Risks: the command/startup protocol is reverse-engineered and order-sensitive. The shared buffer is reused for send and receive and is protected only by the video-device mutex in normal userspace paths. `si4713_i2c_read` returns success with `data[0] = 0` on timeout so the core driver sees CTS missing rather than a transport error. `si4713_start_seq` continues through the entire sequence and returns only the final command status, so earlier startup failures can be overwritten by later success.

Test signals: USB probe on `10c4:8244`, startup command trace matching expected Windows-derived sequence, synthetic I2C subdevice creation, V4L2 frequency/modulator/RDS controls, disconnect while open, and USB timeout/error injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/si4713/radio-usb-si4713.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/si4713/si4713.c -->
# sources/distributed-fs/ceph-client/drivers/media/radio/si4713/si4713.c

Purpose: core I2C V4L2 subdevice driver for the Silicon Labs Si4713 FM radio transmitter. It implements command transport, power sequencing, transmitter tuning, RDS/RadioText loading, V4L2 controls, modulator/frequency subdev ops, and optional platform-device creation for user-visible radio nodes.

Important APIs and functions: low-level command helpers are `si4713_send_command`, `si4713_read_property`, `si4713_write_property`, `si4713_powerup`, `si4713_powerdown`, `si4713_checkrev`, and `si4713_wait_stc`. TX/RDS helpers include `si4713_tx_tune_freq`, `si4713_tx_tune_power`, `si4713_tx_tune_measure`, `si4713_tx_tune_status`, `si4713_tx_rds_buff`, `si4713_tx_rds_ps`, `si4713_set_rds_ps_name`, and `si4713_set_rds_radio_text`. V4L2 entry points are `si4713_s_ctrl`, private `si4713_ioctl` for `SI4713_IOC_MEASURE_RNL`, `g/s_modulator`, `g/s_frequency`, and the `si4713_probe`/`si4713_remove` I2C lifecycle.

Control flow: probe allocates `si4713_device`, acquires optional reset GPIO and `vdd`/`vio` regulators, initializes the V4L2 I2C subdev and completion, creates a large clustered control set anchored by `V4L2_CID_AUDIO_MUTE`, optionally requests an IRQ for CTS/STC completion, powers up just long enough to validate product revision, then powers down. If device tree or platform data requests a platform radio wrapper, probe allocates `radio-si4713` and passes the I2C client as platform data. Control flow on unmute powers up, unmutes, tunes to cached/default frequency, applies modulator mode, and then forces all clustered controls into hardware. Muting writes line-input mute and powers down.

State and persistence: `struct si4713_device` stores the V4L2 subdevice, control handler and control pointers, completion, optional regulators/GPIO, optional platform device, power state, RDS enabled flag, cached frequency, stereo/preemphasis state, and latest received noise level. Hardware properties are not persisted across power down; cached software control values are replayed after power-up through the cluster.

Dependencies and integration points: depends on Linux I2C, completion, IRQ, GPIO descriptor, regulator, V4L2 subdev/control/common/ioctl APIs, platform data from `linux/platform_data/media/si4713.h`, and constants from `si4713.h`. It integrates with platform and USB wrappers as a subdevice and with userspace through V4L2 controls and private RNL measurement ioctl.

Risks: regulator error handling in `si4713_powerup` can leave `vdd` enabled if enabling `vio` fails before command send. Completion reuse lacks visible reinitialization before each command, so stale completions could shorten waits on IRQ-driven paths. `si4713_s_ctrl` assumes the mute control is the cluster anchor and returns `-EINVAL` for direct non-anchor callbacks. RDS RadioText inserts a static carriage-return block by reassigning the input pointer, which is compact but easy to misread. Frequency and alternate-frequency conversions are integer and clamp-heavy, so boundary behavior should be tested.

Test signals: I2C probe with and without IRQ, regulator/GPIO power sequencing, product revision check, mute/unmute replay of all controls, frequency range clamping, RDS PS and RadioText programming, RNL measurement ioctl, USB wrapper polling behavior, and remove while powered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/si4713/si4713.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/si4713/si4713.h -->
# sources/distributed-fs/ceph-client/drivers/media/radio/si4713/si4713.h

Purpose: private/public contract for the Si4713 driver stack. It defines command IDs, argument/response sizes, property IDs, device limits, control bounds, private state, and the platform-data handoff used by the radio wrapper.

Important APIs and types: `struct si4713_device` contains the V4L2 subdev/control handler, 29-control cluster pointers, completion, regulators, reset GPIO, optional platform device, and cached transmitter state. `struct radio_si4713_platform_data` passes an I2C client to `radio-platform-si4713.c`. Macros define power-up/down commands, tune commands, status bits (`SI4713_CTS`, `SI4713_ERR`, `SI4713_STC_INT`), property addresses (`SI4713_TX_COMPONENT_ENABLE`, RDS, limiter, pilot, compression), RDS string limits, power/frequency/antenna bounds, and preemphasis values.

Control flow: executable code in `si4713.c`, `radio-usb-si4713.c`, and `radio-platform-si4713.c` consumes these constants to build command buffers, decode responses, configure controls, and instantiate the platform wrapper.

State and persistence: the header defines the shape of volatile driver state only. The cached fields in `struct si4713_device` are replayed into hardware after power-up because the chip loses active property state after power-down/reset.

Dependencies and integration points: includes platform device, regulator, GPIO, V4L2 subdev/control, and platform-data headers. The command constants are shared by both physical I2C and USB-emulated-I2C paths.

Risks: the control cluster is represented as an anonymous struct embedded in `si4713_device`; code depends on the control pointer order matching the `v4l2_ctrl_cluster(29, &sdev->mute)` call. Large RDS limits permit scrolling extensions beyond strict RDS nominal sizes. Command sizes must remain synchronized with the transport wrappers' command tables.

Test signals: compile coverage across all three Si4713 modules, static inspection that command table sizes match macros, V4L2 control creation count/order, and runtime tests for power-up, tuning, RDS, and private RNL ioctl.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/si4713/si4713.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/tea575x.c -->
# sources/distributed-fs/ceph-client/drivers/media/radio/tea575x.c

Purpose: reusable V4L2 radio support library for Philips TEA5757/TEA5759 AM/FM tuner chips, historically used by sound-card radio devices. It bit-bangs or delegates the 25-bit tuner protocol, exposes V4L2 tuner/frequency/seek ioctls, and registers/unregisters a `video_device` for parent drivers.

Important APIs and functions: exported APIs are `snd_tea575x_set_freq`, `snd_tea575x_enum_freq_bands`, `snd_tea575x_g_tuner`, `snd_tea575x_s_hw_freq_seek`, `snd_tea575x_hw_init`, `snd_tea575x_init`, and `snd_tea575x_exit`. Internal helpers include `snd_tea575x_write`, `snd_tea575x_read`, `snd_tea575x_val_to_freq`, `snd_tea575x_get_freq`, V4L2 ioctl handlers, `tea575x_s_ctrl`, and the file/ioctl/control templates.

Control flow: init validates readback if supported, programs default FM frequency 90.5 MHz, copies a video-device template, sets device caps and file ops, optionally creates a mute control, runs parent `ext_init`, sets controls, and registers a radio node. Frequency set chooses AM, Japanese FM, or standard FM band, clamps to band limits, computes tuner PLL bits with IF offsets, writes the 25-bit word, and updates cached frequency. Hardware seek starts the chip seek bit, polls until search clears or times out, filters wrong-direction/too-small moves, and stops on signal interruption or success.

State and persistence: parent-owned `struct snd_tea575x` holds current 25-bit value, frequency, band, stereo/tuned flags, mute state, capabilities, V4L2 device/video/control state, and chip-specific ops. Hardware state is updated by serial writes and can be read back only if the board supports data reads.

Dependencies and integration points: depends on `media/drv-intf/tea575x.h` for board ops and constants, V4L2 device/dev/fh/ioctl/event APIs, and low-level parent callbacks `set_direction`, `set_pins`, `get_pins`, or direct `read_val`/`write_val`. It integrates as a library, not a standalone bus driver.

Risks: boards with `cannot_read_data` cannot support bounded hardware seek and may expose less state fidelity. Bit-banged timing uses small `udelay` intervals and depends on parent GPIO/IO callbacks. Seek blocks for up to 10 seconds and refuses nonblocking file handles. `snd_tea575x_init` frees the control handler on some errors, so parent drivers must not double-free it.

Test signals: parent-driver builds, readback probe on hardware that supports it, FM/AM band enumeration and clamping, mute control, hardware seek timeout/signal paths, and unload/reload leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/tea575x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/tef6862.c -->
# sources/distributed-fs/ceph-client/drivers/media/radio/tef6862.c

Purpose: V4L2 I2C subdevice driver for the Philips/NXP TEF6862 car-radio tuner, supporting basic FM tuner status and frequency programming.

Important APIs and functions: `struct tef6862_state` stores the subdev and cached frequency. Tuner ops are `tef6862_g_tuner`, `tef6862_s_tuner`, `tef6862_s_frequency`, and `tef6862_g_frequency`; lifecycle functions are `tef6862_probe` and `tef6862_remove`. `tef6862_sigstr` reads four bytes and reports signal strength from the fourth response byte.

Control flow: probe checks adapter functionality, logs the chip address, allocates state, initializes default low frequency, and registers as a V4L2 I2C subdevice. Setting frequency clamps to 87.5-108 MHz in V4L2 low-frequency units, converts to a PLL value with a fixed formula, and writes a three-byte preset-mode I2C message. Getting tuner fills a mono FM tuner descriptor and reads signal strength.

State and persistence: the only software state is cached `freq`. Hardware PLL state persists in the tuner until reprogrammed or powered down externally. The driver does not cache signal strength or other register state.

Dependencies and integration points: depends on Linux I2C and V4L2 subdev/tuner APIs. It is intended to be instantiated by a parent media device that owns the I2C adapter and routes V4L2 tuner subdev calls.

Risks: probe checks `I2C_FUNC_SMBUS_BYTE_DATA` but uses `i2c_master_send`/`recv`, so the functionality check is only an approximate gate. Signal strength is a crude high-byte value. Only FM is supported; `s_tuner` accepts index zero but ignores requested mode. No runtime PM or explicit power sequencing exists.

Test signals: I2C probe/remove, frequency programming at band edges, parent subdev tuner calls, signal-strength reads, and build coverage with media I2C tuner users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/tef6862.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/rc/Kconfig

Purpose: top-level Kconfig menu for Linux remote-controller core support, LIRC/raw IR interfaces, protocol decoders, and standalone IR/RF receiver/transmitter drivers.

Important APIs and symbols: `RC_CORE` gates the subsystem and depends on input. `BPF_LIRC_MODE2` enables eBPF attachment to LIRC raw devices when `RC_CORE=y`, `LIRC`, and `BPF_SYSCALL` are present. `LIRC` enables `/dev/lirc*`. `RC_DECODERS` gates protocol decoder tristates such as NEC, RC5, RC6, JVC, Sony, Sanyo, Sharp, XMP, MCE keyboard, iMON, and RC-MM. `RC_DEVICES` gates hardware drivers including ENE, Fintek, GPIO RX/TX, USB receivers/transceivers, Super I/O CIR devices, serial/SPI/PWM transmitters, ATI/X10 RF remotes, loopback, ST, and Xbox DVD receiver. It sources keymaps and ImgTec IR Kconfig files.

Control flow: the selected symbols drive the rc Makefile, which builds the rc core, raw decoders, keymaps, and hardware drivers. Dependencies constrain drivers to required buses, architecture features, PNP, GPIO, PWM, USB, LIRC, timers, or compile-test paths.

State and persistence: no runtime state. Config selections persist in the kernel config and determine available modules and built-in decoders/devices.

Dependencies and integration points: integrates media rc-core with Linux input, BPF, LIRC, USB, PNP, OF/GPIO, PWM, SPI, architecture-specific SoC drivers, LEDs, and the `img-ir` subdirectory.

Risks: dependency accuracy is critical because many drivers perform direct I/O port or timing-sensitive operations. `BPF_LIRC_MODE2` requires built-in rc-core (`RC_CORE=y`), so it is not available for modular rc-core. Some help text exposes hardware limitations, such as IgorPlugUSB's very small pulse buffer.

Test signals: Kconfig dependency tests, `allmodconfig`/`randconfig`, module build matrix, and runtime checks that selected decoders/devices register expected rc-core capabilities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/rc/Makefile

Purpose: kbuild recipe for the remote-controller subsystem, protocol decoders, keymaps, and hardware drivers.

Important APIs and entries: `rc-core-y := rc-main.o rc-ir-raw.o`, with optional `lirc_dev.o`, CEC keymap support, and `bpf-lirc.o`. It always descends into `keymaps/`. It maps each `CONFIG_IR_*` decoder/device and `CONFIG_RC_*` driver to the matching object, and descends into `img-ir/` for `CONFIG_IR_IMG`.

Control flow: selected Kconfig symbols determine object inclusion. The file intentionally keeps decoder and standalone driver lists alphabetically sorted by Kconfig name.

State and persistence: no runtime state; build composition only.

Dependencies and integration points: depends on symbols from `drivers/media/rc/Kconfig` and child Kconfig files. The core object aggregates LIRC and BPF support when enabled rather than building them as unrelated modules.

Risks: breaking alphabetical order is a maintainability issue flagged by comments. Adding a Kconfig symbol without a matching object entry produces a visible configuration that builds no code. Optional `rc-core-*` additions must match symbols that are valid when `RC_CORE` is selected.

Test signals: targeted builds for each listed driver/decoder, `make W=1` for object lists, and Kconfig-to-Makefile consistency checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/ati_remote.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/ati_remote.c

Purpose: USB driver for ATI/X10 RF remote receivers, exposing non-mouse remote buttons through rc-core scancodes and optional pointer/mouse-like events through the input subsystem.

Important APIs and functions: module parameters are `channel_mask`, `debug`, `repeat_filter`, `repeat_delay`, and `mouse`. Device identity and keymap selection use `ati_remote_table`, `struct ati_receiver_type`, and `get_medion_keymap`. Runtime state is `struct ati_remote`. Main functions include `ati_remote_open/close`, input and rc open/close wrappers, `ati_remote_sendpacket`, `ati_remote_initialize`, `ati_remote_input_report`, interrupt callbacks `ati_remote_irq_in/out`, buffer allocation/free, input/rc initialization, `ati_remote_probe`, and `ati_remote_disconnect`.

Control flow: probe validates two interrupt endpoints, allocates URBs/coherent buffers and an rc device, detects model-specific keymap, initializes USB interrupt URBs and sends two hardware init packets, registers the rc device, optionally registers an input mouse device, and stores driver data. On first rc/input open it submits the IN URB; last close kills it. Each input packet is validated by length/header/checksum/channel, masked by `channel_mask`, decoded into either mouse events, scrollwheel repeats, or rc-core keydown/keyup events. The IN URB resubmits itself after each successful packet.

State and persistence: state is in `struct ati_remote`: URBs, coherent buffers, endpoint descriptors, rc/input device pointers, duplicate/repeat timing, acceleration timing, names/phys paths, wait queue, send flags, and open-user count. No persistent storage exists; remote channel configuration is external to the driver.

Dependencies and integration points: depends on USB input helpers, wait queues/jiffies, mutexes, and rc-core. Integrates with rc keymaps such as ATI X10, Medion variants, and SnapStream Firefly, plus the input subsystem for pointer events.

Risks: `ati_remote_alloc_buffers` returns failure on partial allocation but cleanup must tolerate NULL members, which current free paths do. Duplicate filtering is heuristic and intentionally bypasses rc-core repeat handling to avoid regressions. The `mouse` module parameter is read-only after load. Channel masks use one-based bit numbering in user-facing documentation but zero-based remote numbers internally.

Test signals: probe for all USB IDs, Medion descriptor-based keymap selection, open/close reference counting across rc and mouse users, checksum/channel filtering, repeat behavior, pointer acceleration, disconnect while open, and module parameter coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/ati_remote.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/bpf-lirc.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/bpf-lirc.c

Purpose: eBPF integration for LIRC mode2/raw IR devices. It lets users attach BPF programs to raw IR samples and use helper calls to emit rc-core key, repeat, or relative-pointer events.

Important APIs and functions: exports `lirc_mode2_prog_ops` and `lirc_mode2_verifier_ops`. BPF helpers are `bpf_rc_repeat`, `bpf_rc_keydown`, and `bpf_rc_pointer_rel`, with prototypes selected by `lirc_mode2_func_proto`. Attachment lifecycle uses `lirc_prog_attach`, `lirc_prog_detach`, `lirc_prog_query`, `lirc_bpf_attach`, `lirc_bpf_detach`, `lirc_bpf_run`, and `lirc_bpf_free`.

Control flow: verifier access permits only a single read-only `u32` context sample. Attach obtains an `rc_dev` from a target fd, requires `RC_DRIVER_IR_RAW`, locks `ir_raw_handler_lock`, copies the old BPF program array with the new program appended, swaps it with RCU, and frees the old array. Detach performs the inverse and drops program references. Raw IR receive code calls `lirc_bpf_run`, which stores the sample in `ir_raw_event_ctrl` and runs the RCU-protected program array. Query returns attach flags and program IDs to userspace.

State and persistence: BPF program arrays live under `rcdev->raw->progs` and are RCU-managed. `raw->bpf_sample` is the per-run context value. Program references persist until detach or `lirc_bpf_free`, which must run after the rc thread is stopped and under the raw handler lock.

Dependencies and integration points: depends on Linux BPF/filter APIs, `linux/bpf_lirc.h`, rc-core private raw handler state, input relative events, rc key helpers, and RCU. Kconfig requires built-in rc-core for BPF LIRC support.

Risks: maximum attached programs is fixed at 64. Attach/detach correctness depends on `ir_raw_handler_lock` and RCU lifetime ordering. Helpers can emit input/rc events from BPF program logic, so verifier restrictions and helper availability are the main safety boundary. `trace_printk` is exposed only with token `CAP_PERFMON`.

Test signals: BPF attach/detach/query via `bpf(2)`, verifier rejection of invalid context access, multiple program ordering, raw IR sample processing, helper-generated key/repeat/pointer events, and teardown after rc device removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/bpf-lirc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/ene_ir.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/ene_ir.c

Purpose: PNP driver for ENE KB3926-series consumer IR receivers/transceivers. It directly programs ENE embedded-controller registers to receive raw IR samples, optionally detect carrier/learning input, transmit IR, and support wake from suspend.

Important APIs and functions: module parameters are `sample_period`, `learning_mode_force`, `debug`, and `txsim`. Register helpers are `ene_read_reg`, `ene_write_reg`, mask helpers, and `ene_hw_detect`. RX paths include buffer setup/restoration, pointer tracking, carrier sensing, input selection, `ene_rx_setup`, enable/disable/reset, and ISR sample extraction. TX paths include carrier/transmitter setup, `ene_tx_enable`, `ene_tx_sample`, simulated TX timer, and `ene_transmit`. rc-core callbacks include open/close, `s_idle`, wideband receiver, carrier report, TX mask/carrier/duty, and transmit. Lifecycle is `ene_probe`, `ene_remove`, suspend/resume/shutdown.

Control flow: probe validates PNP I/O and IRQ resources, detects hardware revision/features and firmware buffer layout, sets default RX/TX settings, configures hardware, registers an rc raw device, requests I/O region and shared IRQ. Open enables RX firmware/IRQ and input path. ISR acknowledges ENE IRQ status, feeds TX samples on TX interrupts, reads RX ring-buffer samples, converts space/pulse duration using sample period or fan-input resolution, reports optional carrier events, and calls `ir_raw_event_handle`. TX primes two hardware output slots, then interrupt/timer callbacks continue feeding chunks until completion or timeout.

State and persistence: `struct ene_device` tracks PNP resources, hardware feature flags, ring-buffer addresses and pointers, saved config register, TX buffer/progress/completion/timer, TX carrier/duty/mask, RX learning/carrier/period state, and whether RX is enabled. Hardware register configuration is reuploaded on resume and restored on remove where extra firmware buffers were modified.

Dependencies and integration points: depends on PNP, I/O port access, shared IRQs, timers/completions, spinlocks, and rc-core raw IR APIs. Header `ene_ir.h` provides register map and state structure. It integrates with wakeup-capable PNP devices matching `ENE0100`, `ENE0200`, `ENE0201`, and `ENE0202`.

Risks: heavy direct hardware manipulation under spinlocks makes register ordering important. Probe registers the rc device before requesting I/O/IRQ, so error paths must unregister carefully. `txsim` can force TX capability on unsupported hardware and is explicitly dangerous. Carrier/duty setting uses `BUG_ON` for invalid duty values inside carrier programming. Extra-buffer validation failures degrade to legacy buffering and may reduce RX reliability.

Test signals: PNP probe on B/C/D revisions, RX sample decoding with and without extra buffers/fan input, learning mode and carrier reports, TX mask/carrier/duty/transmit completion, suspend/resume wake behavior, shutdown wake enable, and stress tests for ISR ring-buffer wrap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/ene_ir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/ene_ir.h -->
# sources/distributed-fs/ceph-client/drivers/media/rc/ene_ir.h

Purpose: register map, bit definitions, debug macros, hardware-version constants, and private state declaration for the ENE KB3926 CIR driver.

Important APIs and types: `struct ene_device` describes PNP/rc resources, hardware I/O and IRQ, hardware feature flags, extra RX buffer metadata, RX/TX runtime state, TX settings, RX settings, and synchronization primitives. Register macros define indexed I/O ports, firmware sample buffers/flags, IRQ registers for revision B versus C/D, CIR config/data/modulation/carrier registers, fan-input registers, GPIO transmitter selectors, PLL/version registers, and IRQ type bits.

Control flow: `ene_ir.c` uses these definitions to detect hardware revision, configure firmware buffers, select RX inputs, demodulate carrier, feed TX samples, handle interrupts, and manage wake. Function prototypes for `ene_irq_status` and `ene_rx_read_hw_pointer` support cross-use within the C file.

State and persistence: the header defines volatile driver state and hardware register addresses. Some hardware buffer addresses are saved so remove can restore firmware buffer pointers after module reload.

Dependencies and integration points: includes `linux/spinlock.h` and is private to the ENE rc driver. Debug macros rely on the C file's `debug` module parameter.

Risks: many magic register addresses are chip-specific and revision-sensitive. Comments note typos and uncertain protocol knobs, so untested register changes can regress hardware. `struct ene_device` stores caller TX buffer pointers directly during transmit, requiring synchronous completion semantics.

Test signals: compile coverage, static checks that C code and header feature flags match, hardware detection logs for each revision, and RX/TX tests exercising every state field path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/ene_ir.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/fintek-cir.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/fintek-cir.c

Purpose: PNP driver for Fintek LPC Super I/O consumer IR receivers/transceivers. It configures the CIR logical device, receives raw IR packets from I/O registers, registers an rc-core raw receiver, and enables CIR wake support.

Important APIs and functions: config helpers include `fintek_cr_read/write`, config-mode enter/exit, logical-device selection, CIR register read/write, and `cir_dump_regs`. Hardware setup uses `fintek_hw_detect`, `fintek_cir_ldev_init`, `fintek_cir_regs_init`, and `fintek_enable_wake`. RX parsing uses `fintek_cmdsize`, `fintek_get_rx_ir_data`, and `fintek_process_rx_ir_data`. Interrupt/lifecycle callbacks are `fintek_cir_isr`, `fintek_open`, `fintek_close`, `fintek_probe`, `fintek_remove`, `fintek_suspend`, `fintek_resume`, and `fintek_shutdown`.

Control flow: probe validates PNP port/IRQ resources, initializes config port defaults, detects vendor/chip/logical-device revision and TX capability, programs CIR base/IRQ into the logical device, clears/enables CIR interrupts, fills an rc raw device descriptor, requests the I/O region and shared IRQ, registers rc-core, and enables wake capability. ISR selects the CIR logical device, reads status, drains RX data while receive/timeout flags remain, parses command/data versus pulse samples, stores raw IR events, acknowledges status bits, and returns handled. Open enables the logical device and interrupts; close disables it. Suspend disables IRQ/logical device and enables ACPI wake bits; resume re-enables and reinitializes registers.

State and persistence: `struct fintek_dev` stores PNP resources, locks, RX parse buffer and parser state, config/index ports, CIR address/IRQ/length, chip IDs, feature flags, learning/carrier flags, TX queue fields reserved by the structure, and carrier. Hardware configuration is reprogrammed on resume; wake bits may persist through shutdown for IR power-on.

Dependencies and integration points: depends on PNP, direct I/O port access, shared IRQs, spinlocks, wait queues, and rc-core raw event APIs. Header `fintek-cir.h` supplies the register map and state. PNP table matches `FIT0002`.

Risks: `fintek_hw_detect` reads `CIR_CR_CLASS` through the CIR runtime register accessor while in config mode, which is unusual because class is documented as a config register; behavior depends on chip decode semantics. TX-capable fields exist but this file exposes only RX callbacks, so transmit support is incomplete or absent. RX buffer length is 32 bytes but the hardware drain loop increments `pkts` without an explicit bound check. Wake enable is unconditional on remove/shutdown.

Test signals: PNP probe on supported Fintek chips, config port 0x2e/0x4e fallback, RX packet parsing including command headers and overflow, interrupt ack behavior, suspend/resume wake tests, and debug register dump validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/fintek-cir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/fintek-cir.h -->
# sources/distributed-fs/ceph-client/drivers/media/rc/fintek-cir.h

Purpose: private definitions for the Fintek LPC Super I/O CIR driver, including register addresses, packet constants, debug macros, and `struct fintek_dev`.

Important APIs and types: `struct fintek_dev` captures PNP/rc resources, spinlocks, RX packet buffer/parser state, TX staging queue fields, config-register ports, CIR I/O resources, chip/vendor IDs, logical-device number, feature flags, learning/carrier flags, and current carrier period. Macros cover Fintek vendor ID, config-mode magic, global control registers, CIR logical-device registers, ACPI wake registers, CIR runtime registers/status bits, RX/TX packet encodings, and sample period.

Control flow: `fintek-cir.c` consumes these definitions for hardware detection, logical-device setup, IRQ handling, raw sample parsing, power management, and wake enablement.

State and persistence: header state is in-memory driver state plus hardware register constants. Wake configuration registers can persist across suspend/shutdown as platform firmware-visible state.

Dependencies and integration points: includes spinlock and ioctl headers and is private to `fintek-cir.c`. Debug macros use the translation unit's `debug` module parameter.

Risks: TX-related fields and packet constants are present even though the C file does not expose TX rc-core callbacks, which can mislead maintainers. Parser constants mirror MCEUSB-like framing and must stay synchronized with hardware packet format. Direct I/O register constants are revision-sensitive.

Test signals: compile coverage, hardware detection logs, parser tests using known packet streams, and suspend/resume wake register validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/fintek-cir.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/gpio-ir-recv.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/gpio-ir-recv.c

Purpose: platform driver for simple GPIO-based IR receivers. It converts GPIO edges into rc-core raw IR events and optionally uses runtime PM/QoS to reduce first-edge latency on cpuidle-sensitive systems.

Important APIs and functions: `struct gpio_rc_dev` stores the rc device, GPIO descriptor, IRQ, optional PM device, and CPU latency QoS request. Main functions are `gpio_ir_recv_irq`, `gpio_ir_recv_probe`, `gpio_ir_recv_remove`, system suspend/resume callbacks, and runtime suspend/resume callbacks.

Control flow: probe requires a device-tree node, gets an input GPIO and maps it to an IRQ, allocates an `RC_DRIVER_IR_RAW` device, fills protocols/timeouts/keymap from `linux,rc-map-name` or `RC_MAP_EMPTY`, registers rc-core, configures optional autosuspend from `linux,autosuspend-period`, stores drvdata, and requests both-edge IRQ. The IRQ optionally runtime-resumes the device, reads GPIO level, stores an edge event (`val == 1` as pulse), and schedules autosuspend.

State and persistence: state is devm-managed per platform device. Runtime PM and QoS state persist while the driver is bound. No IR data is persisted beyond rc-core raw event queues.

Dependencies and integration points: depends on OF, GPIO descriptors, IRQ, runtime PM, CPU latency QoS, platform bus, and rc-core. Device-tree compatible is `gpio-ir-receiver`.

Risks: the QoS remove path is called during runtime suspend/remove, so it relies on runtime resume having added the request first. Edge polarity is hard-coded from GPIO value and may depend on device-tree GPIO flags. The IRQ is requested after rc registration, so a request failure leaves only devm cleanup and registered rc device rollback through managed resources.

Test signals: device-tree probe, both-edge IRQ capture, keymap property handling, wakeup-source suspend behavior, autosuspend-period PM behavior, and rc-core decoder output under tight pulse timings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/gpio-ir-recv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/gpio-ir-tx.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/gpio-ir-tx.c

Purpose: platform raw IR transmitter that bit-bangs a GPIO, either unmodulated or modulated at a configured carrier and duty cycle.

Important APIs and functions: `struct gpio_ir` stores the GPIO, carrier, and duty cycle. rc-core callbacks are `gpio_ir_tx`, `gpio_ir_tx_set_carrier`, and `gpio_ir_tx_set_duty_cycle`. Timing helpers are `delay_until`, `gpio_ir_tx_unmodulated`, and `gpio_ir_tx_modulated`. Probe is `gpio_ir_tx_probe`.

Control flow: probe allocates state and an `RC_DRIVER_IR_RAW_TX` device, gets an output-low GPIO, assigns transmit and carrier/duty callbacks, defaults to 38 kHz and 50 percent duty cycle, and registers rc-core. Transmit disables local IRQs, then either toggles the GPIO for each pulse/space or generates carrier cycles during pulse intervals using `ndelay`, `udelay`, and `mdelay` until the requested waveform is complete.

State and persistence: only carrier and duty-cycle settings persist in driver memory while bound. GPIO is driven low after unmodulated transmit and naturally ends low after modulated pulse loops.

Dependencies and integration points: depends on OF, GPIO descriptors, platform bus, delay/timing helpers, and rc-core raw TX. Device-tree compatible is `gpio-ir-tx`; Kconfig excludes PREEMPT_RT because transmit disables local IRQs and busy-waits.

Risks: bit-banged timing blocks the CPU with local interrupts disabled and can affect latency. Carrier is limited to 500 kHz but duty cycle is not range-checked in this file. Long buffers can monopolize CPU time. Timing accuracy depends on GPIO latency and busy-wait calibration.

Test signals: waveform capture with a logic analyzer for default and custom carriers/duty cycles, unmodulated mode with carrier set to zero, invalid high carrier rejection, rc-core TX API tests, and latency testing on target SoCs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/gpio-ir-tx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/igorplugusb.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/igorplugusb.c

Purpose: USB raw IR receiver driver for IgorPlugUSB-compatible devices. It polls a vendor control endpoint, decodes the device's small pulse/space buffer, and feeds rc-core raw IR decoders.

Important APIs and functions: `struct igorplugusb` stores the rc device, USB control URB/request, polling timer, input buffer, and physical path. Core functions are `igorplugusb_cmd`, `igorplugusb_timer`, `igorplugusb_callback`, `igorplugusb_irdata`, `igorplugusb_probe`, and `igorplugusb_disconnect`.

Control flow: probe validates a single control-IN endpoint, allocates request/URB/buffer, initializes a polling timer, builds a vendor IN control request, allocates and registers an `RC_DRIVER_IR_RAW` device with limited allowed protocols, stores driver data, and sends `SET_INFRABUFFER_EMPTY`. Timer callbacks submit `GET_INFRACODE`. URB completion either decodes received IR data, schedules the next poll after 50 ms, or clears the hardware buffer after errors. Decoding handles circular overwrite indicated by the overflow byte, converts byte samples to 85-us pulse/space durations, adds a trailing timeout space, and calls `ir_raw_event_handle`.

State and persistence: runtime state is the URB, timer, buffer, and rc-core device. Device firmware buffer is explicitly cleared after reads or errors. No settings are persisted.

Dependencies and integration points: depends on USB core/control URBs, timers, and rc-core raw APIs. USB IDs include Atmel `03eb:0002` and Fit PC2 `03eb:21fe`; default keymap is Hauppauge.

Risks: hardware stores only 36 pulses/spaces, so long protocols are disabled and overflow loses data. Polling every 50 ms can miss bursts if the device overwrites its buffer repeatedly. Error cleanup must coordinate poisoned URBs and timer deletion; the code uses poison/unpoison around teardown.

Test signals: USB probe for both IDs, polling cadence, overflow handling, raw event durations at 85-us resolution, disabled protocol mask behavior, disconnect during active polling, and error URB statuses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/igorplugusb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/iguanair.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/iguanair.c

Purpose: USB raw IR receiver/transmitter driver for IguanaWorks USB IR transceivers. It receives compact raw samples, transmits carrier-period encoded waveforms, and exposes rc-core RX/TX callbacks.

Important APIs and functions: `struct iguanair` stores rc device, USB device, firmware version/features, RX/TX URBs and DMA buffers, completion, receiver state, carrier, and TX packet. Key functions are `process_ir_data`, `iguanair_rx`, `iguanair_send`, `iguanair_get_features`, `iguanair_receiver`, TX callbacks `iguanair_set_tx_carrier`, `iguanair_set_tx_mask`, `iguanair_tx`, rc open/close, probe/disconnect, and suspend/resume.

Control flow: probe validates interrupt endpoints, allocates coherent IN/OUT buffers and URBs, submits the IN URB, sends a NOP and feature queries, rejects firmware older than `0x0205`, fills an rc raw device with RX/TX callbacks and timeouts, defaults to 38 kHz and no TX mask, registers rc-core, and stores USB data. Incoming URBs either complete control commands or decode seven-byte IR sample packets into pulse/space events. TX converts microsecond durations to carrier periods, chunks into 7-bit payload entries with pulse/space markers, sends the packet, and reports overflow if firmware returns `CMD_TX_OVERFLOW`. Suspend disables receiver if active and kills URBs; resume resubmits RX and reenables receiver.

State and persistence: state includes firmware version, buffer size, cycle overhead, current carrier, TX channel mask, receiver-on flag, and DMA-backed packet buffers. Settings persist only while the USB device remains bound.

Dependencies and integration points: depends on USB interrupt URBs, coherent DMA buffers, completions, and rc-core raw RX/TX APIs. USB ID is `1781:0938`; default map is RC6 MCE.

Risks: TX packet size is bounded by firmware-reported `bufsize`; long waveforms return `-EINVAL`. Carrier generation relies on firmware CPU-cycle calculations and `cycle_overhead` from feature query. Probe submits the RX URB before feature negotiation, so control responses and raw packets share the same IN path. `iguanair_send` waits for `TIMEOUT` jiffies, not milliseconds, because it passes the raw constant to `wait_for_completion_timeout`.

Test signals: firmware version/feature negotiation, RX sample decoding including `0x80` long space, TX carrier/mask/waveform output, overflow reporting, open/close receiver commands, suspend/resume, and disconnect during active RX/TX.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/iguanair.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/img-ir/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/rc/img-ir/Kconfig

Purpose: Kconfig options for the Imagination Technologies IR decoder block, selecting raw mode, hardware decode mode, and per-protocol hardware decoders.

Important APIs and symbols: `IR_IMG` is the main tristate and depends on `RC_CORE` plus MIPS or compile-test. `IR_IMG_RAW` enables raw edge reporting. `IR_IMG_HW` enables hardware decode and is selected by default when raw mode is not enabled. Protocol booleans `IR_IMG_NEC`, `IR_IMG_JVC`, `IR_IMG_SONY`, `IR_IMG_SHARP`, `IR_IMG_SANYO`, `IR_IMG_RC5`, and `IR_IMG_RC6` depend on hardware decode, with NEC selecting `BITREVERSE`.

Control flow: selected symbols determine which objects the img-ir Makefile links into the aggregate `img-ir.o` module and which decode modes/protocols are available to runtime setup.

State and persistence: no runtime state. Configuration persists in the kernel build config.

Dependencies and integration points: sourced from the rc device menu. Integrates ImgTec platform hardware with rc-core raw decoders or hardware scancode decode support.

Risks: enabling only raw mode trades reliability and CPU use for protocol flexibility, as documented in help text. Hardware RC6 support is limited to mode 0. Protocol booleans do nothing without `IR_IMG_HW`.

Test signals: Kconfig matrix builds for raw-only, hardware-only, and protocol combinations; module contents matching enabled protocols; device-tree probe on compatible hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/img-ir/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/img-ir/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/rc/img-ir/Makefile

Purpose: kbuild composition for the ImgTec IR decoder aggregate module.

Important APIs and entries: `img-ir-y := img-ir-core.o`; optional objects are appended for raw mode, hardware mode, and each enabled hardware protocol decoder. `img-ir-objs := $(img-ir-y)` builds the aggregate object, and `obj-$(CONFIG_IR_IMG) += img-ir.o` adds it to the parent build.

Control flow: kbuild links selected source files into one `img-ir.o`, so the core platform driver and optional raw/hardware/protocol helpers share one module boundary.

State and persistence: no runtime state; object composition only.

Dependencies and integration points: depends on symbols from `img-ir/Kconfig`. The core file expects helper functions from raw/hardware objects to be present or stubbed according to configuration.

Risks: optional protocol objects must stay synchronized with Kconfig names and helper declarations in local headers. Missing an object can produce unresolved symbols only for specific configuration combinations.

Test signals: targeted builds for each `IR_IMG_*` combination and link tests for raw-only, hardware-only, and multi-protocol configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/img-ir/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/img-ir/img-ir-core.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/img-ir/img-ir-core.c

Purpose: core platform driver for the ImgTec IR decoder hardware block. It maps device resources, manages clocks and interrupts, initializes raw and hardware decode subcomponents, and dispatches IRQ status to the enabled decode path.

Important APIs and functions: main functions are `img_ir_isr`, `img_ir_setup`, `img_ir_ident`, `img_ir_probe`, and `img_ir_remove`. It uses helper APIs declared in `img-ir.h`, including `img_ir_read/write`, `img_ir_setup_raw/hw`, `img_ir_probe_raw/hw`, `img_ir_remove_raw/hw`, `img_ir_raw_enabled`, `img_ir_hw_enabled`, `img_ir_isr_raw`, `img_ir_isr_hw`, and PM callbacks `img_ir_suspend/resume`.

Control flow: probe gets IRQ and MMIO resources, allocates `img_ir_priv`, initializes a spinlock, maps registers, obtains optional core and sys clocks, enables sys clock before register access, probes raw and hardware decoders and requires at least one to succeed, requests IRQ, logs identity/modes, disables IRQs, sets up raw/hw subcomponents, and enables the core clock. ISR locks, reads and clears IRQ status, masks it by enabled bits, dispatches edge interrupts to raw handling when raw is enabled, dispatches data match/valid interrupts to hardware handling when hardware decode is enabled, then unlocks.

State and persistence: `img_ir_priv` stores device, register base, clocks, IRQ, spinlock, and raw/hardware substate. Clock and register state are runtime-only and restored through setup/resume paths.

Dependencies and integration points: depends on platform device resources, OF compatible `img,ir-rev1`, MMIO, clocks, IRQs, spinlocks, and local raw/hardware decode modules. It registers as one platform driver named `img-ir`.

Risks: core clock is enabled in `img_ir_setup` after raw/hw setup, while sys clock is enabled earlier for register access; clock ordering is hardware-sensitive. IRQ status is cleared before handler dispatch, so missed status capture would lose events. Probe succeeds if either raw or hardware decoder initializes, making partial-mode failures nonfatal. Error paths must remove whichever subcomponent succeeded.

Test signals: device-tree probe, sys/core clock availability and failure injection, IRQ dispatch for edge and data-valid/match bits, raw-only and hardware-only configurations, suspend/resume, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/img-ir/img-ir-core.c -->
