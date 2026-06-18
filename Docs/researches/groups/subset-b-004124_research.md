# subset-b-004124 research

This grouped report covers two SAA7134 media-driver files under `sources/distributed-fs/ceph-client/drivers/media/pci/saa7134`. Each section preserves the original source path for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/saa7134/saa7134-alsa.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/saa7134/saa7134-alsa.c

## Purpose
This file implements the optional ALSA PCM capture interface for Philips/NXP SAA713x PCI video-capture chips. It exposes the chip's DMA audio capture path as an ALSA capture-only PCM device, creates simple mixer controls for input selection and coarse volume/mute behavior, and wires the ALSA side into the main `saa7134` V4L2 driver through the global `saa7134_dmasound_init` and `saa7134_dmasound_exit` hooks.

The implementation is intentionally close to the older OSS DMA path in the same driver family. It allocates a vmalloc-backed audio buffer, maps it into a scatterlist and SAA7134 page table, programs the SAA7134 audio DMA register set, handles audio DMA interrupts, and reports period completion back to ALSA.

## Important APIs, Types, and Functions
The file's local ALSA card wrapper is `snd_card_saa7134_t`. It stores the ALSA `struct snd_card`, mixer lock and mixer state, active capture source, per-source capture controls, PCI/SAA7134 device pointers, I/O base, IRQ, and the `mute_was_on` restore flag. `snd_card_saa7134_pcm_t` is the per-open runtime object attached to `runtime->private_data`; it points back to the `saa7134_dev` and current substream.

DMA lifecycle helpers are `saa7134_dma_start()`, `saa7134_dma_stop()`, `saa7134_alsa_dma_init()`, `saa7134_alsa_dma_map()`, `saa7134_alsa_dma_unmap()`, `saa7134_alsa_dma_free()`, `dsp_buffer_init()`, and `dsp_buffer_free()`. These use `vmalloc_32()`, `vmalloc_to_page()`, `sg_init_table()`, `dma_map_sg()`, and the shared SAA7134 page-table helpers `saa7134_pgtable_alloc()`, `saa7134_pgtable_build()`, and `saa7134_pgtable_free()`.

The ALSA PCM callbacks are collected in `snd_card_saa7134_capture_ops`: `snd_card_saa7134_capture_open()`, `snd_card_saa7134_capture_close()`, `snd_card_saa7134_hw_params()`, `snd_card_saa7134_hw_free()`, `snd_card_saa7134_capture_prepare()`, `snd_card_saa7134_capture_trigger()`, `snd_card_saa7134_capture_pointer()`, and `snd_card_saa7134_page()`. The advertised hardware capabilities are in `snd_card_saa7134_capture`, which limits capture to 32 kHz, one or two channels, MMAP/interleaved/block-transfer formats, and 8/16-bit signed or unsigned PCM variants.

Mixer controls are defined by `SAA713x_VOLUME()` and `SAA713x_CAPSRC()` entries, implemented by `snd_saa7134_volume_info/get/put()` and `snd_saa7134_capsrc_info/get/put()`. `snd_saa7134_capsrc_set()` is the central control routine that updates the cached source state and programs SAA7134/SAA7133/SAA7135 audio input routing registers.

Interrupt handling is split between `saa7134_alsa_irq()` and `saa7134_irq_alsa_done()`. The IRQ handler filters shared interrupts for `SAA7134_IRQ_REPORT_DONE_RA3`, acknowledges the audio DMA done bit, and advances ring-buffer state. Card creation and teardown flow through `alsa_card_saa7134_create()`, `alsa_device_init()`, `alsa_device_exit()`, `saa7134_alsa_init()`, and `saa7134_alsa_exit()`.

## Control Flow
Module initialization is via `late_initcall(saa7134_alsa_init)`, deliberately after the sound core is available. Initialization installs `alsa_device_init` and `alsa_device_exit` into the main driver's `saa7134_dmasound_*` hooks, then walks `saa7134_devlist`. SAA7130 devices are skipped because they do not support digital audio; other present devices get an ALSA card through `alsa_card_saa7134_create()`.

Card creation checks the ALSA card index/enable arrays, allocates `struct snd_card` with `snd_card_new()`, initializes locks and chip pointers, requests the shared PCI IRQ using `devm_request_irq()`, creates mixer controls, creates one capture-only PCM device with `snd_pcm_new()`, fills card names, and calls `snd_card_register()`. On success, the card is stored in `snd_saa7134_cards[devnum]`.

Open initializes `dev->dmasound.read_count` and `read_offset`, derives the initial audio input from `dev->input->amux`, allocates the per-runtime PCM state, assigns ALSA hardware constraints, and temporarily unmutes TV audio if the V4L2 side had `ctl_mute` set. `hw_params` validates period size, period count, and total buffer size, tears down any prior runtime DMA area, allocates the vmalloc audio buffer, maps it for DMA, builds the SAA7134 DMA page table, and exposes that vmalloc buffer as ALSA's `runtime->dma_area`.

Prepare derives SAA7134 format bits from ALSA format, signedness, endian, channel count, and the selected input. It programs either SAA7134 audio registers or SAA7133/SAA7135 audio registers, writes DMA channel 6 base addresses, pitch, and control bits, stores the runtime rate, and forces the cached ALSA capture source control to match `dev->dmasound.input`. Trigger only starts or stops the audio DMA under `dev->slock`; actual hardware setup happened in prepare.

On each RA3 audio DMA interrupt, `saa7134_irq_alsa_done()` validates the expected odd/even block transition, logs lost IRQ status bits, detects ring overrun using `read_count`, schedules the next block address into `SAA7134_RS_BA1/BA2(6)`, advances `dma_blk`, increments `read_count`, records the active register, and calls `snd_pcm_period_elapsed()` once enough bytes have accumulated. The ALSA pointer callback subtracts one period from `read_count`, advances `read_offset`, wraps at `bufsize`, and returns the current frame position.

Close restores mute if open had cleared it. `hw_free` and `alsa_device_exit` tear down page tables, DMA mappings, vmalloc buffers, and ALSA card registration.

## State and Persistence
All persistent state is in kernel memory and device registers; nothing is saved across driver unload or reboot. Global module parameters `index[]` and `enable[]` control ALSA card allocation. `snd_saa7134_cards[]` tracks registered ALSA cards by SAA7134 device number.

Per-device audio state is mostly shared through `dev->dmasound`: block size/count, buffer size, vmalloc address, scatterlist, DMA sg length, SAA7134 page table, current DMA block, read offset/count, selected input, current ALSA substream, DMA running flag, and a mutex used around open-time state initialization. `dev->slock` protects IRQ and trigger DMA fields. Mixer state lives in `snd_card_saa7134_t` and is protected by `mixer_lock`; it caches per-source volume, active capture source address, and left/right boolean source state.

Hardware state programmed by this file includes audio format registers, SIF sample frequency, analog I/O selection, SAA7133 digital input/output crossbars, DMA channel 6 base/pitch/control registers, and the main driver's DMA enable bits via `saa7134_set_dmabits()`. The `mute_was_on` flag is a per-card transient used to restore V4L2 mute state after capture closes.

## Dependencies and Integration Points
This file depends on `saa7134.h` and `saa7134-reg.h` for device structures, register constants, `saa_readl/writel/writeb/andorb/andorl`, `saa_dsp_writel()`, `saa7134_set_dmabits()`, `saa7134_pgtable_*()`, `saa7134_tvaudio_setmute()`, `saa7134_boards[]`, and the global device list. It integrates with ALSA core through card, PCM, mixer-control, PCM-ops, period-elapsed, XRUN, and mmap page APIs.

It uses the Linux DMA mapping API for `DMA_FROM_DEVICE`, vmalloc helpers for audio buffer pages, PCI device IDs to distinguish SAA7134 from SAA7133/SAA7135 register programming, and shared PCI interrupts. It also relies on the V4L2-side SAA7134 input model because `dev->input->amux` seeds the ALSA capture source.

## Risks and Edge Cases
The DMA buffer is vmalloc-backed and exposed to ALSA by overriding `runtime->dma_area`, while the hardware uses a separately built SAA7134 page table. That is deliberate but fragile: buffer-size validation, scatterlist construction, DMA mapping, and page-table teardown must stay exactly paired or capture can corrupt memory or leak mappings.

The IRQ and pointer logic uses `read_count` as an overrun and period accounting counter. The IRQ side updates it under `dev->slock`, while `snd_card_saa7134_capture_pointer()` updates it without taking that lock, so races are possible if ALSA pointer callbacks interleave with audio interrupts. Overrun handling calls `snd_pcm_stop_xrun()` after dropping the spinlock and returns without the final unlock path, which is intentional but easy to break.

Source and volume controls are coarse hardware switches rather than true gain controls. TV tuner volume is forced to 20, line volume maps around a threshold into mute/enable bits, and capture-source controls prevent deactivating the active source. User-space mixer behavior may therefore look unlike a normal ALSA mixer.

Rate handling is constrained to 32 kHz even though some line-input register paths include 48 kHz comments and encodings. The fixed rate avoids silent source-switch resampling problems, but any change to advertised rates must re-audit SAA7133/35 DDEP mode, TV/radio paths, and source switching. The initial `amux` conversion clamps invalid or out-of-range values to line 1, which can hide bad board definitions.

`alsa_device_init()` always returns 1 and ignores the error from `alsa_card_saa7134_create()`, so initialization failures may only be visible through logs. Device numbers beyond `SNDRV_CARDS` are rejected, and `dev->nr` is used as an index into `snd_saa7134_cards[]`; any mismatch between SAA7134 numbering and ALSA card capacity is a functional limit.

## Test Signals
Build signals include compiling this file with ALSA enabled, SAA7134 core symbols available, and no missing references to the V4L2-side DMA/page-table helpers. Runtime registration should log the ALSA driver load message and one card registration per non-SAA7130 SAA7134/SAA7133/SAA7135 device, with `/proc/asound/cards` and ALSA control enumeration showing the SAA7134 PCM and mixer controls.

Functional tests should open the capture PCM at 32 kHz with supported 8/16-bit, signed/unsigned, little/big-endian, mono/stereo formats; mmap the buffer; vary period sizes/counts at boundary values; start/stop repeatedly; and verify period interrupts advance monotonically without XRUN under normal load. Source-switch tests should cover TV tuner, line 1, line 2, mute restore, and V4L2 input changes before ALSA open. Hardware tests should watch `SAA7134_IRQ_REPORT_DONE_RA3`, lost-interrupt logging, overrun handling, and audio route behavior separately on SAA7134 and SAA7133/SAA7135 chips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/saa7134/saa7134-alsa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/saa7134/saa7134-cards.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/saa7134/saa7134-cards.c

## Purpose
This file is the SAA7134 driver's board database and board-specific initialization layer. It maps PCI subsystem IDs to `SAA7134_BOARD_*` entries, describes each supported capture card's tuner, radio, audio clock, inputs, GPIO routing, MPEG transport capability, demodulator options, and optional remote-control wiring, then applies early and I2C-dependent fixups during device initialization.

Most of the file is declarative hardware knowledge for many Philips/NXP SAA7130, SAA7133, SAA7134, and SAA7135 based analog, hybrid, DVB, ATSC, cardbus, and MPEG encoder boards. The executable part handles tuner callbacks, board-specific GPIO resets, EEPROM interpretation, subdevice creation, and tuner configuration.

## Important APIs, Types, and Functions
The exported board data is `saa7134_input_name[]`, `saa7134_boards[]`, `saa7134_bcount`, and `saa7134_pci_tbl[]`. `saa7134_boards[]` is an indexed array of `struct saa7134_board`; each entry commonly defines `.name`, `.audio_clock`, `.tuner_type`, `.radio_type`, `.tuner_addr`, `.radio_addr`, `.tda9887_conf`, `.tda829x_conf`, `.gpiomask`, `.inputs[]`, `.radio`, `.mute`, `.mpeg`, `.ts_type`, `.ts_force_val`, `.empress_addr`, `.rds_addr`, `.video_out`, and `.vid_port_opts`. `saa7134_pci_tbl[]` maps PCI vendor/device/subvendor/subdevice combinations to board IDs through `.driver_data` and is exported with `MODULE_DEVICE_TABLE(pci, ...)`.

Tuner callback helpers are `saa7134_xc2028_callback()`, `saa7134_xc5000_callback()`, `saa7134_tda8290_827x_callback()`, `saa7134_tda18271_hvr11x0_toggle_agc()`, `saa7134_kworld_sbtvd_toggle_agc()`, `saa7134_kworld_pc150u_toggle_agc()`, `saa7134_leadtek_hdtv200h_toggle_agc()`, `saa7134_tda8290_18271_callback()`, `saa7134_tda8290_callback()`, and exported `saa7134_tuner_callback()`. These are called by tuner subdevices to reset tuners, change LNA/AGC routing, or program video sync GPIO behavior.

Board initialization entry points are `saa7134_board_init1()` and `saa7134_board_init2()`. `saa7134_board_init1()` runs before I2C-dependent setup and mostly reads/prints GPIO state, sets `dev->has_remote`, powers or resets board components with GPIO writes, and applies hardware workarounds. `saa7134_board_init2()` runs after I2C is usable, handles EEPROM and demodulator bridge fixups, instantiates tuner subdevices with `v4l2_i2c_new_subdev()`, and calls `saa7134_tuner_setup()`.

`hauppauge_eeprom()` parses Hauppauge analog EEPROM data with `tveeprom_hauppauge_analog()` and logs or warns on model numbers. `saa7134_tuner_setup()` builds `struct tuner_setup` and `struct v4l2_priv_tun_config` requests for radio tuners, analog TV tuners, TDA9887 IF demods, XC2028 firmware parameters, and TEA5767 private configuration on selected boards.

## Control Flow
PCI matching starts with `saa7134_pci_tbl[]`. Exact subsystem matches map to known board IDs; later catch-all entries map SAA7130/7133/7134/7135 devices to `SAA7134_BOARD_UNKNOWN`, and Philips subsystem ID zero entries map to `SAA7134_BOARD_NOAUTO`. The core driver uses the selected board ID to copy tuner/audio/input defaults from `saa7134_boards[]`.

The first board initialization phase sets GPIO mode to input, reads `SAA7134_GPIO_GPSTATUS0`, logs the value because some vendors encode hardware variant bits there, and enters a large board switch. Common actions include marking GPIO or I2C remote-control support, warning about ambiguous FlyVideo or MD5044 variants, powering tuner chips up or down, disabling problematic remote chips, turning cardbus fans on, resetting XC2028/XC5000-capable boards, clearing production-test mode on RTD VFG7350, selecting analog AGC paths on Hauppauge hybrid boards, and applying fixed GPIO masks/status values for AverMedia, Beholder, MagicPro, VideoMate, and other hybrid designs.

The second phase runs once I2C can be used. It first applies board-type corrections or bridge initialization that must happen before tuner probing. BMK MPEX boards are split into tuner/no-tuner variants by probing address `0x60`. Medion MD7134 reads EEPROM bytes at `0x50` to infer tuner type and may write tuner address `0x61` to force analog IF mode. Philips Europa can be reclassified as the Snake reference design from EEPROM. Tiger/Tiger-S, ASUS P7131 analog, and Compro DVB-T200/T200A variants are reclassified from EEPROM hints. Hybrid boards write small I2C command sequences to demodulator/bridge addresses such as `0x08`, `0x09`, `0x0a`, or `0x0b` to expose analog tuners or initialize analog mode. Hauppauge boards parse EEPROM model data from `dev->eedata + 0x80`.

After fixups, `saa7134_board_init2()` creates tuner subdevices unless the device is suspended or has `TUNER_ABSENT`. It creates a radio tuner at `dev->radio_addr` when present, optionally creates a demod tuner on known demod addresses when `TDA9887_PRESENT` is set, and creates the TV tuner either at a fixed address or by probing address lists selected from `v4l2_i2c_tuner_addrs()`. `saa7134_tuner_setup()` then sends type/address/config callbacks to all tuner subdevices and applies per-tuner private configuration such as TDA9887 config flags and XC2028 firmware/demod selection. Finally, selected boards get TEA5767 private config.

During tuner operation, subdrivers call `saa7134_tuner_callback()`. It dispatches by `dev->tuner_type`: TDA8290 callbacks either go to the TDA18271 AGC path or the TDA827x LNA/vsync path; XC2028 callbacks reset tuner GPIOs; XC5000 callbacks either toggle special-mode reset pins on Behold boards or apply a broader analog-clock/GPIO initialization sequence for default boards.

## State and Persistence
The board table is static kernel data. It does not change at runtime, but selected board identity and copied board parameters in `struct saa7134_dev` may be changed by `saa7134_board_init2()` fixups based on EEPROM or I2C probing. Important mutable fields include `dev->board`, `dev->tuner_type`, `dev->tuner_addr`, `dev->radio_type`, `dev->radio_addr`, `dev->tda9887_conf`, `dev->gpio_value`, and `dev->has_remote`.

Hardware state is written into SAA7134 GPIO mode/status registers, audio/input routing fields indirectly consumed by other SAA7134 files, demodulator bridge I2C registers, tuner IF mode, and tuner AGC/LNA GPIO lines. These settings are volatile and must be re-established on probe and relevant resume paths; `saa7134_board_init2()` explicitly avoids tuner creation while `dev->insuspend` is true but still applies board setup around the switch logic.

Board entries define persistent-in-code defaults for input muxing. Each input combines an input type exposed to V4L2, a video mux (`vmux`), an audio mux (`amux`), and optional GPIO state. The rest of the driver consumes these structures when selecting inputs, setting mute/radio routes, configuring audio clocks, initializing MPEG/DVB paths, and deciding whether remote-control support is GPIO or I2C based.

## Dependencies and Integration Points
This file depends on `saa7134.h` and `saa7134-reg.h` for board IDs, input constants, audio mux constants, MPEG mode constants, register accessors, GPIO helpers, device state, and the `card(dev)` macro. It integrates with tuner and demodulator frameworks through `media/tuner.h`-style tuner types, `struct tuner_setup`, `saa_call_all(dev, tuner, ...)`, `v4l2_i2c_new_subdev()`, `v4l2_i2c_tuner_addrs()`, and `struct v4l2_priv_tun_config`.

External tuner/demod-specific dependencies include XC2028, XC5000, TDA8290/TDA827x, TDA18271, TEA5767, TDA9887, S5H1411-adjacent board support, and Hauppauge `tveeprom`. The PCI table integrates with the PCI core and module autoloading. MPEG fields integrate with the SAA7134 DVB and empress encoder paths, while `.video_out`, `.vid_port_opts`, `.ts_type`, and `.ts_force_val` guide transport or encoder routing outside this file.

Remote-control integration is by `dev->has_remote`, which later input/IR setup consumes. One fixup explicitly calls `saa7134_input_init1(dev)` when reclassifying an ASUS P7131 analog board after the usual IR init point, showing that board detection order affects input-device registration.

## Risks and Edge Cases
The biggest risk is stale or wrong board data. A single incorrect `vmux`, `amux`, tuner type, GPIO mask, radio address, MPEG mode, or PCI subsystem mapping can produce no video, no sound, inverted mute, disabled tuner power, missing remote control, or a board binding to the wrong configuration. Many entries include comments such as untested, FIXME, ambiguous hardware revision, or copied Windows/DScaler GPIO values; these should be treated as hardware assumptions rather than verified invariants.

Several boards share PCI IDs and require EEPROM or GPIO/I2C probing to differentiate. If EEPROM contents differ from expected bytes, the code may keep a default board, reclassify incorrectly, or only log a warning. The BMK MPEX probe uses a zero-length I2C receive as a presence test at address `0x60`; adapter behavior around that transaction matters. MD7134 EEPROM parsing has old and new structure branches and logs unknown tuner codes but may leave a default tuner type.

GPIO programming is board-specific and sometimes broad. Some paths write full masks such as `0xffffffff` or fixed mode/status values, and some callbacks toggle reset lines with sleeps. A wrong board selection can therefore disturb unrelated pins or hold a tuner/demod in reset. Hybrid-board AGC callbacks switch analog/digital RF paths, so incorrect callback dispatch can break DVB or analog reception depending on current mode.

I2C initialization sequences often ignore transfer failures or only warn. Demodulator bridge writes are required to make analog tuners visible on many hybrid boards; if those writes fail, later tuner probing may silently miss hardware. `saa7134_tuner_setup()` calls `saa_call_all()` broadly, so multiple tuner-like subdevices must respect mode masks and addresses.

The PCI table contains exact matches, duplicate-looking subsystem IDs for variants, and default catches. Ordering is important: a broad catch placed too early would hide exact board mappings, while a duplicate subsystem entry with different `driver_data` could make one board variant unreachable. Board count and enum ordering must remain synchronized with `saa7134_boards[]`.

## Test Signals
Build signals are successful compilation of the SAA7134 driver with tuner, tveeprom, I2C, V4L2, DVB, and empress paths enabled in broad configurations. Static review should verify every `SAA7134_BOARD_*` used in `saa7134_pci_tbl[]` has a matching `saa7134_boards[]` entry and that board array count matches expectations.

Probe-time logs are key runtime signals: GPIO value printout, board name, board-type fixup messages, Hauppauge model log, tuner-type logs, warnings about ambiguous hardware, and I2C failure warnings. Hardware validation should cover V4L2 input enumeration and switching for TV/composite/S-Video/radio/mute, audio route correctness, remote-control detection, tuner attach messages, and MPEG/DVB frontend availability for boards with `.mpeg = SAA7134_MPEG_DVB` or `.mpeg = SAA7134_MPEG_EMPRESS`.

Regression tests should include exact PCI-ID autodetect, manual `card=` override behavior, suspend/resume, tuner callbacks during analog/digital mode changes, XC2028/XC5000 reset paths, TDA18271 AGC toggles, and EEPROM-driven reclassification paths for Philips Europa/Snake, Tiger/Tiger-S, ASUS P7131 analog, Compro DVB-T200/T200A, BMK MPEX, MD7134, and Hauppauge HVR variants. For board-table edits, real hardware or user-provided GPIO/I2C traces are the highest-value signal because many failures are board-specific and invisible to compile tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/saa7134/saa7134-cards.c -->
