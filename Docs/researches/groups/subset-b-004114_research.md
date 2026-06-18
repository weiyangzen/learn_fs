# subset-b-004114 research

Grouped research report for the requested cx23885 NetUP/CX23888 and cx25821 media PCI driver files. Each section is keyed by original source path for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23888-ir.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23888-ir.c

Purpose: implements the CX23888 integrated consumer infrared controller as a V4L2 subdevice on cx23885-family PCIe bridges. It programs the IR register block, exposes V4L2 IR receive/transmit parameter operations, converts hardware FIFO pulse-width records into `struct ir_raw_event` data, and registers/unregisters the IR subdevice under `CX23885_HW_888_IR`.

Important APIs and functions: public entry points are `cx23888_ir_probe` and `cx23888_ir_remove`. The V4L2 operation tables bind `cx23888_ir_irq_handler`, `cx23888_ir_log_status`, optional advanced-debug register accessors, RX ops (`cx23888_ir_rx_read`, `rx_g_parameters`, `rx_s_parameters`) and TX ops (`tx_write`, `tx_g_parameters`, `tx_s_parameters`). Helper groups cover register access (`cx23888_ir_write4`, `read4`, `and_or4`), carrier and pulse-width math (`carrier_freq_to_clock_divider`, `pulse_width_count_to_ns`, `ns_to_pulse_clocks`), control bits, IRQ enables, low-pass filter setup, and duty-cycle programming.

Control flow: probe allocates `struct cx23888_ir_state`, allocates an RX kfifo, initializes the subdevice, registers it with the parent `v4l2_device`, disables IR interrupts, then applies default RX and TX parameters. RX parameter setting disables receiver/IRQs, configures demodulation or raw pulse-width timing, sets carrier window and low-pass filter, stores divider and inversion in atomics, resets the software FIFO when enabling, and then enables hardware plus optional IRQs. The IRQ handler reads status/enables, drains the hardware RX FIFO into the kfifo on service or timeout, reports software/hardware overruns and end-of-receive via `v4l2_subdev_notify`, and clears hardware overrun/timeout by toggling control bits. `rx_read` drains complete FIFO records, interprets level/timeout bits, applies polarity inversion, clamps duration to `IR_MAX_DURATION`, and writes `ir_raw_event` records back into the caller buffer. TX configuration programs carrier/duty/polarity and enables hardware, but `tx_write` currently only enables the TX service interrupt and reports all bytes accepted.

State and persistence: state is volatile driver state only. `cx23888_ir_state` owns the V4L2 subdevice, parent `cx23885_dev`, saved RX/TX parameter snapshots protected by mutexes, atomic clock divider/inversion values consumed in interrupt/read paths, and a spinlock-protected RX kfifo sized for 256 FIFO records. Hardware state persists only in MMIO registers while the device is active; remove explicitly shuts down RX/TX, unregisters the subdevice, frees the kfifo, and frees state.

Dependencies and integration points: depends on cx23885 register helpers from `cx23885.h`, `cx23888-ir.h`, Linux kfifo/slab, V4L2 subdev APIs, and `rc-core` raw IR event definitions. It integrates with the parent cx23885 device through `v4l2_device_register_subdev`, `cx23885_find_hw`, `CX23885_HW_888_IR`, and the parent interrupt dispatch through the subdev interrupt service routine. Debug integration uses module parameter `ir_888_debug` and optional `CONFIG_VIDEO_ADV_DEBUG`.

Risks: TX is not fully implemented despite exposing TX hooks; callers may see accepted writes without hardware FIFO programming. IRQ draining depends on kfifo capacity and correct record-size alignment; software FIFO overflow loses pulse data. Timing conversion uses fixed 54 MHz IR reference clock and integer rounding, so carrier/window edge cases can differ from requested values. Several hardware-clear paths toggle receiver/FIFO enables, which can drop in-flight pulses. Advanced debug register writes can alter raw hardware state. There is a typo-like macro name `CX23888_IR_MAKS2_REG`, though it is unused here.

Test signals: there are no local unit tests in this subset. Useful signals are kernel build coverage with `CONFIG_VIDEO_CX23885`, probe/remove on CX23888 hardware, V4L2 IR parameter get/set behavior, rc-core event decoding under real remote input, overrun/timeout notification behavior under high pulse rates, and log-status output matching register values. TX should be treated as unimplemented unless validated on hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23888-ir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23888-ir.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23888-ir.h

Purpose: declares the cx23885-facing lifecycle API for the CX23888 IR controller subdevice.

Important APIs and types: exports `cx23888_ir_probe(struct cx23885_dev *dev)` and `cx23888_ir_remove(struct cx23885_dev *dev)`. It intentionally exposes no internal register definitions or state types; those remain private to `cx23888-ir.c`.

Control flow: parent cx23885 board setup can include this header and call probe during device initialization and remove during teardown. The implementation registers and unregisters a V4L2 subdevice internally.

State and persistence: this header owns no state. Its declarations operate on the parent `struct cx23885_dev`, with all IR state allocated by the C implementation and attached to V4L2 subdev data.

Dependencies and integration points: requires the including translation unit to know `struct cx23885_dev`, typically through `cx23885.h`. It is the integration boundary between the cx23885 core and the CX23888-specific IR controller.

Risks: because only lifecycle functions are declared, callers cannot inspect partial initialization state and must treat probe/remove return codes as authoritative. Missing include of a forward declaration is acceptable only when included after `cx23885.h`.

Test signals: compile-time coverage is the main signal for this header. Runtime probe/remove tests for `cx23888-ir.c` validate the declarations indirectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23888-ir.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/netup-eeprom.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/netup-eeprom.c

Purpose: reads identification data from a 24LC02 EEPROM on NetUP Dual DVB-S2 CI cards, specifically the board revision and two six-byte MAC addresses.

Important APIs and functions: `netup_eeprom_read(struct i2c_adapter *i2c_adap, u8 addr)` performs a combined one-byte address write and one-byte data read from EEPROM I2C address `0x50`. `netup_get_card_info(struct i2c_adapter *i2c_adap, struct netup_card_info *cinfo)` reads revision byte 63, MAC bytes 64-69 for port 0, and MAC bytes 70-75 for port 1.

Control flow: `netup_eeprom_read` builds two `i2c_msg` entries, initializes the target offset, calls `i2c_transfer`, logs an error if two messages are not completed, and returns either the byte value or `-1`. `netup_get_card_info` performs sequential single-byte reads and stores results directly into the output structure.

State and persistence: the only persistent state is on the EEPROM device. The driver does not cache contents, validate MAC address format, or preserve partial-read error state. Failed reads become `0xff` when assigned to `u8` MAC/revision fields because the helper returns `-1` as an `int`.

Dependencies and integration points: depends on Linux I2C APIs, `cx23885.h`, and structure declarations in `netup-eeprom.h`. It is consumed by cx23885 NetUP board setup paths that need card revision and per-port MAC addresses.

Risks: the file contains a stray line with just `#` before includes, which is accepted as an empty preprocessing directive but is unusual. Error handling is weak for multi-byte card info reads because individual failures are not propagated. The EEPROM layout offsets are hard-coded. It assumes a one-byte EEPROM address and 7-bit I2C address `0x50`.

Test signals: useful validation includes I2C transfer failure injection, real NetUP EEPROM reads confirming revision/MAC offsets, and build coverage for the cx23885 NetUP configuration. No local tests are present in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/netup-eeprom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/netup-eeprom.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/netup-eeprom.h

Purpose: defines the NetUP EEPROM card-info structure and declares the EEPROM read helpers.

Important APIs and types: `struct netup_port_info` contains one six-byte MAC address. `struct netup_card_info` contains two ports and an 8-bit revision. Exported functions are `netup_eeprom_read` and `netup_get_card_info`.

Control flow: consumers allocate or embed `struct netup_card_info`, pass an `i2c_adapter` to `netup_get_card_info`, and then read populated revision/MAC fields. Single-address reads can use `netup_eeprom_read` directly.

State and persistence: the header stores no state. It documents the shape of data copied from EEPROM into transient caller-owned structures.

Dependencies and integration points: relies on Linux integer aliases (`u8`) and `struct i2c_adapter` from included kernel headers in consumers. It is the public boundary for `netup-eeprom.c` inside the cx23885 driver.

Risks: the API has no explicit error-returning version of `netup_get_card_info`, so callers cannot distinguish valid `0xff` EEPROM bytes from read failures without changing the implementation. Structure fields are fixed to exactly two ports.

Test signals: compile coverage and board-level EEPROM read tests validate this header. Static checks should ensure callers have included I2C type definitions before this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/netup-eeprom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/netup-init.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/netup-init.c

Purpose: performs NetUP Dual DVB-S2 CI board-specific initialization by programming the cx23885 A/V core over I2C to set AUX clock output to 27 MHz.

Important APIs and functions: public `netup_initialize(struct cx23885_dev *dev)` uses static helpers `i2c_av_write`, `i2c_av_write4`, `i2c_av_read`, and `i2c_av_and_or` to access 8-bit and 32-bit A/V core registers at I2C address `0x88 >> 1`.

Control flow: `netup_initialize` selects `dev->i2c_bus[2]`, stops the microcontroller by clearing bit `0x10` in register `0x803`, writes AUX PLL fractional value `0xea0eb3` to `0x114`, writes AUX PLL integer value `0x090319` to `0x110`, and restarts the microcontroller by setting bit `0x10`. The read-modify-write helper reads a byte register and writes back masked/or'ed data.

State and persistence: programmed state is hardware register state in the A/V core. There is no software cache and no retry/recovery beyond logging transfer errors. Helper writes use little-endian byte order for 32-bit values as expected by the target register protocol.

Dependencies and integration points: depends on `cx23885.h`, the cx23885 I2C bus array, Linux I2C transfer API, and `netup-init.h`. It is called from NetUP-specific board initialization before DVB/CI components rely on the 27 MHz AUX clock.

Risks: I2C helper functions log failures but do not return errors, so `netup_initialize` cannot report partial PLL programming failure. The function assumes bus 2 exists and that the A/V core is reachable at address `0x44`. Register constants are magic values with no local symbolic definitions. The read helper logs "write error" on its initial address phase, which can confuse diagnostics.

Test signals: board bring-up should verify the AUX clock frequency, successful I2C transactions, and downstream tuner/demod stability. No local unit tests are present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/netup-init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/netup-init.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/netup-init.h

Purpose: declares the NetUP board initialization hook.

Important APIs and types: exports `netup_initialize(struct cx23885_dev *dev)`.

Control flow: cx23885 board setup calls this function for NetUP cards to program A/V core PLL registers. The implementation handles I2C access internally.

State and persistence: the header has no state. Its function mutates hardware clock configuration through the parent device.

Dependencies and integration points: requires consumer visibility of `struct cx23885_dev`. It is the integration boundary for NetUP-specific AUX clock initialization.

Risks: unlike many kernel headers, it has no include guard; repeated inclusion is harmless for this single extern declaration but inconsistent with local style. The API exposes no error return even though initialization can fail at the I2C layer.

Test signals: compile coverage and board-level clock bring-up validate this declaration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/netup-init.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx25821/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx25821/Kconfig

Purpose: defines kernel configuration options for the Conexant cx25821 video driver and its optional ALSA DMA audio companion.

Important APIs and symbols: `VIDEO_CX25821` is a tristate depending on `VIDEO_DEV`, `PCI`, and `I2C`, selecting `I2C_ALGOBIT` and `VIDEOBUF2_DMA_SG`. `VIDEO_CX25821_ALSA` is a tristate depending on `VIDEO_CX25821` and `SND`, selecting `SND_PCM`.

Control flow: Kconfig selection determines whether `cx25821.o` and `cx25821-alsa.o` are built by the Makefile. Help text names the produced modules and explains the ALSA function-01 hardware requirement.

State and persistence: no runtime state. Configuration values persist in the kernel build configuration and control module availability.

Dependencies and integration points: integrates with the media PCI driver Kconfig tree, V4L2 core, PCI, I2C, videobuf2 DMA-SG, and ALSA PCM. The ALSA option depends on the base video driver because the audio module attaches to devices owned by the cx25821 PCI driver.

Risks: help text mentions audio PCI IDs `14f1:8801` or `14f1:8811`, while the ALSA source table in this snapshot contains `14f1:0920`; that mismatch can confuse users. Selecting `I2C_ALGOBIT` is conservative even though this implementation uses a custom register-backed `i2c_algorithm`.

Test signals: menuconfig visibility, allmodconfig builds, module load tests for `cx25821`, and optional `cx25821-alsa` load after a base device is present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx25821/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx25821/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx25821/Makefile

Purpose: maps cx25821 Kconfig symbols to object files for the base video driver and ALSA companion module.

Important APIs and entries: `cx25821-y` links `cx25821-core.o`, `cx25821-cards.o`, `cx25821-i2c.o`, `cx25821-gpio.o`, `cx25821-medusa-video.o`, and `cx25821-video.o` into `cx25821.o`. `obj-$(CONFIG_VIDEO_CX25821)` builds the base module and `obj-$(CONFIG_VIDEO_CX25821_ALSA)` builds `cx25821-alsa.o`.

Control flow: kbuild compiles the listed implementation files into a single base module, while the ALSA file remains a separate module that late-initializes against the registered PCI driver.

State and persistence: no runtime state. Build output shape is determined by selected Kconfig symbols.

Dependencies and integration points: depends on the Kconfig symbols from `Kconfig` and on the source file boundaries in this directory. The base module must export symbols used by the ALSA module, such as SRAM channel setup and IRQ bit printing.

Risks: adding new implementation files requires updating `cx25821-y`; forgetting to do so can leave declarations unresolved or functionality omitted. ALSA is not linked into the base module, so symbol export and module load ordering matter.

Test signals: `make M=drivers/media/pci/cx25821` style builds with base-only and base-plus-ALSA configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx25821/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx25821/cx25821-alsa.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx25821/cx25821-alsa.c

Purpose: implements an ALSA PCM capture companion for cx25821 boards, using audio channel SRAM/DMA resources from the base cx25821 driver to expose 48 kHz stereo S16_LE capture.

Important APIs and functions: module entry is `late_initcall(cx25821_alsa_init)` and exit is `cx25821_audio_fini`. Device attach flow uses `cx25821_alsa_init_callback` and `cx25821_audio_initdev`. PCM callbacks include `snd_cx25821_pcm_open`, `hw_params`, `hw_free`, `prepare`, `trigger`, `pointer`, and `page`. DMA helpers include `cx25821_alsa_dma_init`, `dma_map`, `dma_unmap`, `dma_free`, `_cx25821_start_audio_dma`, `_cx25821_stop_audio_dma`, and `dsp_buffer_free`. IRQ handling is through a separate shared `cx25821_irq` and `cx25821_aud_irq`.

Control flow: the late init finds the already registered `"cx25821"` PCI driver and iterates its devices. For each enabled ALSA device, it creates an ALSA card, stores `struct cx25821_audio_dev` in card private data, requests the same PCI IRQ with a shared handler, creates one capture PCM named `"cx25821 Digital"`, and registers the card. On `hw_params`, it allocates a vmalloc_32 buffer, converts pages to a scatterlist, maps it for DMA, builds an audio RISC program with `cx25821_risc_databuffer_audio`, and loops the RISC jump back to the start. Trigger start enables GPIO0 direction for audio MCLK, configures SRAM channel `SRAM_CH08`, sets audio length/config registers, clears and enables interrupts, and turns on FIFO/RISC bits. IRQ handling acknowledges PCI/audio status, reports errors, resets on sync errors, and on downstream RISC1 updates a period counter then calls `snd_pcm_period_elapsed`.

State and persistence: `struct cx25821_audio_dev` tracks parent cx25821 device, ALSA card, PCI device, IRQ, DMA buffer, period sizing, current substream, and atomic hardware period count. `struct cx25821_audio_buffer` owns vmalloc memory, scatterlist, DMA mapping length, and RISC memory. Runtime state is freed in `hw_free` or module exit; hardware register state is enabled only while PCM is running.

Dependencies and integration points: depends on ALSA core/PCM APIs, PCI DMA mapping, vmalloc page mapping, base cx25821 register macros, exported `cx25821_sram_channels`, `cx25821_sram_channel_setup_audio`, `cx25821_risc_databuffer_audio`, `cx25821_sram_channel_dump_audio`, `cx25821_print_irqbits`, and GPIO helper. It attaches to existing `struct cx25821_dev` through the V4L2 device stored in PCI drvdata.

Risks: the module uses `driver_find` without checking for NULL before `driver_for_each_device`, which can fail badly if the base driver is unavailable. Error paths in `hw_params` can leave DMA mappings or vmalloc allocations if failure occurs after partial setup; `chip->buf` is nulled before freeing via common cleanup. The audio IRQ handler shares the same PCI interrupt line and acknowledges broad PCI status, so interaction with the base video IRQ handler is delicate. Only capture is created (`snd_pcm_new(..., 0 playback, 1 capture)`). Buffer constraints are narrow and require power-of-two periods.

Test signals: build with `CONFIG_VIDEO_CX25821_ALSA`, module load after base driver, `arecord` capability/probing, mmap capture, period interrupt cadence, RISC error diagnostics, and unload/reload leak checks. Hardware tests should run concurrent video and audio capture to catch shared IRQ masking regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx25821/cx25821-alsa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx25821/cx25821-audio.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx25821/cx25821-audio.h

Purpose: defines audio DMA sizing constants used by the cx25821 core and ALSA support.

Important APIs and constants: `AUDIO_LINE_SIZE` is 128, `LINES_PER_BUFFER` is 15, `NUMBER_OF_PROGRAMS` is 8, and `MAX_AUDIO_DMA_BUFFER_SIZE` derives from RISC instruction sizes. It conditionally computes `MAX_BUFFER_PROGRAM_SIZE` using RISC NOOP instructions.

Control flow: no executable code. The constants guide buffer and RISC program sizing expectations for audio DMA paths.

State and persistence: no state. Values are compile-time constants.

Dependencies and integration points: included by `cx25821.h`, making these constants visible to core and audio compilation units. It aligns with SRAM audio cluster size definitions in `cx25821-sram.h` and RISC instruction generation in `cx25821-core.c`.

Risks: sizing constants must stay consistent with actual RISC program generation; undersizing can cause DMA program overflow, while oversizing wastes coherent memory. Some constants are legacy or not directly consumed by the current ALSA path.

Test signals: compile coverage and ALSA `hw_params`/capture tests that exercise maximum period counts and RISC program allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx25821/cx25821-audio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx25821/cx25821-biffuncs.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx25821/cx25821-biffuncs.h

Purpose: provides small bit-manipulation helpers used by Medusa video register programming.

Important APIs and functions: `SetBit(Bit)` expands to `1 << Bit`; `getBit(sample, index)` extracts a bit as `u8`; `clearBitAtPos(value, bit)` clears one bit in a `u32`; `setBitAtPos(sample, bit)` sets one bit in a `u32`.

Control flow: inline helpers are used in read-modify-write sequences for Medusa decoder registers, especially `MISC_TIM_CTRL`, DENC enable bits, and procamp-related control paths.

State and persistence: no state. Helpers return computed values for callers to write to hardware.

Dependencies and integration points: depends on Linux fixed-width aliases `u8` and `u32`, normally available through the including driver headers. Included directly by `cx25821-medusa-video.c`.

Risks: shifts are unguarded; bit indexes outside the width of `int`/`u32` would be undefined. `SetBit` uses `1` rather than `1U`, so high-bit use could be signed-sensitive, though current callers use small bit positions.

Test signals: compile coverage and register-programming tests that verify individual bit changes preserve unrelated register fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx25821/cx25821-biffuncs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx25821/cx25821-cards.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx25821/cx25821-cards.c

Purpose: declares the cx25821 board table used by core device setup and V4L2 capability reporting.

Important APIs and data: `cx25821_boards[]` contains `UNKNOWN_BOARD` with safe zero clock default and `CX25821_BOARD` named `"CX25821"` with `portb = CX25821_RAW` and `portc = CX25821_264`.

Control flow: `cx25821_dev_setup` selects board index 1 and later reports `cx25821_boards[dev->board].name`. The table does not perform autodetection logic itself.

State and persistence: static board metadata only. It is process-global driver data and not mutated at runtime.

Dependencies and integration points: depends on `cx25821.h` for board enum values and structure definitions. The core driver and V4L2 querycap path consume this table.

Risks: the core currently hard-codes `dev->board = 1`, so table expansion alone will not add real board autodetection. Unknown board has safe clock but may not be reachable because incorrect hardware is rejected earlier.

Test signals: probe logs and `VIDIOC_QUERYCAP` card names should reflect expected board table entries. Build coverage catches structure drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx25821/cx25821-cards.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx25821/cx25821-core.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx25821/cx25821-core.c

Purpose: implements the base cx25821 PCI/V4L2 driver: PCI probe/remove, MMIO mapping, register/PLL initialization, SRAM channel descriptors, RISC program generation, video IRQ dispatch, DMA helper exports, and base device teardown.

Important APIs and functions: module lifecycle is `cx25821_init`/`cx25821_fini` registering `cx25821_pci_driver`. Probe/remove are `cx25821_initdev` and `cx25821_finidev`. Exported helpers include `cx25821_sram_channels`, `cx25821_sram_channel_setup`, `cx25821_sram_channel_setup_audio`, `cx25821_sram_channel_dump_audio`, `cx25821_riscmem_alloc`, `cx25821_risc_databuffer_audio`, `cx25821_free_buffer`, `cx25821_print_irqbits`, `cx25821_dev_get`, and `cx25821_dev_unregister`. Internal setup includes `cx25821_registers_init`, `cx25821_initialize`, `cx25821_dev_setup`, `cx25821_shutdown`, and RISC builders `cx25821_risc_buffer`/`cx25821_risc_field`.

Control flow: PCI probe allocates `struct cx25821_dev`, registers a V4L2 device, enables PCI, calls device setup, sets bus mastering/DMA mask, and requests a shared IRQ. Device setup validates device ID `0x8210`, initializes channel-to-SRAM mappings, requests and maps BAR0, logs board information, initializes hardware registers/PLLs/SRAM, registers I2C bus 0, initializes Medusa video, registers V4L2 video devices, and reads hardware revision. Runtime video IRQ reads `PCI_INT_STAT`, checks the low eight video bits, reads each channel status, calls `cx25821_video_irq`, and acknowledges channel bits. Remove shuts hardware down, frees IRQ, disables PCI, unregisters video/I2C/MMIO/V4L2, and frees the device.

State and persistence: `struct cx25821_dev` persists for the PCI device lifetime and owns MMIO pointers, PCI metadata, I2C bus objects, channel state, board/tvnorm fields, and V4L2 device state. `cx25821_sram_channels` is the fixed hardware mapping for video A-H, audio, video upstream I/J, and audio upstream B. RISC memory is coherent DMA memory owned by buffers and freed by `cx25821_free_buffer` or audio cleanup.

Dependencies and integration points: depends on Linux PCI, DMA, IRQ, I2C, V4L2, videobuf2, and local headers `cx25821.h`, `cx25821-sram.h`, and `cx25821-video.h`. It integrates with `cx25821-i2c.c`, `cx25821-gpio.c`, `cx25821-medusa-video.c`, `cx25821-video.c`, and optional `cx25821-alsa.c` through exported symbols and shared device state.

Risks: setup failure paths after memory-region request or ioremap do not always release every prior resource in the same function, so probe-error cleanup deserves scrutiny. The hard-coded board selection and PLL magic values make unsupported variants risky. `cx25821_set_pixel_format` writes `dev->channels[channel_select]` even when `channel_select` is outside 0-7 after skipping the MMIO write, so invalid callers can corrupt out-of-range state. RISC builders assume valid scatterlists and use `BUG_ON` for size checks. The base IRQ handler only services video channels, while ALSA registers a separate shared IRQ handler.

Test signals: kernel build, PCI probe/remove, MMIO mapping failure paths, video interrupt delivery, buffer DMA under scatterlist fragmentation, module unload leak checks, and concurrent ALSA/video capture. Register dump functions provide diagnostic signal after RISC opcode errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx25821/cx25821-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx25821/cx25821-gpio.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx25821/cx25821-gpio.c

Purpose: controls cx25821 GPIO direction/value for board initialization and audio clock output support.

Important APIs and functions: exported `cx25821_set_gpiopin_direction(struct cx25821_dev *dev, int pin_number, int pin_logic_value)` changes output-enable bits for low/high GPIO banks. Static `cx25821_set_gpiopin_logicvalue` sets a pin output value after forcing output direction. `cx25821_gpio_init` applies board-specific GPIO setup.

Control flow: direction helper rejects pin numbers >=47, chooses low or high OE register, reads current OE state, sets or clears the selected bit, and writes the result. Logic-value helper calls direction with output mode, selects low/high data register, updates the bit, and writes it. Board init currently sets GPIO5 high for `CX25821_BOARD_CONEXANT_ATHENA10`/default and delays 20 ms.

State and persistence: GPIO state persists in hardware registers while the device is powered. There is no software shadow; all operations are read-modify-write against MMIO.

Dependencies and integration points: depends on `cx25821.h` register macros, `GPIO_LO`, `GPIO_HI`, `GPIO_LO_OE`, `GPIO_HI_OE`, and `Set_GPIO_Bit`/`Clear_GPIO_Bit`. Core initialization calls `cx25821_gpio_init`, and ALSA start uses `cx25821_set_gpiopin_direction` for audio MCLK-related GPIO0 setup.

Risks: high-bank bit calculation subtracts 31 rather than 32, which may be intentional for register bit layout but is easy to misuse. `pin_logic_value` semantics in the direction helper map 1 to setting the OE bit and 0 to clearing it; comments say GPIOs 0 and 1 are output but implementation is generic. No locking protects concurrent GPIO read-modify-write operations.

Test signals: board bring-up verifying Medusa/Athena path selection on GPIO5, audio capture clock availability on GPIO0, and register readback for low/high GPIO banks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx25821/cx25821-gpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx25821/cx25821-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx25821/cx25821-i2c.c

Purpose: implements a register-backed Linux I2C adapter for cx25821 I2C masters and convenience helpers for 32-bit Medusa register access.

Important APIs and functions: adapter entry points are `i2c_xfer` and `cx25821_functionality` in `cx25821_i2c_algo_template`. Public driver helpers are `cx25821_i2c_register`, `cx25821_i2c_unregister`, `cx25821_i2c_read`, and `cx25821_i2c_write`. Low-level transfer helpers are `i2c_sendbytes`, `i2c_readbytes`, `i2c_wait_done`, `i2c_is_busy`, and `i2c_slave_did_ack`.

Control flow: registration copies adapter/client templates, names the adapter after the device, stores the bus as `algo_data`, associates V4L2 device data, and calls `i2c_add_adapter`. Transfers iterate message arrays; plain writes call `i2c_sendbytes`, reads call `i2c_readbytes`, and write-then-read pairs to the same address are joined with `NOSTOP` handling. Low-level helpers program address/data/control registers, poll the busy bit with bounded `udelay`, and optionally use extend/no-stop bits for multi-byte messages. `cx25821_i2c_read` writes a 16-bit register address to Medusa address `0x44`, reads four bytes, assembles little-endian `u32`, and returns it; write sends two address bytes plus four value bytes.

State and persistence: `struct cx25821_i2c` stores register offsets, period setting, adapter, and client. Hardware I2C controller state is in MMIO registers. No transaction history or error counters are persisted.

Dependencies and integration points: depends on Linux I2C core and `cx25821.h` register macros. Core setup configures bus 0 register offsets and registers it; Medusa video setup and diagnostics use `cx25821_i2c_read/write`. The optional `i2c_scan` module parameter is declared but not used in this file.

Risks: `i2c_wait_done` returns 0/1, but callers check `<0` even though it cannot return negative. ACK status is checked only for zero-length probe paths, not for normal byte writes/reads. `cx25821_i2c_read/write` ignore return values from `i2c_xfer` when assembling/returning register values. Medusa helpers force I2C address `0x44`, bypassing the template client address. There is no explicit locking around shared I2C controller access beyond the I2C core adapter serialization.

Test signals: I2C bus scan/probe, Medusa register readback after writes, error injection for timeout/no-ACK, and video-standard initialization that depends on large I2C register programming sequences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx25821/cx25821-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx25821/cx25821-medusa-defines.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx25821/cx25821-medusa-defines.h

Purpose: defines Medusa decoder identifiers and small constants shared by Medusa video programming.

Important APIs and constants: decoder IDs `VDEC_A` through `VDEC_H` map to 0-7. `END_OF_SEQ` is `0xF`. `MAX_REGISTRY_SZ` is defined as `40;`.

Control flow: Medusa functions use decoder IDs for switch statements and register offset calculations.

State and persistence: no state; compile-time constants only.

Dependencies and integration points: included by `cx25821-medusa-video.h`, which is included by Medusa implementation and indirectly by control paths.

Risks: `MAX_REGISTRY_SZ` includes a semicolon in the macro body, which is harmless only in statement-like contexts and risky in expressions. Decoder IDs must stay aligned with `MAX_DECODERS` and register block spacing in `cx25821-medusa-reg.h`.

Test signals: compile coverage and Medusa per-decoder control tests across all decoder IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx25821/cx25821-medusa-defines.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx25821/cx25821-medusa-reg.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx25821/cx25821-medusa-reg.h

Purpose: provides the Medusa video decoder/encoder register address map used by cx25821 I2C register programming.

Important APIs and constants: defines chip configuration registers (`CHIP_CTRL`, `AFE_*`, `DENC_AB_CTRL`, `BYP_AB_CTRL`, `MON_A_CTRL`, `PIN_OE_CTRL`), DENC A/B register blocks, decoder A-H blocks with 0x200 spacing, scaler/timing/procamp registers, comb-filter controls, version/reset registers, and byte-oriented aliases such as `VDEC_A_BRITE_CTRL`, `VDEC_A_CNTRST_CTRL`, `VDEC_A_USAT_CTRL`, `VDEC_A_VSAT_CTRL`, and `VDEC_A_HUE_CTRL`.

Control flow: `cx25821-medusa-video.c` combines base register constants with `0x200 * decoder` or `0x100 * encoder` offsets to initialize all decoders/encoders, set standard-specific timing, set resolution, enable blue-field output, and update brightness/contrast/hue/saturation.

State and persistence: no software state. The constants identify persistent hardware register addresses reachable through the cx25821 I2C adapter.

Dependencies and integration points: included by `cx25821.h`, making Medusa register names globally visible across the driver. It pairs with `cx25821-i2c.c` for actual access and `cx25821-medusa-video.c` for programming policy.

Risks: this is a manually maintained register map; a single incorrect address can program the wrong decoder field. `VDEC_H_INT_STAT_MASK` is `0x1E1E` while the pattern suggests `0x1E10`, which may be a hardware-specific exception or typo. Byte aliases for procamp controls rely on the I2C helper and hardware accepting byte-offset-style addresses even though the helper reads/writes four bytes.

Test signals: hardware register readback, video standard initialization on all decoder channels, procamp controls affecting the selected channel only, and regression checks for decoder-H interrupt/status behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx25821/cx25821-medusa-reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx25821/cx25821-medusa-video.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx25821/cx25821-medusa-video.c

Purpose: programs the Medusa/Athena video decoder and encoder over I2C for video standard, resolution, monitor routing, blue-field output, and V4L2 procamp controls.

Important APIs and functions: exported functions are `medusa_video_init`, `medusa_set_videostandard`, `medusa_set_resolution`, `medusa_set_brightness`, `medusa_set_contrast`, `medusa_set_hue`, and `medusa_set_saturation`. Internal helpers include `medusa_initialize_ntsc`, `medusa_initialize_pal`, `medusa_PALCombInit`, `medusa_enable_bluefield_output`, `medusa_set_decoderduration`, `mapM`, and `convert_to_twos`.

Control flow: core setup calls `medusa_video_init`, which disables auto/master source selection, sets decoder display duration to 0 for all decoders, configures DENC/monitor bypass/pin output registers, then calls `medusa_set_videostandard`. Standard selection chooses PAL initialization for PAL-BG/DK and NTSC otherwise. NTSC/PAL init loops over all decoders to write mode, horizontal/vertical timing, subcarrier step, VIP active output, special-play/chroma-runaway mitigations, VBI gating, comb-filter setup for PAL, and blue-field output. It loops over two encoders to write standard-specific DENC timing and subcarrier values. Resolution selection maps widths 160/176/320/352/720 to hscale/vscale constants for one decoder or all decoders. Procamp setters map V4L2 0-10000 ranges to signed/unsigned byte hardware values and update only the relevant low byte register.

State and persistence: state is hardware register state on Medusa. Driver software keeps the selected V4L2 standard and channel dimensions in `struct cx25821_dev`/channel state; this file writes hardware to match those values. There is no readback cache or transactional rollback.

Dependencies and integration points: depends on `cx25821_i2c_read/write`, Medusa register constants, bit helpers, V4L2 standard bits, and channel IDs. It is called from core initialization, video standard ioctl, format-setting/resolution path, and V4L2 control callbacks in `cx25821-video.c`.

Risks: many I2C writes overwrite `ret_val`, so earlier failures can be lost if later writes succeed. Several functions accept decoder indexes without complete validation; procamp setters compute `base + 0x200 * decoder` after only range-checking value, relying on callers to pass valid channel IDs. `convert_to_twos` ignores `bits_len` and uses 8-bit conversion unconditionally. Blue-field enable returns early for decoders E-H, so behavior differs across channels. Magic constants dominate and need hardware documentation for safe changes.

Test signals: real hardware initialization for NTSC and PAL inputs, scaler output at 720/352/320/176/160 widths, V4L2 brightness/contrast/hue/saturation controls per channel, and I2C failure injection to verify error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx25821/cx25821-medusa-video.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx25821/cx25821-medusa-video.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx25821/cx25821-medusa-video.h

Purpose: defines Medusa video color-control ranges and default procamp values.

Important APIs and constants: includes decoder IDs from `cx25821-medusa-defines.h`; defines `VIDEO_PROCAMP_MIN`/`MAX` as 0/10000, signed and unsigned byte target ranges, and defaults for sharpness, saturation, brightness, contrast, and hue.

Control flow: procamp setter functions use these ranges to map V4L2 control values to register byte values. `cx25821-video.c` uses matching defaults when creating V4L2 controls, especially brightness 6200 and contrast/saturation/hue 5000.

State and persistence: no state. Constants guide hardware value mapping and control defaults.

Dependencies and integration points: included by `cx25821-medusa-video.c` and other driver code needing Medusa defaults. Tied to V4L2 control setup and Medusa register programming.

Risks: defaults must stay consistent with V4L2 control initialization; drift can make reported defaults differ from hardware programming. Sharpness default is defined but not wired to a V4L2 control in this subset.

Test signals: V4L2 control default inspection and procamp mapping tests at min/mid/max values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx25821/cx25821-medusa-video.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx25821/cx25821-reg.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx25821/cx25821-reg.h

Purpose: defines the cx25821 bridge MMIO register map and bit fields for RISC DMA, PCI interrupts, GPIO, PLL/PCIe blocks, video channels, audio channels, I2C controllers, UART, motion detection, and pixel format constants.

Important APIs and constants: RISC opcodes/flags include `RISC_WRITE`, `RISC_JUMP`, `RISC_SYNC`, `RISC_IRQ1`, `RISC_SOL`, and `RISC_EOL`. Interrupt registers include `PCI_INT_MSK/STAT/MSTAT`, per-video `VID_*_INT_*`, audio `AUD_*_INT_*`, and field masks such as `FLD_VID_DST_RISC1` and `FLD_AUD_DST_RISCI1`. DMA channel register families define `DMA1_PTR1` through `DMA26_*`. Video destination/source registers cover GPCNT, DMA control, VIP control, pixel format, active controls, and CDT size. Audio registers cover `AUD_A_*` through `AUD_E_*` and `AUD_INT_DMA_CTL`. I2C register groups define `I2C1_*`, `I2C2_*`, and `I2C3_*`. Pixel constants include `PIXEL_FRMT_422`, `PIXEL_FRMT_411`, and `PIXEL_ENGINE_VIP1`.

Control flow: all implementation files use these constants through `cx_read`, `cx_write`, `cx_set`, and `cx_clear` macros defined in `cx25821.h`. Core setup programs PLLs, PCI interrupt masks, DMA descriptors, and SRAM channel descriptors. Video and ALSA paths enable FIFO/RISC bits, acknowledge interrupts, and configure formats using this map. I2C access depends on the I2C register definitions.

State and persistence: no software state; constants map to hardware state in BAR0 MMIO. Register values persist while the PCI function remains enabled and are reset or overwritten during `cx25821_initialize`/shutdown.

Dependencies and integration points: included by `cx25821.h` and directly by `cx25821-alsa.c`. It is the central hardware contract for every cx25821 source file in this subset.

Risks: broad global macro namespace increases collision risk. Some register definitions overlap by hardware design or legacy naming, which can confuse diagnostics. Any typo in address or bit mask affects low-level hardware programming and is hard to catch without hardware. RISC and DMA field constants must match the instruction builders exactly or capture/audio buffers can corrupt memory or stall.

Test signals: build coverage, MMIO register readback on hardware, successful DMA start/stop for all capture channels, audio capture interrupts, I2C transactions, and debug dumps after forced RISC opcode errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx25821/cx25821-reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx25821/cx25821-sram.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx25821/cx25821-sram.h

Purpose: defines fixed cx25821 SRAM layout for command blocks, instruction queues, cluster descriptor tables, and FIFO cluster buffers used by video, audio, and Mobilygen interface DMA channels.

Important APIs and constants: sizing constants include `VID_CMDS_SIZE`, `AUDIO_CMDS_SIZE`, `VID_IQ_SIZE`, `AUDIO_IQ_SIZE`, `VID_CDT_SIZE`, `AUDIO_CDT_SIZE`, `VID_CLUSTER_SIZE` 1440, and `AUDIO_CLUSTER_SIZE` 128. Address constants map RX and TX SRAM regions such as `VID_A_DOWN_CMDS`, `VID_A_IQ`, `VID_A_CDT`, `VID_A_DOWN_CLUSTER_1`, upstream video clusters, and audio clusters. Conversion helpers include `BYTES_TO_DWORDS`, `BYTES_TO_QWORDS`, and `BYTES_TO_OWORDS`.

Control flow: `cx25821-core.c` uses these addresses to populate `cx25821_sram_channels[]`; SRAM setup writes command, CDT, FIFO, pointer, and count registers based on each channel descriptor. Video and audio DMA then point hardware at these SRAM regions.

State and persistence: no software state. Constants describe hardware SRAM address allocation; actual SRAM contents are initialized during device setup and DMA start.

Dependencies and integration points: included by `cx25821.h` and `cx25821-core.c`. It must remain consistent with `struct sram_channel` descriptors and `cx25821-reg.h` DMA register constants.

Risks: static layout leaves little room for runtime validation; overlapping or incorrect addresses would cause cross-channel DMA corruption. Comments show several legacy/reserved regions, so maintainers must avoid assuming all apparent free space is usable. Audio channel setup expects only three audio clusters, unlike video's four.

Test signals: SRAM channel dump output, successful concurrent multi-channel video capture, audio capture, and RISC error diagnostics showing expected command/CDT/FIFO ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx25821/cx25821-sram.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx25821/cx25821-video.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx25821/cx25821-video.c

Purpose: implements cx25821 V4L2 video capture and partial output device registration using videobuf2 scatter-gather DMA, format negotiation, standard selection, controls, streaming, and video interrupt completion.

Important APIs and functions: exported functions are `cx25821_start_video_dma`, `cx25821_video_irq`, `cx25821_video_unregister`, and `cx25821_video_register`. VB2 operations are `cx25821_queue_setup`, `cx25821_buffer_prepare`, `cx25821_buffer_finish`, `cx25821_buffer_queue`, `cx25821_start_streaming`, and `cx25821_stop_streaming`. V4L2 ioctl handlers include querycap, enum/g/try/s format for capture and output, std get/set, input/output enum/get/set, log status, and control callback `cx25821_s_ctrl`.

Control flow: registration sets default NTSC, initializes the spinlock, loops over video-capable channels excluding audio channel 8, creates V4L2 controls for capture channels, initializes channel dimensions/format, initializes a VB2 queue for capture, copies the appropriate `video_device` template, and registers it. Buffer preparation computes bytes-per-line, validates plane size, creates a RISC program for top/bottom/interlaced/sequential fields, and sets payload. Queuing links RISC programs into an active list, patching the previous buffer jump to the new buffer. Streaming starts DMA using the first active buffer and channel SRAM descriptor. IRQ completion on `FLD_VID_DST_RISC1` timestamps and completes the first active buffer. Format setting selects Y41P/411 or YUYV/422, updates channel dimensions, programs pixel format and Medusa resolution. Standard setting updates tvnorm and asks Medusa to reprogram standard-specific registers.

State and persistence: per-channel state lives in `struct cx25821_channel`: format, field, dimensions, pixel format, CIF flags, VB2 queue, V4L2 controls, and active DMA queue. Per-buffer state includes RISC DMA memory and list linkage. Hardware state includes channel SRAM, DMA control, interrupt masks, pixel format, and Medusa decoder scaler/standard registers.

Dependencies and integration points: depends on V4L2/videobuf2 APIs, local `cx25821-video.h`, core DMA/RISC helpers, `cx25821_sram_channels`, Medusa control functions, and register macros. The base PCI IRQ handler in `cx25821-core.c` calls `cx25821_video_irq`.

Risks: `cx25821_start_streaming` assumes the active list has at least one buffer; VB2 `min_queued_buffers = 2` helps, but defensive checks are absent. `vidioc_s_fmt_vid_cap` programs `SRAM_CH00` pixel format and Medusa resolution regardless of the current channel, so nonzero channels may not be programmed correctly. Output devices are registered for upstream channels but their VB2 queues are not initialized, making output support incomplete. `dprintk` macro uses compile-time `VIDEO_DEBUG` rather than runtime `video_debug`, so module parameter has limited effect. Active queue manipulation lacks explicit locking in `buffer_queue`, relying on VB2 serialization.

Test signals: V4L2 compliance for capture devices, streaming with MMAP/USERPTR/DMABUF, all supported formats and widths, NTSC/PAL standard switching, control changes affecting Medusa registers, interrupt-driven buffer completion, streamoff returning queued buffers with error, and negative testing for output nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx25821/cx25821-video.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx25821/cx25821-video.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx25821/cx25821-video.h

Purpose: declares the cx25821 video module interface and pulls in the kernel/V4L2 dependencies needed by the video implementation.

Important APIs and constants: defines `VIDEO_DEBUG`, a `dprintk` macro, `FORMAT_FLAGS_PACKED`, and prototypes for `cx25821_start_video_dma`, `cx25821_video_irq`, `cx25821_video_unregister`, and `cx25821_video_register`.

Control flow: core setup calls `cx25821_video_register`; teardown calls `cx25821_video_unregister` per channel; the PCI IRQ handler calls `cx25821_video_irq`; streaming uses `cx25821_start_video_dma` from the VB2 start path.

State and persistence: the header contains no state. Its prototypes operate on `struct cx25821_dev`, `struct cx25821_dmaqueue`, `struct cx25821_buffer`, and `struct sram_channel` defined in `cx25821.h`.

Dependencies and integration points: includes many kernel headers, `cx25821.h`, and V4L2 common/ioctl/event headers. It is included by `cx25821-core.c` and `cx25821-video.c`.

Risks: `dprintk` references a `dev` variable implicitly and checks constant `VIDEO_DEBUG`, so it is context-sensitive and not controlled by the runtime `video_debug` module parameter in `cx25821-video.c`. Broad includes increase compile coupling.

Test signals: compile coverage and base/video module linkage validate the declarations. Runtime tests for registration, IRQ, and streaming validate the API contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx25821/cx25821-video.h -->
