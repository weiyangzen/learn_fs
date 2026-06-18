# subset-b-004048 Research

Grouped research for the requested media common driver files. Each section title preserves the original source path and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/b2c2/flexcop-hw-filter.c -->
# sources/distributed-fs/ceph-client/drivers/media/common/b2c2/flexcop-hw-filter.c

Purpose: implements FlexCop transport-stream hardware filtering: receive-data gating, smartcard and null-packet filter bits, MAC filter programming, PID slot programming, and full-TS fallback.

Important APIs/functions: exported `flexcop_pid_feed_control()` is the DVB demux start/stop hook target. `flexcop_hw_filter_init()` clears all supported PID filters and enables null filtering. `flexcop_set_mac_filter()`, `flexcop_mac_filter_ctrl()`, and `flexcop_smc_ctrl()` configure MAC/SMC bits. Internal helpers map the first six named PID registers and optional 32 extra slots via `index_reg_310`/`pid_n_reg_314`.

Control flow: feed start/stop adjusts `fc->feedcount` and `fc->extra_feedcount`, programs a slot unless PID filtering is bypassed, then toggles group filtering/full-TS mode when filter capacity is exceeded or PID `0x2000` is requested. First feed enables receiver data and optional bus stream control; last feed disables streaming, resets block 300, and reinitializes filters.

State/persistence: state is volatile hardware register state plus in-memory counters (`feedcount`, `extra_feedcount`, `fullts_streaming_state`). No durable persistence.

Dependencies/integration: relies on `flexcop_ibi_value` register bitfields, `fc->read_ibi_reg`/`write_ibi_reg`, DVB demux feed indices, and bus-specific `stream_control`.

Risks/test signals: counter underflow or mismatched start/stop calls could leave full TS enabled. Boundary tests should cover six-slot mode, `skip_6_hw_pid_filter`, 32-slot mode, filter overflow, PID `0x2000`, first/last feed transitions, and MAC byte placement in registers `0x418`/`0x41c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/b2c2/flexcop-hw-filter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/b2c2/flexcop-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/media/common/b2c2/flexcop-i2c.c

Purpose: exposes the FlexCop internal two-wire controller as three Linux I2C adapters for demodulator, EEPROM, and tuner access.

Important APIs/functions: exported `flexcop_i2c_request()` performs chunked register reads/writes up to four bytes per hardware transaction. `flexcop_i2c_init()` registers the three adapters and marks `FC_STATE_I2C_INIT`; `flexcop_i2c_exit()` unregisters them. `flexcop_master_xfer()` adapts Linux `i2c_msg` sequences to FlexCop register operations. Internal `flexcop_i2c_operation()` starts a transfer and polls `tw_sm_c_100`.

Control flow: `master_xfer` serializes through `fc->i2c_mutex`, treats common one-byte/zero-byte read probes as successful no-ops, folds write-then-read message pairs into read requests, and maps other messages to writes. Request handling splits large buffers into four-byte transfers, increments base addresses, and retries reads for known card/gate quirks.

State/persistence: adapter state lives in `fc->fc_i2c_adap[]`, including port and `no_base_addr`; no persistent storage. Hardware state is reset per transfer by writing zero then command into `tw_sm_c_100`.

Dependencies/integration: depends on FlexCop IBI register definitions, Linux I2C core, device type `FC_SKY_REV27` workaround, and callers such as EEPROM/frontend/tuner setup.

Risks/test signals: polling limit (`FC_MAX_I2C_RETRIES`) can busy-loop; unsupported probe reads are intentionally faked. Tests should cover multi-chunk transfers, no-base-address writes, read retry behavior, adapter registration unwind, mutex interruption, and error mapping to `-EREMOTEIO`/`-ERESTARTSYS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/b2c2/flexcop-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/b2c2/flexcop-misc.c -->
# sources/distributed-fs/ceph-client/drivers/media/common/b2c2/flexcop-misc.c

Purpose: contains FlexCop identification and user-facing device-name logging helpers.

Important APIs/functions: `flexcop_determine_revision()` reads `misc_204`, maps revision nibbles to `FLEXCOP_II`, `FLEXCOP_IIB`, or `FLEXCOP_III`, and records whether the chip advertises 32 extra hardware PID filters. `flexcop_device_name()` formats bus/device/revision names for initialization logging.

Control flow: revision detection is a simple switch over `Rev_N_sig_revision_hi`, followed by capability-bit extraction from `Rev_N_sig_caps`. Device naming indexes static name tables by `fc->dev_type`, `fc->bus_type`, and `fc->rev`.

State/persistence: updates only in-memory `struct flexcop_device` fields (`rev`, `has_32_hw_pid_filter`) and emits logs. No durable persistence.

Dependencies/integration: relies on `flexcop-reg.h` enums and register bitfields, `fc->read_ibi_reg`, and valid enum values populated by bus/front-end probing.

Risks/test signals: unknown revisions leave `fc->rev` unchanged, which later SRAM setup rejects. Name-array indexing assumes trusted enum values. Test signals include mocked `misc_204` values for all revisions/capability combinations, unknown revision handling, and log output for each bus/device type used by bus drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/b2c2/flexcop-misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/b2c2/flexcop-reg.h -->
# sources/distributed-fs/ceph-client/drivers/media/common/b2c2/flexcop-reg.h

Purpose: central FlexCop register abstraction header: chip/device/bus enums, I2C/SRAM/DMA enum values, register addresses, endian-specific `flexcop_ibi_value`, and helper macro for read-modify-write bit updates.

Important APIs/types: defines `flexcop_revision_t`, `flexcop_device_type_t`, `flexcop_bus_t`, `flexcop_i2c_port_t`, `flexcop_access_op_t`, SRAM destination/target/type enums, WAN speed enum, DMA indices, and `flexcop_ibi_register`. `flexcop_set_ibi_value(reg, attr, val)` reads a register through local variable `fc`, updates one bitfield, and writes it back.

Control flow: compile-time endian selection includes either `flexcop_ibi_value_le.h` or `flexcop_ibi_value_be.h`, failing if no endian macro is defined.

State/persistence: no runtime state, but it defines the symbolic contract used to manipulate volatile device registers. `extern flexcop_ibi_value ibi_zero` is defined by `flexcop.c`.

Dependencies/integration: included via FlexCop private/common headers by core, I2C, filter, SRAM, EEPROM, frontend, USB, and PCI code.

Risks/test signals: bitfield layout correctness is critical and compiler/endianness sensitive. The macro depends on an in-scope `fc` pointer, which is terse but fragile. Build tests on little- and big-endian targets and register-level tests for representative fields are the main confidence signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/b2c2/flexcop-reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/b2c2/flexcop-sram.c -->
# sources/distributed-fs/ceph-client/drivers/media/common/b2c2/flexcop-sram.c

Purpose: configures FlexCop SRAM chip type, SRAM destination routing, WAN speed, and SRAM/DMA control flags.

Important APIs/functions: `flexcop_sram_init()` selects SRAM type by chip revision. Exported `flexcop_sram_set_dest()` routes NET/CAI/CAO/MEDIA destinations to USB/WAN, DMA1, DMA2, or FlexCopIII CA. Exported `flexcop_wan_set_speed()` and `flexcop_sram_ctrl()` update WAN speed and SRAM control bits. A large `#if 0` block preserves obsolete SRAM read/write/detect experiments and is not compiled.

Control flow: initialization maps FlexCopII/IIB to one 32 KiB chip and FlexCopIII to one 48 KiB chip. Destination programming reads `sram_dest_reg_714`, validates FlexCopIII-only target use, updates selected destination fields according to the bitmask, writes the register, then delays.

State/persistence: all state is volatile hardware register state. There is no persistent software cache aside from `fc->rev`.

Dependencies/integration: uses `flexcop-reg.h` enums/bitfields, `fc->read_ibi_reg`/`write_ibi_reg`, `ibi_zero` conventions, and exported APIs called by bus-specific streaming/DMA setup.

Risks/test signals: destination routing mistakes can silently send TS data to the wrong engine. The 1 ms `udelay` is a latency risk. Tests should cover revision validation, bitmask combinations, FC3-only target rejection on older chips, WAN speed field updates, and that dead `#if 0` code remains uncompilable/irrelevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/b2c2/flexcop-sram.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/b2c2/flexcop.c -->
# sources/distributed-fs/ceph-client/drivers/media/common/b2c2/flexcop.c

Purpose: main common FlexCop module. It wires the chip into DVB core, coordinates reset/initialization/teardown, exports demux data injection helpers, and owns the debug module parameter and global zero register value.

Important APIs/functions: exported `flexcop_device_kmalloc()`, `flexcop_device_kfree()`, `flexcop_device_initialize()`, `flexcop_device_exit()`, `flexcop_pass_dmx_data()`, `flexcop_pass_dmx_packets()`, and `flexcop_reset_block_300()`. Internal `flexcop_dvb_init()` registers `dvb_adapter`, `dvb_demux`, `dmxdev`, hardware/memory frontends, and `dvb_net`; `flexcop_dvb_exit()` unwinds them.

Control flow: initialization zeroes `ibi_zero`, resets the chip/peripherals, determines revision, initializes SRAM and filters, disables SMC, registers DVB, initializes I2C, reads/programs MAC filtering, attaches frontend, then logs completion. Any failure calls `flexcop_device_exit()`, which tears down frontend, I2C, and DVB based on init state.

State/persistence: `init_state` gates teardown; `dvb_adapter.proposed_mac` stores the runtime MAC; no durable persistence. `b2c2_flexcop_debug` is a module parameter.

Dependencies/integration: bus drivers allocate `struct flexcop_device`, fill register callbacks and bus-specific operations, then call initialize/exit. Depends heavily on Linux DVB demux/net, I2C, and frontend helper code.

Risks/test signals: partial-init unwinding, MAC-read failure path, reset timing, and missing bus callbacks are key risks. Tests should simulate failures after DVB/I2C/frontend stages, feed start/stop through demux callbacks, and verify no adapter/I2C leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/b2c2/flexcop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/b2c2/flexcop.h -->
# sources/distributed-fs/ceph-client/drivers/media/common/b2c2/flexcop.h

Purpose: private FlexCop chip-source header that sets the log prefix, includes common FlexCop declarations, and defines debug-print categories.

Important APIs/types: declares `extern int b2c2_flexcop_debug`; defines `dprintk(level, args...)` under `CONFIG_DVB_B2C2_FLEXCOP_DEBUG`; category macros include `deb_info`, `deb_tuner`, `deb_i2c`, `deb_ts`, `deb_sram`, `deb_rdump`, and `deb_i2c_dump`.

Control flow: debug logging compiles to a runtime bitmask check when debug is enabled and to `no_printk` otherwise, preserving format checking without emitting code.

State/persistence: no owned state; logging behavior depends on the module parameter defined in `flexcop.c`.

Dependencies/integration: all common FlexCop C files include this header. It depends on `flexcop-common.h` for the actual device structure, exported prototypes, and Linux media definitions.

Risks/test signals: mismatched debug bit documentation and macro definitions can make field diagnosis harder. Build tests with debug enabled and disabled are the main signal; runtime tests can verify category bits emit expected logs without affecting non-debug builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/b2c2/flexcop.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/b2c2/flexcop_ibi_value_be.h -->
# sources/distributed-fs/ceph-client/drivers/media/common/b2c2/flexcop_ibi_value_be.h

Purpose: generated big-endian layout for the `flexcop_ibi_value` union, allowing named access to every 32-bit FlexCop IBI register field.

Important APIs/types: defines `typedef union flexcop_ibi_value` with raw `u32` access and register-specific structs for DMA, I2C two-wire state, LNB/misc/control/IRQ/reset, PID filters, MAC/card IDs, CI/PI/DVB registers, SRAM buffers, destination routing, and WAN control.

Control flow: no executable logic; consumers read/write `raw` or named bitfields after `flexcop-reg.h` selects this file under `__BIG_ENDIAN`.

State/persistence: describes volatile hardware register layout only. Runtime state is the `u32 raw` value returned by bus-specific register IO.

Dependencies/integration: every FlexCop register operation in common/bus code depends on these bit positions matching hardware on big-endian builds.

Risks/test signals: C bitfield layout is implementation-sensitive and this file is explicitly generated. Any manual edit or compiler assumption mismatch corrupts register programming. Cross-endian compile coverage, comparing raw encodings for key fields against datasheet constants, and tests for I2C/control/PID/SRAM fields are critical.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/b2c2/flexcop_ibi_value_be.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/b2c2/flexcop_ibi_value_le.h -->
# sources/distributed-fs/ceph-client/drivers/media/common/b2c2/flexcop_ibi_value_le.h

Purpose: generated little-endian layout for the `flexcop_ibi_value` union, giving named bitfield access to FlexCop IBI registers on little-endian builds.

Important APIs/types: the union mirrors the big-endian file but declares fields in little-endian bit order. It covers DMA descriptors, two-wire/I2C data and status registers, revision/control/IRQ/reset fields, PID and group filters, MAC/card registers, CI/PI/DVB state, SRAM control/buffers/destinations, and WAN speed/chip configuration.

Control flow: no logic; selected by `flexcop-reg.h` when `__LITTLE_ENDIAN` is defined.

State/persistence: represents transient register snapshots and values to write; no durable state.

Dependencies/integration: heavily used by FlexCop filter, I2C, misc, SRAM, reset, EEPROM, frontend, and bus code through `fc->read_ibi_reg`/`write_ibi_reg`.

Risks/test signals: layout errors manifest as wrong hardware behavior rather than type errors. The little-endian path is likely common, so regression signals include real-device I2C transfers, revision detection, PID filtering, MAC programming, SRAM routing, and raw value assertions for representative fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/b2c2/flexcop_ibi_value_le.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/cx2341x.c -->
# sources/distributed-fs/ceph-client/drivers/media/common/cx2341x.c

Purpose: common V4L2 control and firmware-command translation code for Conexant CX23415/6/8 MPEG encoder devices.

Important APIs/functions: exports the legacy parameter API (`cx2341x_mpeg_ctrls`, `cx2341x_ctrl_query()`, `cx2341x_ctrl_get_menu()`, `cx2341x_ext_ctrls()`, `cx2341x_fill_defaults()`, `cx2341x_update()`, `cx2341x_log_status()`) and the newer control-handler API (`cx2341x_handler_init()`, `cx2341x_handler_set_50hz()`, `cx2341x_handler_setup()`, `cx2341x_handler_set_busy()`). Internal helpers map control IDs, validate menus/ranges, compute audio properties, and call firmware mailbox callbacks.

Control flow: legacy setters validate each requested `v4l2_ext_control`, enforce busy restrictions and dependent constraints, then recompute audio properties. `cx2341x_update()` compares old/new params and emits only needed mailbox commands. The handler path creates clustered V4L2 controls; `try_ctrl` normalizes dependent values, and `s_ctrl` sends corresponding firmware commands plus optional board callbacks.

State/persistence: legacy state lives in `struct cx2341x_mpeg_params`; handler state lives in `struct cx2341x_handler` and V4L2 control objects. No durable persistence.

Dependencies/integration: depends on V4L2 control/menu APIs, `media/drv-intf/cx2341x.h`, tuner/media constants, and a caller-provided mailbox function that actually talks to firmware.

Risks/test signals: dependent controls are subtle: MPEG-1 forces CBR, peak bitrate must exceed bitrate, B-frames reshape GOP, AC3 controls activate only with capability, busy controls are grabbed during encoding. Tests should cover range/menu validation, clusters, firmware command ordering, old-vs-new update diffs, 50/60 Hz GOP defaults, and callback error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/cx2341x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/cypress_firmware.c -->
# sources/distributed-fs/ceph-client/drivers/media/common/cypress_firmware.c

Purpose: downloads Intel HEX-style firmware records into Cypress AN2135/AN2235/FX2 USB controller RAM and restarts the controller CPU.

Important APIs/functions: exported `cypress_load_firmware()` is the public loader. `usb_cypress_writemem()` sends vendor request `0xa0` to write RAM/control-space bytes. `cypress_get_hexline()` parses one firmware record into `struct hexline`. Static `cypress[]` maps loader type to controller name and CPU control/status register (`0x7f92` or `0xe600`).

Control flow: loader allocates a hexline buffer, writes `1` to the CPU control register to stop execution, iterates firmware records, writes each record payload to its target address, then writes `0` to restart. Short USB writes and parse failures become errors.

State/persistence: no persistent kernel state; firmware is written into device RAM and affects device execution after restart.

Dependencies/integration: depends on Linux USB core, firmware loader, and callers passing a valid type constant from `cypress_firmware.h`.

Risks/test signals: no checksum validation is performed despite storing `chk`; type is not bounds-checked before indexing `cypress[]`; extended linear address handling assumes type `0x04`. Tests should cover malformed/truncated records, short USB writes, invalid type handling by callers, stop/start failures, and representative FX2 firmware load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/cypress_firmware.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/cypress_firmware.h -->
# sources/distributed-fs/ceph-client/drivers/media/common/cypress_firmware.h

Purpose: public declarations for the Cypress firmware downloader.

Important APIs/types: defines controller type constants `CYPRESS_AN2135`, `CYPRESS_AN2235`, and `CYPRESS_FX2`; declares `struct hexline` with record length, 32-bit address, record type, up to 255 data bytes, and checksum byte; declares `cypress_load_firmware(struct usb_device *, const struct firmware *, int)`.

Control flow: header-only contract; implementation is in `cypress_firmware.c`.

State/persistence: no state. The struct is a temporary parser container for firmware records.

Dependencies/integration: included by USB media drivers that request firmware with Linux firmware APIs and then call the loader for Cypress-based devices.

Risks/test signals: the integer type constants are used as array indices by the implementation, so callers must pass only known values. Compile coverage should ensure USB and firmware types are visible; runtime tests should pair each type with the correct CPU control register through the implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/cypress_firmware.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/saa7146/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/common/saa7146/Kconfig

Purpose: declares build-time configuration symbols for the SAA7146 common PCI/media support.

Important APIs/types: `VIDEO_SAA7146` is a hidden tristate depending on `I2C && PCI`. `VIDEO_SAA7146_VV` is a hidden tristate depending on `VIDEO_DEV`, selecting `VIDEOBUF2_DMA_SG` and the base `VIDEO_SAA7146` module.

Control flow: Kconfig dependency resolution determines whether base PCI/I2C support and optional V4L2 video/VBI support are built.

State/persistence: no runtime state; affects kernel configuration and module composition.

Dependencies/integration: selected by board drivers using SAA7146 hardware. The split lets DVB-only or non-video users depend on the base module while video/VBI users pull in VB2 DMA scatter-gather support.

Risks/test signals: incorrect dependencies cause link failures or missing symbols (`vb2_dma_sg_memops`, V4L2 ops, I2C/PCI APIs). Config tests should build base-only and video-enabled combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/saa7146/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/saa7146/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/common/saa7146/Makefile

Purpose: maps SAA7146 configuration symbols to composite kernel objects.

Important build artifacts: `saa7146.o` is built from `saa7146_i2c.o` and `saa7146_core.o`; `saa7146_vv.o` is built from `saa7146_fops.o`, `saa7146_video.o`, `saa7146_hlp.o`, and `saa7146_vbi.o`.

Control flow: `obj-$(CONFIG_VIDEO_SAA7146)` and `obj-$(CONFIG_VIDEO_SAA7146_VV)` include the base and video/VBI modules according to Kconfig.

State/persistence: no runtime state.

Dependencies/integration: mirrors the Kconfig split and keeps exported base symbols separate from optional V4L2/VB2 capture support.

Risks/test signals: object ordering matters for composite modules only at link/export level. Build tests should ensure all referenced symbols between base and VV parts resolve for both module and built-in configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/saa7146/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/saa7146/saa7146_core.c -->
# sources/distributed-fs/ceph-client/drivers/media/common/saa7146/saa7146_core.c

Purpose: base PCI driver framework for SAA7146 devices: extension registration, PCI probe/remove, IRQ dispatch, GPIO/DEBI helpers, and DMA page-table allocation/building.

Important APIs/functions: exports `saa7146_register_extension()`, `saa7146_unregister_extension()`, `saa7146_setgpio()`, DEBI wait helper, page-table helpers, vmalloc-backed page-table helpers, `saa7146_i2c_adapter_prepare`, and debug state. Internal `saa7146_init_one()` performs PCI enable, BAR mapping, IRQ registration, coherent RPS/I2C memory allocation, extension probe/attach, and drvdata setup.

Control flow: the shared interrupt handler acknowledges ISR bits, delegates extension IRQs, routes RPS0/RPS1 to VV callbacks, wakes I2C waiters, disables unhandled sources, then writes ISR ack. Remove calls extension detach, stops DMA/IRQs, frees coherent blocks, unmaps BAR, disables PCI, and frees `dev`.

State/persistence: runtime state is `struct saa7146_dev`, coherent RPS/I2C buffers, locks, wait queues, IRQ masks, and global device count/debug parameter. No durable persistence.

Dependencies/integration: extension modules supply PCI IDs, probe/attach/detach/IRQ callbacks. Base relies on Linux PCI, DMA, IRQ, I2C, V4L2 device embedding, and SAA7146 register macros.

Risks/test signals: partial-probe unwind, shared IRQ masking, I2C IRQ races, DMA mapping failures, and extension callback errors are key. Test by injecting failures at each allocation/register stage, exercising extension IRQ masks, and validating remove after failed/partial attach.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/saa7146/saa7146_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/saa7146/saa7146_fops.c -->
# sources/distributed-fs/ceph-client/drivers/media/common/saa7146/saa7146_fops.c

Purpose: common V4L2/VB2 file-operation and device-registration layer for SAA7146 video/VBI extensions, plus shared DMA queue/resource management.

Important APIs/functions: `saa7146_vv_init()` registers `v4l2_device`, creates brightness/contrast/saturation/flip controls, initializes video/VBI use-ops, and default formats. `saa7146_vv_release()` tears down VV state. `saa7146_register_device()` sets file/ioctl ops, device caps, VB2 queue properties, and registers `video_device`; `saa7146_unregister_device()` unregisters it. Buffer helpers queue, finish, advance, and timeout buffers.

Control flow: VB2 queues call into video or VBI qops; queued buffers are either activated immediately or linked. IRQ callbacks finish current buffer and activate next. Timeout marks current buffer error and advances. `fops_write()` delegates only VBI writes supported by an extension.

State/persistence: `struct saa7146_vv` holds resource bits, formats, queues, timers, sequence number, current standard/source/sync, and wait queues. State is runtime only.

Dependencies/integration: depends on SAA7146 core, V4L2 device/control/file ops, VB2 DMA-SG memory ops, extension-provided capabilities/standards/callbacks.

Risks/test signals: resource locking has a redundant first check that effectively treats already-set bits as success, so concurrent resource semantics deserve scrutiny. Test queue lifecycle, timeout handling, video vs VBI capability masks, VB2 queue init failure, and extension VBI write locking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/saa7146/saa7146_fops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/saa7146/saa7146_hlp.c -->
# sources/distributed-fs/ceph-client/drivers/media/common/saa7146/saa7146_hlp.c

Purpose: low-level SAA7146 video helper routines for HPS scaling, output format programming, DMA register programming, capture engine RPS programs, clipping disable, and source/sync selection.

Important APIs/functions: exported `saa7146_set_hps_source_and_sync()` and `saa7146_write_out_dma()`. `saa7146_set_capture()` is the main capture-programming entry used by video buffer activation. Internal scaling helpers calculate horizontal/vertical scaler registers from input/output dimensions, field mode, and flips; DMA helpers program packed and planar formats.

Control flow: capture activation recalculates HPS window and output format, disables clipping, toggles alternate field state, writes DMA descriptors for packed or planar formats, builds an RPS0 program that waits for field boundaries, enables DMAs, stops them, interrupts, then starts RPS0.

State/persistence: hardware register state is updated on each capture. `vv->last_field`, `current_hps_source`, `current_hps_sync`, `hflip`, and `vflip` influence programming. No durable persistence.

Dependencies/integration: used by `saa7146_video.c` buffer activation. Depends on SAA7146 register constants, RPS macros, format metadata, VB2-built page tables, and extension-selected TV standard geometry.

Risks/test signals: scaling math rejects vertical zoom but mostly ignores return values; DMA offsets for planar/user buffers have FIXME notes; flips and alternate fields are fragile. Test signals include format/field matrix captures, planar 4:2:0/4:2:2 offsets, hflip/vflip boundaries, NTSC/PAL standard sizes, and RPS interrupt completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/saa7146/saa7146_hlp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/saa7146/saa7146_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/media/common/saa7146/saa7146_i2c.c

Purpose: implements the SAA7146 I2C master algorithm and adapter preparation for extension drivers.

Important APIs/functions: `saa7146_i2c_adapter_prepare()` enables pins, records bitrate, resets the controller, and fills `struct i2c_adapter`. Internal `saa7146_i2c_msg_prepare()` packs I2C messages into SAA7146 transfer dwords, `saa7146_i2c_writeout()` executes one dword via IRQ or polling, `saa7146_i2c_transfer()` handles retries/reset/cleanup, and `saa7146_i2c_xfer()` is the algorithm callback.

Control flow: transfer serializes on `dev->i2c_lock`, prepares packed operations, resets error/busy state, writes each dword, retries failed transactions unless IRQ-mode address errors should abort, then unpacks received bytes back into message buffers. Revision 0 gets an extra reset/zero write workaround.

State/persistence: state is runtime hardware status plus `dev->i2c_bitrate`, `dev->i2c_op`, wait queue, extension flags, and coherent `d_i2c` command buffer.

Dependencies/integration: integrates with Linux I2C core and SAA7146 core IRQ handler, which wakes `i2c_wq` on MASK_16/17.

Risks/test signals: packing supports only `SAA7146_I2C_MEM` bytes; cleanup writes bytes for all messages, not only reads; IRQ/poll paths have different address-error behavior. Tests should cover SMBus capability reporting, oversized messages, interrupted waits, poll timeout, IRQ completion, retries, and revision-0 workaround.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/saa7146/saa7146_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/saa7146/saa7146_vbi.c -->
# sources/distributed-fs/ceph-client/drivers/media/common/saa7146/saa7146_vbi.c

Purpose: VBI capture support for the SAA7146 VV module, using DMA3/BRS and RPS1 programs.

Important APIs/functions: exports `saa7146_vbi_uops` with `init` and `irq_done`. Internal `vbi_begin()` claims `RESOURCE_DMA3_BRS`, tunes arbitration, initializes BRS, and may run `vbi_workaround()`. `saa7146_set_vbi_capture()` programs DMA3 and an RPS1 capture sequence. VB2 qops allocate/build/free page tables and handle streaming.

Control flow: start streaming resets sequence if needed and calls `vbi_begin()`. Queued buffers activate DMA3/RPS1 and set a timeout. IRQ completion marks current buffer done and advances; stop disables RPS1 IRQs/DMA3, deletes timers, returns queued buffers, and frees the resource.

State/persistence: VBI state lives in `vv->vbi_dmaq`, `vv->vbi_read_timeout`, `vv->vbi_wq`, resource bits, and BRS/DMA registers. No durable persistence.

Dependencies/integration: uses SAA7146 core registers, `saa7146_write_out_dma()`, shared buffer helpers, VB2 DMA-SG page tables, extension flags such as `SAA7146_USE_PORT_B_FOR_VBI`, and VV IRQ dispatch.

Risks/test signals: `vbi_workaround()` sleeps waiting for IRQ and is signal-sensitive; some constants are PAL-specific; stop has a `return_buffers()` call before resource free in source order that makes the following free unreachable. Tests should cover port A/B paths, signal interruption, timeout, stop cleanup/resource release, and 16-line buffer sizing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/saa7146/saa7146_vbi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/saa7146/saa7146_video.c -->
# sources/distributed-fs/ceph-client/drivers/media/common/saa7146/saa7146_video.c

Purpose: V4L2 video capture implementation for SAA7146 VV devices: format enumeration, standard/format ioctls, controls, VB2 queue ops, page-table construction, and video IRQ completion.

Important APIs/functions: exports `saa7146_video_ioctl_ops`, `saa7146_vbi_ioctl_ops`, `video_qops`, `saa7146_video_uops`, `saa7146_format_by_fourcc()`, and `saa7146_s_ctrl()`. Supports packed RGB/greyscale/UYVY and planar YUV422/YUV420/YVU420 formats.

Control flow: format try clamps dimensions to current TV standard and field type, computes bytesperline/sizeimage, and rejects unknown fourcc. Setting format/standard is blocked while video or VBI queues are busy. Streaming claims DMA/HPS resources, enables RPS0 IRQs, activates queued buffers via `saa7146_set_capture()`, then IRQs finish buffers and advance the queue. Stop disables engine and returns buffers with error.

State/persistence: updates runtime `vv->video_fmt`, `vv->standard`, `last_field`, flips, queue state, and sequence counter. No persistent storage.

Dependencies/integration: depends on helper capture programming in `saa7146_hlp.c`, page-table helpers from core, VB2 DMA-SG, extension standards/callbacks/capabilities, and V4L2 event/control helpers.

Risks/test signals: planar page-table offsets for user buffers have FIXME notes; control changes for flips are blocked only when video queue busy; resource release depends on streaming lifecycle. Tests should cover every format/field, busy `S_FMT`/`S_STD`, planar buffer mapping, start failure returning buffers, IRQ sequencing, and control register writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/saa7146/saa7146_video.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/siano/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/common/siano/Kconfig

Purpose: declares common Siano mobile DTV driver configuration symbols.

Important APIs/types: `SMS_SIANO_MDTV` builds common Siano support when DVB core, DMA, and either USB or SDIO transport are present. `SMS_SIANO_RC` enables remote-controller support with RC core and media common options. `SMS_SIANO_DEBUGFS` enables smsdvb debugfs statistics, constrained to debugfs and matching USB/SDIO configuration.

Control flow: Kconfig dependency resolution selects common core, optional IR, and optional debugfs objects through the Makefile.

State/persistence: no runtime state; controls build composition.

Dependencies/integration: integrates Siano common code with transport drivers (`SMS_USB_DRV`/`SMS_SDIO_DRV`), DVB core, RC core, and debugfs.

Risks/test signals: dependency expressions can make optional features unavailable or built with missing transport support. Build matrix tests should cover USB-only, SDIO-only, RC enabled/disabled, and debugfs enabled constraints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/siano/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/siano/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/common/siano/Makefile

Purpose: defines Siano common and DVB adaptation composite objects.

Important build artifacts: `smsmdtv.o` includes `smscoreapi.o`, `sms-cards.o`, and `smsendian.o`; `smsdvb.o` includes `smsdvb-main.o`. `smsir.o` is appended when `CONFIG_SMS_SIANO_RC=y`; `smsdvb-debugfs.o` is appended when `CONFIG_SMS_SIANO_DEBUGFS=y`.

Control flow: `obj-$(CONFIG_SMS_SIANO_MDTV)` builds both common core and DVB adaptation modules. Conditional blocks add optional IR/debugfs sources.

State/persistence: no runtime state.

Dependencies/integration: mirrors Siano Kconfig and keeps board metadata in the common core while DVB frontend registration lives in `smsdvb`.

Risks/test signals: optional object combinations must match preprocessor stubs in headers. Build tests should cover RC/debugfs permutations and module/built-in linkage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/siano/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/siano/sms-cards.c -->
# sources/distributed-fs/ceph-client/drivers/media/common/siano/sms-cards.c

Purpose: board database and board-specific GPIO/power/LED/LNA behavior for Siano SMS1xxx devices.

Important APIs/functions: exported `sms_get_board()` returns static board metadata; `sms_board_setup()` applies initial GPIO states; `sms_board_power()` handles power-state GPIO effects; `sms_board_led_feedback()` updates LEDs while caching LED state via core API; `sms_board_lna_control()` toggles LNA/RF switch GPIOs; `sms_board_load_modules()` requests `smsdvb`; `sms_board_event()` is a currently mostly-empty event hook.

Control flow: board IDs index `sms_boards[]`, whose entries define name, device type, firmware per mode, default mode, interface number, MTU, crystal, remote map, LED/LNA/RF GPIOs, and GPIO config fields. GPIO helper handles negative pin numbers as inverted GPIOs.

State/persistence: static board table is read-only metadata; LED state is stored via `smscore_led_state()`; actual state is hardware GPIO level. No durable persistence.

Dependencies/integration: depends on `smscoreapi` for board IDs/GPIO operations and on `smsir`/RC maps for IR metadata. Called by Siano USB/SDIO/core/DVB code during hotplug, mode setup, tuning, and feedback.

Risks/test signals: `sms_get_board()` uses `BUG_ON` for invalid IDs, making caller validation critical. Some board fields are `-1`/0 sentinel pins. Tests should cover every board ID, inverted GPIO behavior, LNA unsupported returns, LED duplicate suppression, firmware name selection, and module auto-load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/siano/sms-cards.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/siano/sms-cards.h -->
# sources/distributed-fs/ceph-client/drivers/media/common/siano/sms-cards.h

Purpose: board IDs, board metadata structures, board event enum, LED constants, and board-helper prototypes for Siano SMS1xxx devices.

Important APIs/types: defines board ID constants `SMS_BOARD_UNKNOWN` through `SMS1XXX_BOARD_PCTV_77E`; `struct sms_board_gpio_cfg` names many optional GPIO roles; `struct sms_board` stores device type, name, firmware names by mode, GPIO config, RC map, legacy GPIO shortcuts, interface number, default mode, MTU, crystal, and antenna config. Declares board lookup/setup/power/LED/LNA/module-load helpers.

Control flow: header-only declarations; implementation switches on board IDs in `sms-cards.c`.

State/persistence: no state, except `extern struct smscore_device_t *coredev` declaration from surrounding Siano code.

Dependencies/integration: includes `smscoreapi.h`, Linux USB declarations, and `smsir.h`; consumed by Siano core, USB/SDIO, IR, and DVB adaptation code.

Risks/test signals: numeric board IDs are ABI-like within driver tables and transport ID mappings, so reordering is risky. Tests/build checks should ensure array entries exist for all constants, event enum users handle defaults, and optional fields have clear sentinel semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/siano/sms-cards.h -->
