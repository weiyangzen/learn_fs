# subset-b-001205 Research

Grouped research report for the subset B work item. Each section is keyed by the original source path and is intended for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/tests/ni_routes_test.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/tests/ni_routes_test.c

## Purpose
This file is a loadable kernel-module unit test suite for the COMEDI National Instruments routing helpers implemented by `ni_routes.c` and described by `ni_routes.h`/`ni_stc.h`. It verifies that board-specific route tables are selected, sorted, counted, searched, and translated into register values correctly, including indirect routes through mux-like intermediate destinations such as `NI_RGOUT0` and `NI_RTSI_BRD(n)`.

## Important APIs, Types, And Functions
The test builds fake board state with `struct ni_board_struct board`, `struct ni_private private`, a synthetic `struct ni_device_routes DR`, and a synthetic route-value matrix `RV[NI_NUM_NAMES][NI_NUM_NAMES]`. Helper macros `O()`, `B()`, `V()`, and `RVI()` convert between NI symbolic names, table offsets, and encoded valid register values. `route_set_dests_in_order()` and `route_set_sources_in_order()` assert sorted table invariants.

The individual tests cover `ni_assign_device_routes()`, `ni_sort_device_routes()`, `ni_find_route_set()`, `ni_route_set_has_source()`, `ni_route_to_register()`, `ni_lookup_route_register()`, `route_is_valid()`, `ni_is_cmd_dest()`, `channel_is_pfi()`, `channel_is_rtsi()`, `ni_count_valid_routes()`, `ni_get_valid_routes()`, `ni_find_route_source()`, `route_register_is_valid()`, `ni_check_trigger_arg[_roffs]()`, and `ni_get_reg_value[_roffs]()`. Module entry `ni_routes_unittest()` passes these functions to `exec_unittests()`.

## Control Flow
The suite initializes one of three test board contexts (`pci-6070e`, `pci-6220`, or `pci-fake`) before each logical test. Real board tests assert that E-series and M-series table selection finds expected route sets and register encodings. The fake board tests sort the synthetic route set once, then exercise route lookup, validity, direct register lookup, indirect route resolution, trigger argument validation, and valid-route enumeration. Test failure reporting is non-fatal: every `unittest()` call updates global counters and logs through the kernel logging API, so all tests run even after earlier failures.

## State And Persistence
The file mutates static fake board globals only inside module lifetime. `init_private()` clears `private`; `init_pci_*()` assigns board names and routing table pointers. `ni_sort_device_routes(&DR)` permanently orders the static synthetic route list for later tests in the same module load. No state persists after module unload except kernel log output.

## Dependencies And Integration Points
The test depends on COMEDI NI internals, not only public APIs: it includes `../ni_stc.h` and `../ni_routes.h` and directly instantiates `struct ni_private`. It integrates with the local minimal test framework in `unittest.h` and with Linux module init/exit macros. It is normally built only as part of the COMEDI driver tests.

## Risks And Edge Cases
The tests intentionally rely on hard-coded table sizes and route counts, so legitimate route-table updates can require test updates. Fake routes use names offset from `NI_NAMES_BASE`; an enum layout change could invalidate assumptions. The indirect-route cases are important because direct lookup intentionally rejects muxed paths while `ni_route_to_register()` resolves them. The suite does not test concurrent access, memory allocation failures, or all real boards.

## Test Signals
Strong signals are the expected route-set count for `pci-6070e`, different route-value matrices for `pci-6070e` and `pci-6220`, sortedness of route sets and sources, valid route count `57` for the fake device, invalid return codes such as `-EINVAL`, and correct register values for direct and indirect trigger paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/tests/ni_routes_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/tests/unittest.h -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/tests/unittest.h

## Purpose
This header provides a tiny in-kernel unit-test harness for COMEDI driver tests. It is intentionally simple: tests are void functions, assertions log pass/fail messages, and a module init routine can execute a null-terminated array of test function pointers.

## Important APIs, Types, And Functions
`struct unittest_results` holds global `passed` and `failed` counters for the including translation unit. `typedef void (*unittest_fptr)(void)` defines the test function signature. The `unittest(result, fmt, ...)` macro evaluates a condition, increments counters, logs failures via `pr_err()` with function and line context, and logs passes via `pr_debug()`. `exec_unittests(const char *name, const unittest_fptr *unit_tests)` runs the null-terminated array and prints begin/end summary messages through `pr_info()`.

## Control Flow
Including tests call `exec_unittests()` from module init. It iterates until a `NULL` function pointer, invoking each test synchronously. Each test calls `unittest()` as many times as needed; failures do not abort the current test or the suite.

## State And Persistence
The only mutable state is the static `unittest_results` instance in the including object. Results accumulate for the module load and are not reset by `exec_unittests()`. There is no persistence beyond kernel log messages and module memory lifetime.

## Dependencies And Integration Points
The harness assumes kernel logging helpers and `bool` are available through the including C file's kernel headers. It is not a generic KUnit integration; it has no TAP output, no failure return to module loading, and no isolation between test functions.

## Risks And Edge Cases
Because `unittest_results` is static in a header, each translation unit gets a separate counter, which is fine for the current one-file test pattern but can surprise multi-file users. `exec_unittests()` does not clear counters, so calling it more than once reports cumulative results. Tests that need hard failure semantics must add their own control flow.

## Test Signals
Useful signals are `pr_err("FAIL ...")` lines for individual assertion failures and the final summary showing passed and failed counts. Debug pass logs require dynamic debug or a debug log level.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/tests/unittest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/usbdux.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/usbdux.c

## Purpose
This is the COMEDI USB low-level driver for Stirling/ITL USB-DUX devices. It exposes analog input, analog output, digital I/O, counter, and, on high-speed devices, PWM subdevices. Streaming AI/AO uses isochronous URBs, while single-shot instructions, DIO, counters, firmware upload, and PWM control use bulk or control transfers to device firmware.

## Important APIs, Types, And Functions
`struct usbdux_private` stores URB arrays, firmware command buffers, single-instruction buffers, high-speed capability, running flags for AI/AO/PWM, scan timers/counters, and a mutex serializing command paths. Range tables define 12-bit AI and AO voltage ranges. AI entry points are `usbdux_ai_cmdtest()`, `usbdux_ai_cmd()`, `usbdux_ai_inttrig()`, `usbdux_ai_cancel()`, and `usbdux_ai_insn_read()`. AO equivalents are `usbdux_ao_cmdtest()`, `usbdux_ao_cmd()`, `usbdux_ao_inttrig()`, `usbdux_ao_cancel()`, `usbdux_ao_insn_write()`, and readback via `usbdux_ao_insn_read()`.

`send_dux_commands()` and `receive_dux_commands()` are the firmware command channel helpers. `usbdux_dio_insn_bits()` and `usbdux_dio_insn_config()` handle 8-bit DIO. `usbdux_counter_read()`, `usbdux_counter_write()`, and `usbdux_counter_config()` expose firmware timers. PWM support is handled by `usbdux_pwm_period()`, `usbdux_pwm_start()`, `usbdux_pwm_cancel()`, `usbdux_pwm_pattern()`, `usbdux_pwm_write()`, and `usbdux_pwm_config()`. Attachment is handled by `usbdux_auto_attach()`, USB probe by `usbdux_usb_probe()`, and cleanup by `usbdux_detach()`.

## Control Flow
Attach allocates private state, determines high-speed mode, allocates URBs and buffers, sets USB alternate setting 3, loads `usbdux_firmware.bin`, and registers four or five COMEDI subdevices. AI command validation constrains trigger sources and scan periods to USB frame or microframe rates. AI command setup writes the channel list to firmware, computes interval/timer counters, then either submits all AI URBs immediately for `TRIG_NOW` or installs `inttrig`. Completion copies ISO data, performs bipolar offset munging, writes samples to the COMEDI async buffer, checks stop count, resubmits the URB, and manually calls `comedi_event()`.

AO streaming mirrors AI: command setup computes a millisecond timer, completion pulls samples from the COMEDI buffer, formats channel/value triplets, updates readback, resubmits, and reports underflow or EOA events. Single AI/AO and DIO paths take the private mutex, send a command, and optionally wait for the matching response. PWM starts firmware mode, repeatedly resubmits a bulk URB containing a generated duty-cycle pattern, and stops on cancel or URB error.

## State And Persistence
State is in `usbdux_private` and COMEDI subdevice state. `ai_cmd_running`, `ao_cmd_running`, and `pwm_cmd_running` gate concurrent command starts and completion resubmission. AO readback persists last written values in `s->readback`. DIO direction/state lives in the COMEDI subdevice and is pushed to firmware during `insn_bits`, not during `insn_config`. Firmware is uploaded at attach and device memory/buffers are freed at detach.

## Dependencies And Integration Points
The driver depends on COMEDI USB helpers (`comedi_usb_auto_config`, `module_comedi_usb_driver`, `comedi_load_firmware`), COMEDI async buffer helpers, Linux USB URB APIs, and firmware file `usbdux_firmware.bin`. USB IDs are `0x13d8:0x0001` and `0x13d8:0x0002`. It integrates with the COMEDI core through subdevice callbacks and with Linux firmware loading through `MODULE_FIRMWARE`.

## Risks And Edge Cases
Streaming completion cannot call `comedi_handle_events()` because cancel would unlink the currently executing URB, so manual event/cancel handling is delicate. Several error paths during buffer allocation return without locally freeing partially allocated resources, relying on later detach or core cleanup. Command/response matching retries only a fixed number of times. High-speed timing depends on power-of-two channel intervals. PWM period limits are encoded through FX2 delay math and unsupported values return `-EAGAIN`.

## Test Signals
Behavioral signals include successful firmware load, USB alternate setting selection, valid `cmdtest` normalization of scan periods, no URB resubmit errors, correct COMEDI buffer samples with bipolar offset munging, AO readback matching writes, DIO bit reads after command round trips, and clean cancellation/unlink behavior under disconnect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/usbdux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/usbduxfast.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/usbduxfast.c

## Purpose
This COMEDI USB driver supports USB-DUX-FAST devices, a high-speed analog-input-only board. It programs FX2/GPIF waveform descriptors for selected channel patterns and streams samples from a bulk IN endpoint to the COMEDI async buffer.

## Important APIs, Types, And Functions
`struct usbduxfast_private` holds one bulk URB, the command descriptor buffer `duxbuf`, input buffer `inbuf`, an async running flag, an initial packet ignore counter, and a mutex. `usbduxfast_send_cmd()` sends the descriptor buffer to endpoint 4. `usbduxfast_cmd_data()` fills one GPIF state descriptor. Streaming is implemented by `usbduxfast_ai_cmdtest()`, `usbduxfast_ai_check_chanlist()`, `usbduxfast_ai_cmd()`, `usbduxfast_ai_inttrig()`, `usbduxfast_ai_cancel()`, `usbduxfast_submit_urb()`, `usbduxfast_ai_interrupt()`, and `usbduxfast_ai_handle_urb()`. Single reads are handled by `usbduxfast_ai_insn_read()`. Firmware upload uses `usbduxfast_upload_firmware()`.

## Control Flow
Attach requires USB high speed, switches to alternate setting 1, allocates the URB and buffers, loads `usbduxfast_firmware.bin`, and registers one AI subdevice. `cmdtest` accepts `TRIG_NOW`, `TRIG_EXT`, or `TRIG_INT` starts, `TRIG_FOLLOW` scan begin, timer-based convert timing, and count/none stop. It restricts channel lists to 1, 2, 3, or 16 consecutive channels and requires matching gains for lists longer than three channels.

`usbduxfast_ai_cmd()` converts `convert_arg` into 30 MHz GPIF steps, fills waveform descriptors according to channel count and trigger mode, sends them to firmware, then starts the bulk URB immediately for `TRIG_NOW`/`TRIG_EXT` or installs `inttrig`. The completion path ignores the first four packets to flush stale quad-buffered device data, writes the remaining samples to COMEDI, checks stop count, resubmits, and reports events. Single reads program a fixed descriptor sequence, discard initial packets, then collect the requested channel from 16-channel-aligned packets.

## State And Persistence
`ai_cmd_running` protects async streaming from single reads and repeated starts. `ignore` is reset for each command and decremented in completions. Hardware state consists mainly of GPIF command descriptors in firmware. There is no readback or persistent calibration state in the driver.

## Dependencies And Integration Points
The driver depends on COMEDI USB support, firmware loading, Linux USB bulk URBs, and USB IDs `0x13d8:0x0010`/`0x13d8:0x0011`. It exposes one `COMEDI_SUBD_AI` with 16 channels, two bipolar ranges, 12-bit-plus-overflow maxdata, async command support, and single instruction reads.

## Risks And Edge Cases
The channel list restrictions are strict and hardware-specific. `usbduxfast_ai_inttrig()` returns `1` on successful trigger rather than `0`, which is unusual but existing behavior. Timing conversion rounds through integer `steps`; `cmdtest` adjusts invalid values but can be sensitive to nanosecond-to-step rounding. Bulk transfer errors and corrupted packet lengths abort with COMEDI error events or `-EINVAL`. Allocation failures after partial attach need normal driver-core cleanup coverage.

## Test Signals
Signals include attach rejection on non-high-speed USB, successful firmware load and alternate setting switch, `cmdtest` acceptance only for legal channel lists and timing, initial packet discard before samples are reported, no bulk URB resubmit errors, and correct single-read channel extraction from 16-channel packets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/usbduxfast.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/usbduxsigma.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/usbduxsigma.c

## Purpose
This COMEDI USB driver supports USB-DUX-SIGMA devices. It exposes 24-bit analog input, 8-bit analog output, 24-bit digital I/O, and high-speed-only PWM. It is similar to `usbdux.c` but uses different firmware commands, larger AI samples, sigma ADC configuration bytes, and a startup status/health read.

## Important APIs, Types, And Functions
`struct usbduxsigma_private` tracks AI/AO URB arrays, a PWM URB, command/response buffers, high-speed mode, running flags, timers, intervals, and a mutex. AI operations are implemented by `usbduxsigma_ai_cmdtest()`, `usbduxsigma_ai_cmd()`, `usbduxsigma_ai_inttrig()`, `usbduxsigma_ai_cancel()`, `usbduxsigma_ai_insn_read()`, `usbduxsigma_ai_urb_complete()`, and `usbduxsigma_ai_handle_urb()`. AO operations are implemented by matching `usbduxsigma_ao_*` routines. `usbduxsigma_dio_insn_bits()` and `usbduxsigma_dio_insn_config()` manage 24 DIO lines. PWM operations are implemented by `usbduxsigma_pwm_*`. `usbduxsigma_getstatusinfo()` reads ADC system channels for health/status. Attach, firmware upload, and detach are handled by `usbduxsigma_auto_attach()`, `usbduxsigma_firmware_upload()`, and `usbduxsigma_detach()`.

## Control Flow
Attach determines full/high-speed mode, allocates buffers and URBs, selects alternate setting 3, loads `usbduxsigma_firmware.bin`, registers three or four subdevices, sets default PWM period when present, and reads ADC zero status to confirm communication. AI `cmdtest` chooses an interval from channel count, enforces USB frame or microframe minimum scan periods, and rounds scan timing down to supported units. AI command builds ADC mux bitmasks for selected channels, sends an AD command to firmware, computes a timer, and submits URBs now or later via internal trigger. Completions copy big-endian 32-bit samples, strip status byte, offset-munge 24-bit values, write samples to COMEDI, and resubmit.

AO command mode uses one millisecond scan timing, fills isochronous output packets from the COMEDI async buffer, and updates readback. Single AO writes send one channel/value command at a time. DIO writes pack direction and state across three bytes and reads state back from firmware. PWM uses a high-speed bulk URB pattern buffer and command-controlled firmware mode.

## State And Persistence
The private running flags gate concurrent operations. AI and AO timer/counter fields downsample URB completions to requested scan periods. DIO direction and state live in the COMEDI subdevice and are synchronized on `insn_bits`. AO readback persists last written values. PWM pattern bytes persist in the URB transfer buffer until overwritten or stopped.

## Dependencies And Integration Points
The driver depends on COMEDI USB helpers, Linux USB isochronous/bulk/control APIs, unaligned big-endian loads, and firmware `usbduxsigma_firmware.bin`. USB IDs are `0x13d8:0x0020`, `0x13d8:0x0021`, and `0x13d8:0x0022`. It integrates with COMEDI through AI/AO/DIO/PWM subdevice callbacks and firmware loading through `MODULE_FIRMWARE`.

## Risks And Edge Cases
The file contains a misspelled helper name `usbbuxsigma_send_cmd()`, which is harmless internally but easy to misread. `usbduxsigma_ao_cmdtest()` calls `mutex_unlock(&devpriv->mut)` on an early validation error despite not locking the mutex in that function; this is a high-risk bug signal if that path is reachable. Several partial allocation paths return errors without local unwind. USB sample format handling depends on a leading DIO/status word and 24-bit ADC values inside 32-bit big-endian fields. PWM control lacks explicit mutex use in several paths compared with AI/AO.

## Test Signals
Key signals include successful firmware upload, successful ADC zero status read, valid `cmdtest` timing rounding, correct 24-bit sample offset munging, DIO state round trips across three bytes, AO readback updates, PWM start/stop status, and no URB resubmit failures during disconnect/cancel stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/usbduxsigma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/vmk80xx.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/vmk80xx.c

## Purpose
This COMEDI USB low-level driver supports Velleman K8055/VM110 and K8061/VM140 boards. It exposes instruction-based analog input/output, digital input/output, counters, and K8061 PWM using synchronous USB interrupt or bulk packet exchanges.

## Important APIs, Types, And Functions
`struct vmk80xx_board` describes per-model capabilities such as channel counts, ranges, maxdata, and PWM availability. `struct vmk80xx_private` stores endpoint descriptors, a semaphore limiting concurrent USB packet access, RX/TX buffers, and model type. USB transport is abstracted by `vmk80xx_read_packet()`, `vmk80xx_write_packet()`, and `vmk80xx_do_bulk_msg()`, with K8055 using interrupt endpoints and K8061 using paired bulk transfers.

COMEDI callbacks include `vmk80xx_ai_insn_read()`, `vmk80xx_ao_insn_write()`, `vmk80xx_ao_insn_read()`, `vmk80xx_di_insn_bits()`, `vmk80xx_do_insn_bits()`, `vmk80xx_cnt_insn_read()`, `vmk80xx_cnt_insn_config()`, `vmk80xx_cnt_insn_write()`, `vmk80xx_pwm_insn_read()`, and `vmk80xx_pwm_insn_write()`. Attach helpers are `vmk80xx_find_usb_endpoints()`, `vmk80xx_alloc_usb_buffers()`, `vmk80xx_reset_device()`, `vmk80xx_init_subdevices()`, `vmk80xx_auto_attach()`, and `vmk80xx_detach()`.

## Control Flow
Probe passes the USB ID's `driver_info` to COMEDI auto configuration. Attach selects board info, allocates private data, initializes a semaphore count of 8, finds suitable endpoints, allocates endpoint-sized buffers with a 64-byte minimum, stores interface data, resets K8055 output state, and registers subdevices. Each instruction operation takes `limit_sem`, prepares or reads packet bytes according to model-specific register layout, performs one USB transfer per requested sample or update, then releases the semaphore.

AI reads select K8055 AI registers or K8061 channel command bytes. AO writes update model-specific output registers and K8061 AO can be read back by sending `VMK8061_CMD_RD_AO`. Digital input decodes K8055 bit layout or reads K8061 byte directly. Digital output uses COMEDI state update logic and optionally reads K8061 DO state back. K8055 counters support debounce-time writes using an integer square-root conversion and reset commands; K8061 counters are read/reset only. K8061 PWM values are split into low two bits and upper bits according to vendor DLL behavior.

## State And Persistence
The driver keeps shared USB TX/RX buffers and COMEDI digital output state. K8055 output state is initialized by reset/write during attach because outputs cannot be read back. AO and PWM state mostly resides on hardware; only K8061 readback commands query it. No async streaming state exists.

## Dependencies And Integration Points
The driver depends on COMEDI USB auto configuration, Linux USB endpoint discovery and synchronous message APIs, COMEDI range helpers, and board USB IDs under vendor `0x10cf`. It registers a `vmk80xx` COMEDI driver paired with a USB driver and supports multiple product IDs for both K8055 and K8061 families.

## Risks And Edge Cases
`vmk80xx_do_bulk_msg()` ignores return values from its write and read bulk messages, so K8061 transport failures can be masked. The semaphore count of 8 allows several threads into shared buffers at once, which does not provide exclusive packet-buffer protection; if concurrent instructions occur, TX/RX buffer contents can race. K8061 counter indexing is opaque and marked questionable in comments. Counter debounce conversion clamps to 7450 ms but notes overflow prevention is incomplete. K8055 output reset is best-effort because its return value is ignored by attach.

## Test Signals
Useful signals include successful endpoint discovery for interrupt versus bulk models, attach reset on K8055, correct DIO bit remapping for K8055, K8061 AO/PWM readback consistency, counter reset/write behavior, and tests that run concurrent instructions to expose shared buffer races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/vmk80xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/z8536.h -->
# sources/distributed-fs/ceph-client/drivers/comedi/drivers/z8536.h

## Purpose
This header defines symbolic register offsets and bit fields for the Zilog Z8536 CIO device. It is a hardware-description header used by COMEDI drivers that need to program the CIO's interrupt, port, counter/timer, data direction, handshake, and pattern-match registers.

## Important APIs, Types, And Functions
There are no functions or types. The API surface is a set of `#define` constants. Major groups include master interrupt control (`Z8536_INT_CTRL_*`), master configuration (`Z8536_CFG_CTRL_*`), interrupt vector registers, command/status registers and command encodings (`Z8536_CMD_*`, `Z8536_STAT_*`), port data registers, counter current-count and reload registers, counter mode bits, port mode bits, handshake fields, data path polarity, data direction, special I/O, and pattern polarity/transition/mask registers.

## Control Flow
The header has no runtime control flow. Drivers include it and compose register writes from offsets and bit masks. Parameterized macros such as `Z8536_CT_CMDSTAT_REG(x)`, `Z8536_CT_VAL_MSB_REG(x)`, `Z8536_CT_RELOAD_LSB_REG(x)`, and `Z8536_CT_MODE_REG(x)` map counter index to register address.

## State And Persistence
No state is stored in this header. Persistent behavior is entirely in the Z8536 hardware registers written by consumers.

## Dependencies And Integration Points
The header expects Linux `BIT()` to be available before use. It integrates at the register-programming boundary and should stay synchronized with Z8536 hardware documentation and any COMEDI drivers that use these symbolic names.

## Risks And Edge Cases
Macros are untyped and can be combined incorrectly by callers. Several fields use overlapping bit positions for different register contexts, so consumers must use the correct register group. Some comments encode important polarity semantics, such as data direction `0 = output` and cable/pattern behavior; losing those semantics can cause inverted hardware behavior.

## Test Signals
Tests are indirect: consuming drivers should verify register writes against expected Z8536 values, especially counter mode setup, interrupt enable/clear commands, port direction/polarity, and pattern match masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/drivers/z8536.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/kcomedilib/Makefile -->
# sources/distributed-fs/ceph-client/drivers/comedi/kcomedilib/Makefile

## Purpose
This Makefile builds the kernel COMEDI library object for in-kernel users of comedilib-like helpers.

## Important APIs, Types, And Functions
It sets `ccflags-$(CONFIG_COMEDI_DEBUG) := -DDEBUG`, adds `kcomedilib.o` when `CONFIG_COMEDI_KCOMEDILIB` is enabled, and defines `kcomedilib-objs := kcomedilib_main.o`.

## Control Flow
Kbuild evaluates the config-dependent object line and links `kcomedilib_main.o` into `kcomedilib.o` when selected.

## State And Persistence
No runtime state exists. The file controls build output only.

## Dependencies And Integration Points
It integrates with Kbuild, `CONFIG_COMEDI_DEBUG`, and `CONFIG_COMEDI_KCOMEDILIB`. The resulting object exports symbols from `kcomedilib_main.c`.

## Risks And Edge Cases
Any additional source file for the library must be added to `kcomedilib-objs`. Debug behavior depends on the global COMEDI debug config.

## Test Signals
Build signals are whether `kcomedilib.o` appears only under `CONFIG_COMEDI_KCOMEDILIB` and whether `-DDEBUG` is present only under `CONFIG_COMEDI_DEBUG`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/kcomedilib/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/kcomedilib/kcomedilib_main.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/kcomedilib/kcomedilib_main.c

## Purpose
This file implements a small GPL-exported COMEDI kernel library for other kernel modules. It lets kernel code open COMEDI devices by `/dev/comediN`, safely close them, issue DIO configuration and bitfield instructions, find subdevices, and query channel counts.

## Important APIs, Types, And Functions
Exported APIs are `comedi_open_from()`, `comedi_close_from()`, `comedi_dio_get_config()`, `comedi_dio_config()`, `comedi_dio_bitfield2()`, `comedi_find_subdevice_by_type()`, and `comedi_get_n_channels()`. Internal helper `comedi_do_insn()` validates attachment, subdevice index, subdevice usability, chanlist, and busy state before dispatching `INSN_BITS` or `INSN_CONFIG`. Link tracking is handled by `kcomedilib_set_link_from_to()` and `kcomedilib_clear_link_from_to()` using `kcomedilib_to_from[COMEDI_NUM_BOARD_MINORS][COMEDI_NUM_BOARD_MINORS]`.

## Control Flow
`comedi_open_from()` parses `/dev/comediN`, obtains a COMEDI device reference, checks attachment under `attach_lock`, and records an open edge from one device minor to another. The edge insertion walks the reverse link graph under a mutex to reject loops and caps duplicate edge counts at 255. On failure the device reference is dropped. `comedi_close_from()` removes one edge and releases the device reference.

DIO helpers construct `struct comedi_insn` objects and call `comedi_do_insn()`. `comedi_dio_bitfield2()` additionally handles base-channel shifting for subdevices with up to 32 channels because most drivers ignore `insn->chanspec` for `INSN_BITS`. Query helpers use `attach_lock` to read subdevice metadata safely.

## State And Persistence
The main persistent state is the static link-count matrix, protected by `kcomedilib_to_from_lock`. It records concurrent kernel opens between COMEDI minors and prevents dependency cycles. Subdevice busy state is temporarily set in `comedi_do_insn()` while an instruction executes.

## Dependencies And Integration Points
The file depends on COMEDI core internals (`comedi_dev_get_from_minor`, `comedi_dev_put`, `comedi_check_chanlist`, subdevice callbacks, locks, and busy state) and exports symbols for GPL kernel modules. It integrates with standard COMEDI instruction semantics rather than user-space file descriptors.

## Risks And Edge Cases
The graph loop check assumes the existing matrix is loop-free. If callers mismatch `from` values between open and close, link counts can become inaccurate. `comedi_do_insn()` has comments noting incomplete lock and instruction-length checks. Only `INSN_BITS` and `INSN_CONFIG` are supported. Base-channel shifting in `comedi_dio_bitfield2()` is only corrected for `n_chan <= 32`.

## Test Signals
Useful tests include opening invalid names and minors, refusing open loops, duplicate open count saturation, close decrement behavior, DIO config/query dispatch, bitfield base-channel shifting, busy subdevice rejection, and attach/detach races around `attach_lock`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/kcomedilib/kcomedilib_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/proc.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/proc.c

## Purpose
This file implements the legacy `/proc/comedi` read-only status interface. It reports the COMEDI release, attached devices, and registered COMEDI drivers/board names.

## Important APIs, Types, And Functions
`comedi_read(struct seq_file *m, void *v)` is the proc show callback. `comedi_proc_init()` creates the proc entry with `proc_create_single("comedi", 0444, NULL, comedi_read)`. `comedi_proc_cleanup()` removes it.

## Control Flow
When `/proc/comedi` is read, the callback prints a header and iterates all board minors. For each existing device, it takes `dev->attach_lock`, prints attached device minor, driver name, board name, and subdevice count, then releases the lock and device reference. If none are attached it prints `no devices`. It then locks `comedi_drivers_list_lock` and walks the global `comedi_drivers` list to print each driver's board names using the driver's `board_name`, `num_names`, and `offset` fields.

## State And Persistence
The file owns no device state. It observes COMEDI devices and driver registration lists at read time. The proc entry persists from COMEDI proc init to cleanup.

## Dependencies And Integration Points
It depends on COMEDI internal globals and helpers, Linux procfs, and seq_file. It is tied to the COMEDI core's minor namespace and driver registration list.

## Risks And Edge Cases
The output format is legacy and string-based. Board-name access uses pointer arithmetic through `driver->board_name` and `driver->offset`, so malformed driver metadata could produce bad output. The snapshot can change between devices because only per-device and driver-list locks are held, not a global COMEDI snapshot lock.

## Test Signals
Signals include `/proc/comedi` existence after init, correct `no devices` output when none are attached, attached device rows with expected driver/board/subdevice counts, and complete driver board-name listing under concurrent registration changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/proc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/range.c -->
# sources/distributed-fs/ceph-client/drivers/comedi/range.c

## Purpose
This file defines common COMEDI range tables and implements range metadata validation/copying for the `COMEDI_RANGEINFO` ioctl plus channel-list validation for subdevices.

## Important APIs, Types, And Functions
Exported range tables include `range_bipolar10`, `range_bipolar5`, `range_bipolar2_5`, `range_unipolar10`, `range_unipolar5`, `range_unipolar2_5`, current ranges `range_0_20mA`, `range_4_20mA`, `range_0_32mA`, and `range_unknown`. `do_rangeinfo_ioctl()` validates a `struct comedi_rangeinfo` request and copies the selected `struct comedi_krange` array to user memory. `comedi_check_chanlist()` validates channel and range indexes for each chanspec in a command or instruction.

## Control Flow
`do_rangeinfo_ioctl()` decodes subdevice and channel from `range_type`, verifies device attachment and subdevice bounds, selects either a shared `s->range_table` or per-channel `s->range_table_list`, verifies requested range length against the table length, and uses `copy_to_user()` to return the range array. `comedi_check_chanlist()` loops over each chanspec, resolves the correct range length from shared or per-channel range tables, and rejects any channel outside `s->n_chan` or range index outside the table length.

## State And Persistence
The range table objects are immutable exported constants. No mutable persistent state is owned by this file.

## Dependencies And Integration Points
The file depends on COMEDI chanspec macros (`CR_CHAN`, `CR_RANGE`, `RANGE_LENGTH`), COMEDI subdevice range-table conventions, Linux uaccess, and COMEDI logging. It is used by ioctl handling, command validation, and kernel-library instruction validation.

## Risks And Edge Cases
Only channel and range index are validated by `comedi_check_chanlist()`; analog reference and flags are intentionally left to drivers. `range_type` packs subdevice/channel/length in fixed bit positions and bad user values return `-EINVAL`. Per-channel range tables require valid channel bounds before indexing.

## Test Signals
Tests should cover shared and per-channel range tables, wrong range lengths, invalid subdevice/channel indexes, `copy_to_user()` faults, valid and invalid chanspec lists, and driver-specific validation for references/flags outside this helper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/comedi/range.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/connector/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/connector/Kconfig

## Purpose
This Kconfig file defines build-time configuration for the kernel connector subsystem and its process-event producer.

## Important APIs, Types, And Functions
`menuconfig CONNECTOR` is a tristate option named "Connector - unified userspace <-> kernelspace linker" and depends on `NET`. `config PROC_EVENTS` is a bool option under `CONNECTOR`, depends on `CONNECTOR=y`, defaults to `y`, and enables process event reporting to userspace.

## Control Flow
Kconfig presents `PROC_EVENTS` only inside the connector menu. Because it depends on `CONNECTOR=y`, process events are available only when connector is built into the kernel, not when connector is a module.

## State And Persistence
No runtime state exists. The selections persist in kernel configuration and drive compiled objects.

## Dependencies And Integration Points
The file integrates with `drivers/connector/Makefile`, where `CONFIG_CONNECTOR` builds `cn.o` and `CONFIG_PROC_EVENTS` builds `cn_proc.o`.

## Risks And Edge Cases
The built-in-only dependency for `PROC_EVENTS` is important: enabling connector as a module does not allow process event support. The default `y` can expose process events whenever built-in connector is enabled.

## Test Signals
Configuration tests should confirm `CONNECTOR=n/m/y` object outcomes, `PROC_EVENTS` visibility only for built-in connector, and expected default selection behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/connector/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/connector/Makefile -->
# sources/distributed-fs/ceph-client/drivers/connector/Makefile

## Purpose
This Makefile maps connector Kconfig symbols to built objects.

## Important APIs, Types, And Functions
`obj-$(CONFIG_CONNECTOR) += cn.o` builds the main connector module/object. `obj-$(CONFIG_PROC_EVENTS) += cn_proc.o` builds process event connector support. `cn-y += cn_queue.o connector.o` links callback queue support and netlink transport into `cn.o`.

## Control Flow
Kbuild includes `cn_queue.o` and `connector.o` in the composite connector object whenever `CONFIG_CONNECTOR` is selected. `cn_proc.o` is separate and only built for process events.

## State And Persistence
No runtime state exists. This file controls build composition only.

## Dependencies And Integration Points
It depends on the symbols defined in `Kconfig` and on the implementation files `cn_queue.c`, `connector.c`, and `cn_proc.c`.

## Risks And Edge Cases
Adding new connector core sources requires updating `cn-y`. Building `cn_proc.o` separately means initialization ordering depends on connector core init being available for `cn_add_callback()`.

## Test Signals
Build tests should verify that `cn.o` contains both queue and transport code, that `cn_proc.o` appears only with `CONFIG_PROC_EVENTS`, and that module/built-in combinations match Kconfig constraints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/connector/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/connector/cn_proc.c -->
# sources/distributed-fs/ceph-client/drivers/connector/cn_proc.c

## Purpose
This file implements the process-events connector producer. It lets userspace subscribe over NETLINK_CONNECTOR and receive fork, exec, uid/gid, sid, ptrace, comm, coredump, and exit events from the initial pid/user namespace.

## Important APIs, Types, And Functions
The connector callback ID is `cn_proc_event_id = { CN_IDX_PROC, CN_VAL_PROC }`. Listener count is tracked by `proc_event_num_listeners`. `struct local_event` provides a per-CPU sequence counter protected by `local_lock_t`. `buffer_to_cn_msg()` aligns a stack buffer so the embedded `struct proc_event` is 8-byte aligned. Event emitters include `proc_fork_connector()`, `proc_exec_connector()`, `proc_id_connector()`, `proc_sid_connector()`, `proc_ptrace_connector()`, `proc_comm_connector()`, `proc_coredump_connector()`, and `proc_exit_connector()`. Subscription control is handled by `cn_proc_mcast_ctl()` and acknowledgements by `cn_proc_ack()`.

## Control Flow
Each event emitter first checks whether any listeners exist. It then fills a stack `cn_msg` and `proc_event`, timestamps it, copies relevant task identifiers under RCU where needed, sets message metadata, and calls `send_msg()`. `send_msg()` increments the per-CPU sequence, records CPU number, builds filter data, and broadcasts through `cn_netlink_send_mult()` with a per-socket filter.

Userspace controls subscriptions by sending either a `struct proc_input` or legacy multicast op. `cn_proc_mcast_ctl()` rejects callers outside the initial user and pid namespaces, stores per-socket subscription state in `sk_user_data`, updates the global listener count on LISTEN/IGNORE transitions, and sends an ack with positive errno-style values. `cn_proc_init()` registers the callback with the connector subsystem using `device_initcall`.

## State And Persistence
Persistent state includes global listener count, per-socket `struct proc_input` stored in `sk_user_data`, and per-CPU sequence counters. The state lives as long as connector sockets/callbacks exist. Socket cleanup is coordinated by connector release code in `connector.c`.

## Dependencies And Integration Points
The file depends on scheduler/process hooks calling its exported connector functions, connector core `cn_add_callback()` and `cn_netlink_send_mult()`, `linux/cn_proc.h` ABI structures, RCU task parent/credential access, pid/user namespace checks, and netlink socket user data.

## Risks And Edge Cases
The global listener count is an optimization and can become sensitive to missed LISTEN/IGNORE transitions. Event filtering is per socket and supports `PROC_EVENT_NONZERO_EXIT`. Process events are intentionally limited to init namespaces. Stack buffer alignment depends on `BUILD_BUG_ON(sizeof(struct cn_msg) != 20)`. Ack error values are positive errno numbers by ABI convention rather than normal negative kernel returns.

## Test Signals
Tests should cover subscribe/unsubscribe acks, per-event payload fields, namespace rejection, per-socket filters including nonzero exit, sequence ordering per CPU, listener count transitions, and cleanup of `sk_user_data` when sockets close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/connector/cn_proc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/connector/cn_queue.c -->
# sources/distributed-fs/ceph-client/drivers/connector/cn_queue.c

## Purpose
This file implements callback registration storage and lifetime management for the connector subsystem. It maintains a spinlock-protected list of connector callback entries keyed by connector IDs.

## Important APIs, Types, And Functions
`cn_queue_alloc_callback_entry()` allocates and initializes `struct cn_callback_entry`, sets its refcount, increments the parent queue device refcount, copies the callback name and ID, and stores the function pointer. `cn_queue_release_callback()` decrements the entry refcount, decrements the parent device refcount, and frees the entry on last reference. `cn_cb_equal()` compares connector IDs. Public queue operations are `cn_queue_add_callback()`, `cn_queue_del_callback()`, `cn_queue_alloc_dev()`, and `cn_queue_free_dev()`.

## Control Flow
Adding a callback allocates an entry first, then locks `queue_lock`, scans for duplicate IDs, and either appends to the list or releases the unused entry and returns `-EINVAL`. Deleting locks the list, removes the first matching entry, unlocks, then releases it. Freeing the queue removes all list entries under lock and then waits, sleeping one second at a time, until the queue device refcount reaches zero before freeing the device.

## State And Persistence
State lives in `struct cn_queue_dev`: callback list, queue lock, netlink socket pointer, name, and atomic refcount. Each callback entry has its own refcount and parent queue reference. Callback entries persist until explicitly deleted and until in-flight dispatch references are released.

## Dependencies And Integration Points
The file depends on connector data structures from `linux/connector.h`, kernel list/spinlock/refcount APIs, allocation helpers, and work with dispatch in `connector.c`, which takes temporary references before invoking callbacks.

## Risks And Edge Cases
`cn_queue_free_dev()` waits unboundedly for references to drain, which can delay module unload if callbacks are stuck. Duplicate detection is linear. Deletion removes the entry from the list before dropping the refcount, so in-flight callbacks can finish safely if dispatch took a ref. The `dev = NULL` assignment after `kfree()` is local only.

## Test Signals
Useful tests include duplicate ID rejection, callback add/delete races with dispatch, refcount drain on queue free, callback name truncation behavior, and correct parent refcount increments/decrements.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/connector/cn_queue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/connector/connector.c -->
# sources/distributed-fs/ceph-client/drivers/connector/connector.c

## Purpose
This file is the generic NETLINK_CONNECTOR transport and callback dispatch core. It lets kernel subsystems register callbacks by connector ID and exchange `struct cn_msg` messages with userspace via netlink unicast or multicast groups.

## Important APIs, Types, And Functions
The global connector device is `static struct cn_dev cdev`. Exported APIs are `cn_netlink_send_mult()`, `cn_netlink_send()`, `cn_add_callback()`, and `cn_del_callback()`. Internal functions include `cn_call_callback()` for received-message dispatch, `cn_bind()` for multicast permission checks, `cn_release()` for socket cleanup, `cn_rx_skb()` for netlink receive validation, `cn_proc_show()` for `/proc/net/connector`, `cn_init()`, and `cn_fini()`.

## Control Flow
`cn_init()` creates the NETLINK_CONNECTOR kernel socket in `init_net`, allocates a callback queue, marks the subsystem initialized, and creates `/proc/net/connector`. Incoming skbs are checked for netlink and connector message size, then `cn_call_callback()` finds a registered callback by ID, takes an entry refcount, invokes the callback with netlink parameters, frees the skb, and releases the ref. Outgoing `cn_netlink_send_mult()` resolves the multicast group either from explicit arguments or registered callback ID, checks listeners, allocates an skb, copies the message, and sends by broadcast with optional filter or unicast.

`cn_bind()` allows non-root binding only to the process-events multicast group; other groups require `CAP_NET_ADMIN`. `cn_release()` frees `sk_user_data` for sockets bound to the process group. `cn_fini()` removes proc state, frees callback queue, and releases the netlink socket.

## State And Persistence
`cdev` holds the netlink socket and callback queue. `cn_already_initialized` gates callback registration. Callback registration state is delegated to `cn_queue.c`. Per-socket process subscription state is freed here on release.

## Dependencies And Integration Points
The file depends on Linux netlink APIs, connector queue helpers, procfs/seq_file, capabilities, and connector ABI types. Subsystems such as `cn_proc.c` register callbacks with `cn_add_callback()` and send events with `cn_netlink_send_mult()`.

## Risks And Edge Cases
Message length validation is critical because `msg->len` comes from userspace. Broadcast filtering is optional and subsystem-provided. If no callback group is found and caller did not pass a group/portid, send returns `-ENODEV`. `cn_release()` assumes process connector ownership of `sk_user_data` for the CN_IDX_PROC group. Initialization order matters because `cn_add_callback()` returns `-EAGAIN` until the core is initialized.

## Test Signals
Tests should cover invalid netlink lengths, duplicate/missing callback dispatch, unicast and multicast send paths, listener absence returning `-ESRCH`, permission checks in `cn_bind()`, proc listing of registered callbacks, and callback registration before/after initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/connector/connector.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/counter/104-quad-8.c -->
# sources/distributed-fs/ceph-client/drivers/counter/104-quad-8.c

## Purpose
This is a Linux Counter subsystem driver for ACCES 104-QUAD-8 and 104-QUAD-4 PC/104 quadrature encoder counter boards. It manages eight 24-bit LS7267-style counters over ISA I/O ports, exposes count/signal/function/event controls through the generic Counter API, and handles board interrupts.

## Important APIs, Types, And Functions
Module parameters `base[]` and `irq[]` configure ISA port bases and interrupt lines. `struct quad8` stores a spinlock, shadow copies of CMR/IOR/IDR hardware control registers, filter clock prescalers, preset values, cable-fault enable bits, and a regmap. `quad8_regmap_config` wraps I/O port access with allowed read/write ranges.

Counter operations are collected in `quad8_ops`: `quad8_signal_read()`, `quad8_count_read()`, `quad8_count_write()`, `quad8_function_read()`, `quad8_function_write()`, `quad8_action_read()`, `quad8_events_configure()`, and `quad8_watch_validate()`. Extended attributes cover index polarity/synchronous mode, signal cable fault and filter prescaler, count ceiling/floor/mode/direction/enable/error/preset/preset-enable. Initialization and registration are handled by `quad8_probe()`, `quad8_init_counter()`, and `module_isa_driver_with_irq()`. Interrupts are handled by `quad8_irq_handler()`.

## Control Flow
Probe reserves and maps the ISA I/O range, initializes regmap and Counter device metadata, resets index/interrupt state, resets all counters, initializes each channel's prescaler, preset, flags, CMR, IOR, and IDR, disables cable status reporting, enables counters/interrupts, requests the configured IRQ, and registers the counter device.

Read/write operations take `priv->lock` where shadow registers and multi-step hardware sequences must stay atomic. Count reads transfer the counter to an output latch and read three little-endian bytes. Count writes temporarily load the requested value through the preset register, transfer it to the counter, reset flags, and restore the saved preset. Function and mode writes update shadow CMR/IDR/IOR arrays and write the selected control register. Event configuration maps requested Counter events to FLG pin modes and enables per-channel interrupt bits. The IRQ handler reads status, maps each asserted channel's FLG mode back to a Counter event, pushes events, and clears pending interrupts via the channel operation register.

## State And Persistence
Hardware state is mirrored in `cmr[]`, `ior[]`, `idr[]`, `preset[]`, `fck_prescaler[]`, and `cable_fault_enable` because many user-visible attributes need consistent readback and field updates. These fields persist while the device is registered. Actual count values, flags, and cable status live in hardware. No nonvolatile persistence is used.

## Dependencies And Integration Points
The driver depends on ISA bus support, I/O port mapping, regmap MMIO configured for I/O ports, Linux Counter core, IRQ handling, bitfield helpers, and unaligned 24-bit helpers. Kconfig selects `ISA_BUS_API` and `REGMAP_MMIO`; Makefile builds this file for `CONFIG_104_QUAD_8`.

## Risks And Edge Cases
The synchronous-mode setter appears to read `QUADRATURE_MODE` from `priv->idr[channel]` even though that field belongs to CMR, so validation may be wrong. `QUAD8_COUNT` declares three synapses but sets `num_synapses = 2`, which means index synapses may not be exposed despite index actions and signal definitions. Count writes modify preset hardware temporarily and must restore it correctly under lock. Interrupt event type is inferred from shadow IOR state; stale shadow state would mislabel events. Cable fault status is active-low and disabled channels return `-EINVAL`.

## Test Signals
Strong tests include probe with valid/invalid I/O regions, initial register programming, 24-bit count read/write and range errors, function/mode/preset/ceiling transitions, cable fault enable/read polarity, filter prescaler programming, event watch validation rejecting mixed events per channel, IRQ event mapping/clear behavior, and index/synchronous exposure through Counter sysfs/chrdev.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/counter/104-quad-8.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/counter/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/counter/Kconfig

## Purpose
This Kconfig file defines the generic Counter subsystem and individual counter-device driver options.

## Important APIs, Types, And Functions
`config I8254` is a hidden tristate library option selecting `COUNTER` and `REGMAP`. `menuconfig COUNTER` enables generic Counter device support. Under it, options include `104_QUAD_8`, `FTM_QUADDEC`, `INTEL_QEP`, `INTERRUPT_CNT`, `MICROCHIP_TCB_CAPTURE`, `RZ_MTU3_CNT`, `STM32_LPTIMER_CNT`, `STM32_TIMER_CNT`, `TI_ECAP_CAPTURE`, and `TI_EQEP`. Each option declares platform dependencies, selected support libraries, and module names in help text.

## Control Flow
Kconfig exposes individual drivers only when `COUNTER` is enabled. Dependency expressions limit hardware-specific drivers to matching architectures or `COMPILE_TEST`. Selection clauses pull in required libraries such as `REGMAP_MMIO`, `ISA_BUS_API`, or `REGMAP`.

## State And Persistence
No runtime state exists. The selected config persists in the kernel build configuration and controls object inclusion.

## Dependencies And Integration Points
It integrates with `drivers/counter/Makefile`, Linux architecture/platform symbols, and the generic Counter subsystem. The `104_QUAD_8` option specifically depends on PC/104 x86 or compile testing plus I/O port mapping.

## Risks And Edge Cases
Incorrect dependencies can expose drivers on platforms without required I/O resources or hide compile-test coverage. Library options like `I8254` are hidden and selected by consumers, so dependency loops or missing selects can break builds. Help text module names should remain synchronized with Makefile object names.

## Test Signals
Configuration matrix tests should cover `COUNTER=n/m/y`, compile-test builds, platform-gated visibility, selected helper symbols, and expected module object names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/counter/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/counter/Makefile -->
# sources/distributed-fs/ceph-client/drivers/counter/Makefile

## Purpose
This Makefile maps Counter subsystem Kconfig symbols to core and driver objects.

## Important APIs, Types, And Functions
`obj-$(CONFIG_COUNTER) += counter.o` builds the composite Counter core, with `counter-y := counter-core.o counter-sysfs.o counter-chrdev.o`. Individual driver mappings include `i8254.o`, `104-quad-8.o`, `interrupt-cnt.o`, `rz-mtu3-cnt.o`, `stm32-timer-cnt.o`, `stm32-lptimer-cnt.o`, `ti-eqep.o`, `ftm-quaddec.o`, `microchip-tcb-capture.o`, `intel-qep.o`, and `ti-ecap-capture.o`.

## Control Flow
Kbuild links the core composite object when `CONFIG_COUNTER` is enabled and includes driver objects according to their config symbols. `counter.o` combines core, sysfs, and character-device support.

## State And Persistence
No runtime state exists. The file controls compilation and linkage only.

## Dependencies And Integration Points
It depends on symbols declared in `Kconfig` and source files in the same directory. `104-quad-8.o` corresponds to the `CONFIG_104_QUAD_8` driver.

## Risks And Edge Cases
Adding or renaming drivers requires keeping Kconfig, Makefile, and help-text module names synchronized. The core object composition means sysfs and chrdev support are always linked with `CONFIG_COUNTER`.

## Test Signals
Build tests should verify object inclusion for each config symbol, module names, and the composite contents of `counter.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/counter/Makefile -->
