# Research: subset-b-004113

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23885-core.c -->
## sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23885-core.c

Purpose: PCI core for the Conexant CX23885/CX23887/CX23888 media bridge. It owns PCI probe/remove, MMIO mapping, board detection, bridge reset, SRAM channel setup, common RISC DMA program creation, interrupt demux, GPIO helpers, and registration handoff to analog video, DVB transport, MPEG encoder, audio, I2C, and IR submodules.

Important APIs/types/functions: module parameters `card`, `debug`, `disable_analog_video`, and `dma_reset_workaround` influence probe behavior. `cx23885_initdev()` is the PCI probe entry and `cx23885_finidev()` is remove. `cx23885_dev_setup()` builds `struct cx23885_dev`, selects the SRAM layout table, registers I2C buses, calls card setup, and conditionally registers analog, DVB, and encoder ports. DMA helpers include `cx23885_sram_channel_setup()`, `cx23885_risc_buffer()`, `cx23885_risc_databuffer()`, `cx23885_risc_vbibuffer()`, `cx23885_start_dma()`, `cx23885_buf_prepare()`, `cx23885_buf_queue()`, `cx23885_cancel_buffers()`, and `cx23885_free_buffer()`. IRQ helpers include `cx23885_irq_add_enable()`, `cx23885_irq_disable()`, `cx23885_irq_ts()`, `cx23885_irq_417()`, and the top-level `cx23885_irq()`.

Control flow: PCI probe allocates device state, registers V4L2 device/control state, enables PCI, maps BAR0, detects board and bridge revision, configures I2C master register blocks, initializes TS ports according to board port roles, resets hardware, registers subdevices, and then registers the relevant frontends. Runtime streaming programs an SRAM channel to point at a vb2 buffer RISC program, chains later buffers by patching the previous buffer jump target, and completes buffers from RISCI interrupts. The top IRQ handler reads PCI, video, audio, TS, GPIO/CI, AV-core, and IR status, dispatches to the matching subsystem, then acknowledges handled PCI bits.

State and persistence: all state is volatile in `struct cx23885_dev`, `struct cx23885_tsport`, vb2 queues, DMA queue lists, RISC coherent allocations, interrupt masks, and hardware registers. There is no on-disk persistence. Persistent-like configuration comes only from module parameters and static board tables in other cx23885 files.

Dependencies/integration: Linux PCI, DMA, interrupts, V4L2 device/subdev, vb2 DMA-SG, DVB helpers, I2C, firmware-capable subdrivers, `cx23885-cards`, `cx23885-video`, `cx23885-dvb`, `cx23885-417`, `cx23885-alsa`, `cx23885-av`, NetUP/Altera CI, and IR helpers. Register access relies on `cx23885-reg.h` macros and the `cx_read/cx_write` wrappers from `cx23885.h`.

Risks: RISC program sizing and scatterlist traversal are low-level and protected mainly by `BUG_ON`; malformed queue state can affect DMA. Interrupt mask state is split between `dev->pci_irqmask` and hardware. GPIO helpers intentionally warn but still access MC417 ranges that may collide with encoder host bus use. DMA reset workaround is platform heuristic based on unrelated PCI IDs. Probe has many partial-registration paths, so cleanup ordering is important.

Test signals: successful PCI bind logs with board, bridge, revision, IRQ and MMIO; three I2C adapters registered; analog/DVB/encoder devices appear according to board table; streaming produces monotonically sequenced vb2 buffers; no RISC opcode/fifo/sync errors under sustained capture; suspend/resume resets hardware; remove unloads without IRQ-after-free or DMA leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23885-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23885-dvb.c -->
## sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23885-dvb.c

Purpose: DVB/ATSC transport registration and board-specific frontend attachment for cx23885 TS ports. It configures vb2 capture queues for MPEG transport packets, attaches demodulators/tuners/SEC/CI devices for many supported boards, and registers the resulting DVB adapter bus.

Important APIs/types/functions: `cx23885_dvb_register()` allocates one or more `vb2_dvb_frontend` objects per TS port and initializes `dvbq`. `dvb_register()` is the large board switch that attaches frontends through `dvb_attach()` or I2C client instantiation. `cx23885_dvb_unregister()` tears down DVB bus and auxiliary I2C clients. Queue callbacks `queue_setup()`, `buffer_prepare()`, `buffer_queue()`, `cx23885_start_streaming()`, and `cx23885_stop_streaming()` bridge DVB streaming to common TS DMA helpers. Board hooks include `cx23885_dvb_gate_ctrl()`, `cx23885_dvb_set_frontend()`, `cx23885_set_frontend_hook()`, `f300_set_voltage`, DVBSky voltage wrappers, `cx23885_sp2_ci_ctrl()`, `netup_altera_fpga_rw()`, and `dvb_register_ci_mac()`.

Control flow: core setup calls `cx23885_dvb_register()` for a board port marked `CX23885_MPEG_DVB`. Each frontend gets a vb2 DMA-SG queue sized for 32 buffers of 32 188*4-byte TS rows. After queue init, `dvb_register()` selects the right I2C bus, demod config, tuner config, optional SEC controller, optional CI controller, and MAC extraction path. Streaming starts by using the first queued buffer to start `cx23885_start_dma()` on the TS port; interrupts later complete queued buffers through the core TS IRQ path.

State and persistence: state lives in `port->frontends`, `port->mpegq`, `port->gate_ctrl`, callback shadows such as `port->set_frontend` and `port->fe_set_voltage`, and optional `i2c_client_*` pointers for demod/tuner/SEC/CI. MAC addresses are read from EEPROM into DVB adapter state but not persisted by this driver.

Dependencies/integration: uses vb2-dvb, DVB frontend APIs, many demod/tuner drivers, I2C client model, `request_module()`, V4L2 tuner callbacks, NetUP and Altera CI helpers, SP2 CI, `tveeprom`, cx23885 GPIO helpers, and the common TS DMA path in `cx23885-core.c`.

Risks: the board switch is broad and hardware-specific, so regressions are often per-board. Some I2C client failure paths depend on driver binding and module refcounts. Multi-frontend gate selection is minimally documented. Several boards share tuners with analog through `dev->ts1.analog_fe`, so attach order matters. GPIO voltage and CI control paths touch shared MC417/GPIO registers.

Test signals: DVB adapter/frontend nodes appear for each configured port; frontend lock for each board delivery system; TS streaming without RISC/fifo errors; correct EEPROM MAC in logs; CI slot detection and CAM access where present; module unload releases demod/tuner/SEC/CI clients; analog tuner sharing still works on hybrid boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23885-dvb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23885-f300.c -->
## sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23885-f300.c

Purpose: Bit-banged control driver for a Silicon Labs C8051F300 microcontroller used for LNB voltage control on TeVii S470 and TBS 6920 style DVB-S/S2 cards.

Important APIs/types/functions: `f300_set_voltage()` is the exported frontend `set_voltage` callback. Internal helpers `f300_set_line()`, `f300_get_line()`, `f300_send_byte()`, `f300_get_byte()`, and `f300_xfer()` implement a custom GPIO serial protocol over `GPIO_0` data, `GPIO_1` reset, `GPIO_2` clock, and `GPIO_3` busy.

Control flow: `f300_set_voltage()` builds a small command packet selecting LNB power off, 13 V, or 18 V, then calls `f300_xfer()`. Transfer computes a checksum, drives reset/clock/data idle states, sends write address `0xe0`, shifts out the command bytes MSB-first with microsecond delays, releases reset, waits up to roughly 8 ms for busy to drop, then reads and discards the microcontroller response through address `0xe1`.

State and persistence: no private persistent state. Hardware state is the GPIO direction/value configuration and the microcontroller's LNB output state.

Dependencies/integration: depends on `cx23885_gpio_enable()`, `cx23885_gpio_set()`, `cx23885_gpio_clear()`, `cx23885_gpio_get()`, Linux delay helpers, and DVB SEC voltage enums. It is installed by `cx23885-dvb.c` by assigning `frontend->ops.set_voltage`.

Risks: timing is fixed and undocumented; no locking protects the GPIO protocol from other GPIO users; response bytes are discarded, so checksum/status failures are not validated; unsupported voltage enum values leave packet fields uninitialized except through current caller behavior.

Test signals: satellite frontend can switch SEC_VOLTAGE_13/OFF/18 and drive LNB hardware; busy timeout message is absent; no GPIO conflicts with other board functions; DiSEqC/tuning continues after repeated voltage changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23885-f300.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23885-f300.h -->
## sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23885-f300.h

Purpose: Minimal public declaration for the F300 LNB voltage helper.

Important APIs/types/functions: declares `f300_set_voltage(struct dvb_frontend *fe, enum fe_sec_voltage voltage)`, matching the DVB frontend SEC voltage callback signature.

Control flow: cx23885 DVB board attach code includes this header and assigns the function into `fe->ops.set_voltage` for boards using the C8051F300 microcontroller.

State and persistence: no state is defined. All runtime state is in the frontend's `dvb->priv` TS port and the GPIO-backed hardware.

Dependencies/integration: requires the including translation unit to have DVB frontend type declarations available, normally through `cx23885.h` and DVB headers.

Risks: intentionally no include guard and no direct includes; it relies on include order. Any signature drift from DVB frontend ops would break compile coverage in users.

Test signals: compile of `cx23885-dvb.c` and successful voltage switching on F300-backed boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23885-f300.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23885-i2c.c -->
## sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23885-i2c.c

Purpose: Hardware I2C adapter implementation for the three cx23885 bridge I2C masters. It exposes Linux I2C adapters used by board setup, demods, tuners, EEPROM, AV core, and IR devices.

Important APIs/types/functions: `cx23885_i2c_register()` and `cx23885_i2c_unregister()` add/remove adapters. The `i2c_algorithm` uses `i2c_xfer()` and `cx23885_functionality()`. Low-level helpers `i2c_sendbytes()`, `i2c_readbytes()`, `i2c_wait_done()`, `i2c_is_busy()`, and `i2c_slave_did_ack()` program per-bus address, data, control, and status registers. `cx23885_av_clk()` writes an AV-core clock register through bus 2.

Control flow: core fills `struct cx23885_i2c` register offsets and timing periods, then calls register for each bus. I2C transfers poll the busy bit with 64 retries of 32 us, support zero-length probe messages, ordinary writes, reads, and joined write-then-read messages by using `I2C_NOSTOP` and `I2C_EXTEND`. Optional `i2c_scan` probes all 7-bit addresses. Registration also scans address `0x6b` for an `ir_video` client.

State and persistence: state is in each `struct cx23885_i2c`: adapter, synthetic client, register offsets, last result code, and timing period. Hardware controller state is volatile.

Dependencies/integration: Linux I2C core, V4L2 device adapter data, MMIO access macros, delay helpers, optional module parameters, and cx23885 core bus initialization.

Risks: transfer completion is polling-only and returns generic `-EIO` on timeout; ACK checking is only used for zero-length probes; debug logging interleaves multi-byte output; `cx23885_av_clk()` uses `I2C_M_TEN` while addressing a fixed device-specific register path; no explicit bus lock beyond I2C core serialization.

Test signals: three adapters are visible; tuner/demod/EEPROM subdevices attach; `i2c_scan=1` shows expected devices; combined register reads work; no I2C timeout logs during tune, video mux, or IR probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23885-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23885-input.c -->
## sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23885-input.c

Purpose: rc-core input integration for boards whose IR receiver is represented as a V4L2 IR subdevice. It translates raw IR measurements into Linux remote-control events and manages open/close power state.

Important APIs/types/functions: `cx23885_input_init()` creates and registers `struct rc_dev`, selecting protocol mask and keymap by board. `cx23885_input_fini()` stops hardware and unregisters the RC device. `cx23885_input_rx_work_handler()` processes IR notifications. Internal helpers `cx23885_input_process_measurements()`, `cx23885_input_ir_start()`, `cx23885_input_ir_stop()`, `cx23885_input_ir_open()`, and `cx23885_input_ir_close()` configure and drain the IR subdevice.

Control flow: after the core installs IRQ handling and initializes IR subdevices, it calls input init. Supported boards allocate `cx23885_kernel_ir`, create names/physical path, set rc-core IDs, and register raw IR decoding. On rc open, board-specific receiver parameters are sent via `rx_s_parameters`. Notification work reads arrays of `struct ir_raw_event` from `sd_ir` until empty, stores them to rc-core, handles overflow, and restarts hardware after FIFO overrun. Close and fini set a shutdown flag, disable interrupts, and flush related work.

State and persistence: state is volatile in `dev->kernel_ir`, `rc_dev`, allocated name strings, `dev->ir_input_stopping`, and IR subdevice parameters. No persistent keymap storage is written by this file.

Dependencies/integration: rc-core, V4L2 subdev IR ops, workqueues initialized in core/IR files, board IDs and keymap constants. It depends on `dev->sd_ir` already being populated by card/IR setup.

Risks: only explicitly listed boards are enabled; overrun recovery races are mitigated but still depend on subdevice honoring `shutdown`; `cx23885_input_fini()` calls stop even when no IR exists; keymap assignments for some boards are documented guesses.

Test signals: `/sys/class/rc/rc*` device appears with expected keymap; opening the rc device starts receiver; `ir-keytable -t` sees raw events; FIFO overrun recovers without repeated interrupts; unload during open/close does not leave scheduled work or freed `kernel_ir` access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23885-input.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23885-input.h -->
## sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23885-input.h

Purpose: Internal header for cx23885 IR input support.

Important APIs/types/functions: declares `cx23885_input_rx_work_handler()`, `cx23885_input_init()`, and `cx23885_input_fini()`.

Control flow: the core and IR notification files include this header to register the rc-core device at probe, pass RX events from workqueue context, and tear down input state at remove.

State and persistence: no state is defined in the header. It exposes functions that operate on `struct cx23885_dev`.

Dependencies/integration: guarded by `_CX23885_INPUT_H_`; assumes `struct cx23885_dev` and `u32` are declared by the including context, usually `cx23885.h`.

Risks: narrow internal ABI, so include order matters. Missing this header would not affect external kernel APIs but would break coordination between core, IR, and input code.

Test signals: compile coverage and successful IR init/fini paths on supported boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23885-input.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23885-ioctl.c -->
## sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23885-ioctl.c

Purpose: Optional V4L2 advanced-debug ioctl helpers for reading and writing cx23885 bridge registers and, when present, CX23417 encoder registers.

Important APIs/types/functions: under `CONFIG_VIDEO_ADV_DEBUG`, exports `cx23885_g_chip_info()`, `cx23885_g_register()`, and `cx23885_s_register()`. Internal helpers `cx23417_g_register()` and `cx23417_s_register()` use MC417 register accessors for encoder chip debug access.

Control flow: video ioctl ops call these helpers for `VIDIOC_DBG_G_CHIP_INFO`, `VIDIOC_DBG_G_REGISTER`, and `VIDIOC_DBG_S_REGISTER`. `match.addr == 0` targets the bridge MMIO register space; `match.addr == 1` targets the CX23417 if `dev->v4l_device` is present. Access is rejected for unsupported chip addresses, unaligned offsets, or offsets outside the BAR/encoder debug range.

State and persistence: no driver state is owned here. Writes mutate live hardware registers and can affect active capture, but nothing is persisted.

Dependencies/integration: V4L2 advanced debug API, `video_drvdata()`, PCI BAR size, `cx_read/cx_write`, and cx23417 MC417 register accessors from the encoder support code.

Risks: debug register writes are powerful and can destabilize live hardware; MC417 read/write failures are mapped to `-EINVAL` by V4L2 convention; no serialization beyond higher-level ioctl locking is added here.

Test signals: with `CONFIG_VIDEO_ADV_DEBUG`, `v4l2-dbg` can identify bridge/encoder chips, read aligned bridge registers, reject invalid offsets, and access encoder registers only on encoder-backed boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23885-ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23885-ioctl.h -->
## sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23885-ioctl.h

Purpose: Internal declarations for cx23885 V4L2 advanced-debug ioctl helpers.

Important APIs/types/functions: always declares `cx23885_g_chip_info()`, and conditionally declares `cx23885_g_register()` and `cx23885_s_register()` when `CONFIG_VIDEO_ADV_DEBUG` is enabled.

Control flow: `cx23885-video.c` includes this header and wires these helpers into `v4l2_ioctl_ops` under the same config guard.

State and persistence: no state.

Dependencies/integration: protected by `_CX23885_IOCTL_H_`; relies on V4L2 debug structs and `struct file` from included kernel/V4L2 headers.

Risks: `cx23885_g_chip_info()` is declared unconditionally while its implementation is inside the C file's `CONFIG_VIDEO_ADV_DEBUG` block; current use is also config guarded, so this is compile-safe as long as callers keep the same guard.

Test signals: builds with and without `CONFIG_VIDEO_ADV_DEBUG`; debug ioctls appear only in the enabled configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23885-ioctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23885-ir.c -->
## sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23885-ir.c

Purpose: Non-input IR notification bridge. It collects V4L2 subdevice IR RX/TX notifications, stores them as bit flags, and runs work handlers that forward RX events to the rc-core input layer.

Important APIs/types/functions: `cx23885_ir_rx_v4l2_dev_notify()` and `cx23885_ir_tx_v4l2_dev_notify()` are called from the V4L2 device notify hook, possibly in IRQ context. `cx23885_ir_rx_work_handler()` converts pending notification bits into V4L2 IR event masks and calls `cx23885_input_rx_work_handler()`. `cx23885_ir_tx_work_handler()` currently drains TX service notifications without further action.

Control flow: the core notify callback receives `V4L2_SUBDEV_IR_RX_NOTIFY` or TX notify from `sd_ir`. This file sets internal bits using `set_bit()`. If the notifier is the AV core subdevice it runs the work handler directly because it is already in workqueue context; otherwise it schedules work for IRQ-safe deferral. RX work clears bits, forms event flags, and passes them to input handling only if `dev->kernel_ir` exists.

State and persistence: state is in `dev->ir_rx_notifications`, `dev->ir_tx_notifications`, and the two work_structs initialized by core. No persistence.

Dependencies/integration: V4L2 subdevice notifications, workqueues, bitops, `cx23885-input.c`, and core `cx23885_v4l2_dev_notify()`.

Risks: TX notifications are acknowledged but effectively ignored. Multiple events coalesce into bits, so repeated identical notifications before work runs are compressed. Direct handler invocation for `sd_cx25840` assumes notify context is safe for the downstream RX processing.

Test signals: IR RX interrupts schedule work and produce rc-core events; overrun bits reach input handler; no work remains active during input/core teardown; TX service requests do not spin.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23885-ir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23885-ir.h -->
## sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23885-ir.h

Purpose: Internal header for cx23885 IR notification work functions.

Important APIs/types/functions: declares RX/TX V4L2 notify entry points and RX/TX work handlers: `cx23885_ir_rx_v4l2_dev_notify()`, `cx23885_ir_tx_v4l2_dev_notify()`, `cx23885_ir_rx_work_handler()`, and `cx23885_ir_tx_work_handler()`.

Control flow: included by core for work initialization and notify dispatch, and by IR implementation for shared prototypes.

State and persistence: no state.

Dependencies/integration: guarded by `_CX23885_IR_H_`; relies on V4L2 subdev and workqueue type declarations from including code.

Risks: narrow internal ABI. Any signature change must be coordinated with core notify setup and work initialization.

Test signals: compile coverage and functioning IR notification path on CX2388x IR boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23885-ir.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23885-reg.h -->
## sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23885-reg.h

Purpose: Register map and bit definitions for the cx23885 family bridge, including RISC opcodes, PCI interrupt bits, AV core, IR, DMA, GPIO, video, audio, I2C, and UART register offsets.

Important APIs/types/functions: defines RISC instruction words such as `RISC_WRITE`, `RISC_JUMP`, `RISC_SYNC`, and IRQ/count flags used by DMA program builders. Defines interrupt masks like `PCI_MSK_*`, `VID_BC_MSK_*`, video/audio interrupt registers, `TC_REQ` workaround registers, SRAM DMA pointer/count registers, GPIO/MC417 registers, `PAD_CTRL`, `CLK_DELAY`, video A/B/C DMA controls, audio controls, and I2C bus register blocks.

Control flow: no executable flow. All cx23885 C files consume these constants through `cx_read()`, `cx_write()`, `cx_set()`, and `cx_clear()` to program hardware. The core SRAM setup uses DMA pointer/count offsets; video/VBI/DVB use DMA and interrupt masks; I2C uses bus register sets; IR/input use IR register offsets through subdevice setup code.

State and persistence: no state. The constants define volatile hardware state locations.

Dependencies/integration: included from `cx23885.h`, which then exposes register access helpers to all cx23885 modules.

Risks: offset or bit errors directly cause hardware misprogramming. Some aliases/duplicates exist for VID_B masks, so edits can accidentally diverge definitions. Comments document hardware behavior, not enforced invariants.

Test signals: broad compile coverage; successful capture/tune/audio/I2C/IR operation; register dumps matching expected channels; absence of DMA stalls, bad packet, opcode, sync, and overflow errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23885-reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23885-vbi.c -->
## sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23885-vbi.c

Purpose: VBI capture support for analog video on Video A. It reports sliced raw VBI format parameters, builds vb2 buffers backed by cx23885 RISC DMA programs, starts/stops VBI DMA, and handles VBI RISCI interrupts.

Important APIs/types/functions: exported `cx23885_vbi_fmt()` fills V4L2 VBI format, `cx23885_vbi_irq()` completes buffers from VBI interrupts, and `cx23885_vbi_qops` provides vb2 queue callbacks. Internal helpers include `cx23885_start_vbi_dma()`, `queue_setup()`, `buffer_prepare()`, `buffer_finish()`, `buffer_queue()`, `cx23885_start_streaming()`, and `cx23885_stop_streaming()`.

Control flow: V4L2 video registration attaches this queue to the VBI video device. Queue setup sizes one plane for both fields, using 12 NTSC lines or 18 PAL lines of 1440 samples per line. Buffer prepare creates a two-field RISC program via `cx23885_risc_vbibuffer()`. Queued buffers are chained by patching RISC jumps. Starting streaming programs SRAM channel 2, resets VBI counters, enables video-A VBI interrupts, enables RISC, and starts `VID_A_DMA_CTL` bits `0x22`. Stop clears those bits and returns active buffers with error.

State and persistence: state is in `dev->vbiq`, `dev->vb2_vbiq`, per-buffer RISC allocations, `dev->tvnorm`, hardware counters, and video-A interrupt masks. No persistence.

Dependencies/integration: V4L2/vb2 DMA-SG, common RISC helpers from core, `cx23885-video.c` IRQ dispatch, and `cx23885-reg.h` video-A/VBI registers.

Risks: shares `VID_A_DMA_CTL` and interrupt status with normal video capture, so concurrent video/VBI handling depends on correct masks and queue locking. The file has a `vbibufs` module parameter that is not used by queue setup. Field line offsets are hardcoded around NTSC/PAL assumptions.

Test signals: `/dev/vbi*` registration; VBI format reports expected line counts for 525/60 and 625/50 norms; streaming yields correctly sized buffers; simultaneous video and VBI capture complete independently; stop/unload returns buffers and disables DMA without warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23885-vbi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23885-video.c -->
## sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23885-video.c

Purpose: Analog V4L2 video/VBI device implementation for cx23885 Video A. It provides format negotiation, input/audio/tuner ioctls, buffer queueing, RISC DMA startup, interrupt completion, analog tuner sharing, and video/VBI/audio registration.

Important APIs/types/functions: exported functions include `cx23885_video_register()`, `cx23885_video_unregister()`, `cx23885_video_irq()`, `cx23885_video_wakeup()`, `cx23885_set_tvnorm()`, `cx23885_enum_input()`, `cx23885_get_input()`, `cx23885_set_input()`, `cx23885_set_frequency()`, `cx23885_flatiron_write()`, and `cx23885_flatiron_read()`. Internal vb2 callbacks build packed YUYV RISC buffers. V4L2 ioctl ops cover querycap, format, VBI format, std, input, audio input, tuner, frequency, events, and optional advanced-debug register access.

Control flow: registration initializes default NTSC YUYV 720-wide interlaced state, optionally creates analog tuner subdevices, programs norm/input/audio mux, initializes video and VBI vb2 queues, registers `/dev/video*` and `/dev/vbi*`, then registers ALSA audio. Streaming prepares a field-aware RISC buffer, chains buffers in `dev->vidq`, programs SRAM channel 1 and video-A DMA, and completes buffers on RISCI1. Input ioctls route video through the cx25840 subdevice, apply board GPIO quirks, and route audio through cx25840 and optional Flatiron ADC mux. Frequency ioctls either use V4L2 tuner subdev calls or DVB tuner ops via `analog_fe` on hybrid boards.

State and persistence: volatile state in `dev->tvnorm`, `fmt`, width/height/field, input, audinput, frequency, video/VBI queues, per-buffer RISC memory, registered `video_device` pointers, analog tuner subdevs, and audio device pointer. No on-disk persistence.

Dependencies/integration: V4L2 core/ioctls/events, vb2 DMA-SG, tuner and cx25840 subdev APIs, Flatiron I2C on internal bus, common RISC and IRQ helpers, `cx23885-vbi.c`, `cx23885-ioctl.c`, `cx23885-alsa.c`, board tables, and DVB-attached analog tuner sharing.

Risks: only YUYV is supported; format/norm changes are rejected while any video/VBI/MPEG queue is busy. Video and VBI share Video A DMA/interrupt registers. Hybrid-board analog frequency setup depends on DVB attachment populating `analog_fe`. Flatiron I2C reads/writes mostly log but do not propagate errors. Field order has board-specific `force_bff` behavior.

Test signals: video and VBI nodes register with correct caps; `v4l2-ctl --stream-mmap` captures stable YUYV; standard/input/audio/frequency ioctls update subdevices; tuner-capable hybrid boards tune analog via shared tuner; IRQ logs show no opcode/sync/fifo errors; unregister removes video, VBI, and ALSA devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23885-video.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23885-video.h -->
## sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23885-video.h

Purpose: Small internal header exposing Flatiron audio ADC register helpers used outside `cx23885-video.c`.

Important APIs/types/functions: declares `cx23885_flatiron_write(struct cx23885_dev *dev, u8 reg, u8 data)` and `cx23885_flatiron_read(struct cx23885_dev *dev, u8 reg)`.

Control flow: video code implements these helpers for I2C access to the Flatiron device at address `0x98 >> 1`; other cx23885 modules can include this header if they need direct Flatiron access.

State and persistence: no state. The helpers access live Flatiron hardware registers.

Dependencies/integration: guarded by `_CX23885_VIDEO_H_`; assumes `struct cx23885_dev` and fixed-width integer types are in scope.

Risks: direct register access bypasses higher-level audio routing policy and can affect active capture. Header does not include dependencies itself.

Test signals: compile coverage and successful audio mux behavior on boards using Flatiron LR1/LR2 selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23885-video.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23885.h -->
## sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23885.h

Purpose: Central internal header for the cx23885 driver family. It defines board IDs, GPIO masks, video norms, shared structures, MMIO helper macros, and cross-file prototypes for core, cards, DVB, video, VBI, I2C, encoder, ALSA, and utility code.

Important APIs/types/functions: key types include `struct cx23885_dev`, `struct cx23885_tsport`, `struct cx23885_buffer`, `struct cx23885_riscmem`, `struct cx23885_i2c`, `struct cx23885_dmaqueue`, `struct cx23885_board`, `struct cx23885_input`, `struct cx23885_kernel_ir`, `struct cx23885_audio_dev`, and `struct sram_channel`. It defines `port_t`, input type enums, board constants through `CX23885_BOARD_AVERMEDIA_H789C`, `CX23885_NORMS`, GPIO bit masks, `cx_read/cx_write/cx_set/cx_clear`, `call_all`, `call_hw`, `norm_maxh()`, and declarations for all major subsystem entry points.

Control flow: no executable top-level flow, but this header is the contract that lets the cx23885 modules share a single device object. Probe fills `cx23885_dev`, per-port setup fills `cx23885_tsport`, video/DVB/VBI queues embed `cx23885_buffer`, and all register programming goes through the macros defined here.

State and persistence: defines all major in-memory state containers. State is volatile and bound to PCI device lifetime: V4L2 device/control state, PCI/MMIO data, board selection, I2C buses, TS ports, SRAM layout, analog video state, IR work/state, video devices, vb2 queues, encoder/audio state, and DMA workaround flag.

Dependencies/integration: includes Linux PCI/I2C/mutex/slab and media V4L2, tuner, tveeprom, vb2-dma-sg, vb2-dvb, rc-core, register map, and cx2341x encoder interface. It integrates every cx23885 translation unit and several adjacent media helpers.

Risks: this is a large shared internal ABI, so structure field changes have broad blast radius. MMIO macros depend on a local variable named `dev`, making misuse possible. Many board IDs and function prototypes require synchronization with card tables and Kconfig-selected modules.

Test signals: full driver compile is the main validation; runtime probe exercises device layout, queue structures, GPIO/register macros, and subsystem prototypes across analog, DVB, encoder, audio, and IR configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23885.h -->
