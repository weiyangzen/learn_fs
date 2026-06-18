# Research: subset-b-006395

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/emu10k1/emupcm.c -->
# Research: sources/distributed-fs/ceph-client/sound/pci/emu10k1/emupcm.c

## Purpose
`emupcm.c` implements the ALSA PCM surfaces for EMU10K1/EMU10K2-family cards: standard voice playback plus AC97 ADC capture, multi-channel EFX playback/capture, mic capture, and legacy FX8010 TRAM playback. It bridges ALSA substream callbacks to the EMU voice allocator, page table memory mapper, FX routing mixer state, capture engines, and interrupt callbacks in `irq.c`.

## Important APIs, Types, and Functions
The exported entry points are `snd_emu10k1_pcm()`, `snd_emu10k1_pcm_multi()`, `snd_emu10k1_pcm_mic()`, and `snd_emu10k1_pcm_efx()`, each creating an ALSA `struct snd_pcm` device and installing `struct snd_pcm_ops`. Runtime-private state is `struct snd_emu10k1_pcm`, which tracks the owning `emu`, stream type, allocated voices, extra IRQ voice, mapped memory block, start address, capture registers, running flag, and resume position. Normal playback uses `snd_emu10k1_playback_*`; capture uses `snd_emu10k1_capture_*`; EFX playback has separate synchronized trigger logic; FX8010 playback uses `struct snd_emu10k1_fx8010_pcm` and ALSA indirect playback helpers.

## Control Flow
Open allocates `epcm`, assigns hardware capabilities, constrains rates/periods, and activates mixer controls. `hw_params` allocates EMU voices, ALSA SG pages, and an EMU PTB mapping through `snd_emu10k1_alloc_pages()`. `prepare` writes voice routing, loop bounds, interpolation, capture buffer base/size, and sample-rate fields. `trigger` starts or stops hardware by enabling voice/capture interrupts, writing pitch targets, unmuting or muting attenuation registers, and setting capture buffer-size registers. `pointer` reads hardware current-address registers and compensates for the 64-frame cache and interpolation lookahead. IRQ handlers installed in `emu` call `snd_pcm_period_elapsed()`.

## State and Persistence
No durable state is persisted. Active state lives in ALSA runtime private data, `emu->pcm_mixer[]`, `emu->efx_pcm_mixer[]`, `emu->efx_voices_mask[]`, callback pointers such as `emu->capture_interrupt`, voice dirty/use flags, and hardware registers. Close/open toggles control visibility via `snd_ctl_notify()`. `resume_pos` is retained across EFX stop/suspend trigger transitions to restart from the previous position.

## Dependencies and Integration Points
This file depends on core ALSA PCM helpers, `sound/emu10k1.h` register definitions, `voice.c` allocation, `memory.c` PTB mapping, `io.c` pointer-register writes and interrupt enables, mixer controls from `emumixer.c`, and `irq.c` callback dispatch. E-MU models use `emu->emu1010.word_clock` to constrain rates and adjust 44.1 kHz clocking. FX8010 playback integrates with `snd_emu10k1_fx8010_register_irq_handler()` and TRAM/GPR registers.

## Risks
The logic is timing-sensitive. Normal playback relies on an extra voice for period interrupts and compensates for cache behavior; changes to pitch, cache, or loop setup can create underruns or incorrect positions. EFX playback attempts an atomic multi-voice start using loop-stop bits and can fail with `-EAGAIN` under interruption. Capture has fixed two-period buffer-size constraints and a `udelay(50)` first-pointer workaround. Voice and mixer state must be torn down exactly once, or IRQ callbacks can observe stale substreams. EFX capture mask validation rejects unsupported channel counts; bypassing it can create broken ALSA hardware declarations.

## Test Signals
Exercise playback and capture open/hw_params/prepare/trigger/pointer paths with 8-bit, S16_LE, mono, stereo, and EFX multi-channel modes. Verify period interrupts advance with no missed callbacks, suspend/resume triggers preserve or reset position as intended, and mixer controls become inactive on close. For E-MU cards, test both 44.1 kHz and 48 kHz word-clock modes. Useful signals are `aplay`/`arecord` stability, ALSA PCM pointer monotonicity, `snd_pcm_period_elapsed()` cadence, and absence of stale IRQ callbacks after stream close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/emu10k1/emupcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/emu10k1/emuproc.c -->
# Research: sources/distributed-fs/ceph-client/sound/pci/emu10k1/emuproc.c

## Purpose
`emuproc.c` exposes EMU10K1 diagnostic and debug state through ALSA proc entries. It reports card identity, FX routing, S/PDIF lock/status, capture rates, voice allocator state, FX8010 GPR/TRAM/code dumps, and an FX8010 instruction disassembly. With `CONFIG_SND_DEBUG`, it also creates raw I/O and pointer-register read/write proc files for low-level hardware inspection.

## Important APIs, Types, and Functions
The public entry point is `snd_emu10k1_proc_init()`. Read callbacks include `snd_emu10k1_proc_read()`, `snd_emu10k1_proc_spdif_read()`, `snd_emu10k1_proc_rates_read()`, `snd_emu10k1_proc_acode_read()`, `snd_emu10k1_fx8010_read()`, and `snd_emu10k1_proc_voices_read()`. `struct emu10k1_reg_entry` plus `sblive_reg_entries[]`, `audigy_reg_entries[]`, and `emu10k1_const_entries[]` support symbolic FX8010 disassembly. Debug-only helpers read and write I/O registers, PTR/DATA register banks, and E-MU 1010 FPGA routes.

## Control Flow
Initialization registers read-only proc entries unconditionally for `emu10k1`, `voices`, FX8010 binary dumps, and `fx8010_acode`; additional S/PDIF and capture-rate entries are conditional on card capabilities. Reads query live hardware registers with `snd_emu10k1_ptr_read()`, `snd_emu10k1_efx_read()`, or FPGA helpers and format into `snd_info_buffer`. Binary FX8010 reads select an offset based on the entry name, allocate a temporary buffer, read register words, adjust Audigy TRAM address layout, and copy bytes to userspace.

## State and Persistence
The file does not own persistent state. It observes live `struct snd_emu10k1` fields, FX8010 program metadata, voice flags, masks, and hardware registers. Debug write proc files, when compiled in, directly mutate hardware I/O/PTR registers and therefore can alter device state outside normal ALSA control flows.

## Dependencies and Integration Points
It depends on ALSA proc/info APIs, `sound/emu10k1.h`, `p16v.h` capture-rate register definitions, FX8010 register accessors, E-MU 1010 FPGA helpers in `io.c`, and card capability flags initialized by the main driver. Proc output uses mixer route-name tables such as `snd_emu10k1_audigy_ins`, `snd_emu10k1_sblive_outs`, and `snd_emu10k1_fxbus`.

## Risks
Most production entries are read-only, but they still read live hardware and may have side effects on E-MU FPGA GPIO reads, as documented in `io.c`. `CONFIG_SND_DEBUG` write entries are intentionally sharp: they accept register/value text and write raw I/O or pointer registers with minimal validation. FX8010 binary reads allocate `count + 8`; callers with huge reads could stress memory, though proc read sizes are normally bounded by userspace. Disassembly tables encode hardware knowledge and can become misleading if register maps change.

## Test Signals
After driver load, verify proc entries appear only for matching capabilities and can be read without warnings or sleeps in atomic context. For FX8010 dumps, compare reported sizes with Audigy versus SB Live limits. For debug builds, test invalid register ranges are rejected or ignored, and raw writes do not overrun channel counts. S/PDIF and capture-rate output should track actual input lock/rate changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/emu10k1/emuproc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/emu10k1/io.c -->
# Research: sources/distributed-fs/ceph-client/sound/pci/emu10k1/io.c

## Purpose
`io.c` centralizes low-level EMU10K1 register access and hardware-control primitives. It provides serialized PTR/DATA and PTR2/DATA2 access, SPI/I2C codec transactions, E-MU 1010 FPGA register and route access, firmware bitstream upload, interrupt-mask manipulation, voice loop/interrupt control, wait timing, and AC97 read/write callbacks.

## Important APIs, Types, and Functions
Exported/common APIs include `snd_emu10k1_ptr_read()`, `snd_emu10k1_ptr_write()`, `snd_emu10k1_ptr_write_multiple()`, `snd_emu10k1_ptr20_read()`, `snd_emu10k1_ptr20_write()`, `snd_emu10k1_spi_write()`, `snd_emu10k1_i2c_write()`, FPGA helpers such as `snd_emu1010_fpga_write()`, `snd_emu1010_fpga_read()`, link helpers, `snd_emu1010_update_clock()`, `snd_emu1010_load_firmware_entry()`, interrupt enable/disable helpers, loop-stop helpers, `snd_emu10k1_wait()`, and AC97 callbacks. `check_ptr_reg()` validates encoded register/channel fields for primary pointer access.

## Control Flow
Pointer reads and writes compose `(reg << 16) | channel`, lock `emu->emu_lock`, write the pointer port, and read/write data. Bitfield-encoded registers perform read-modify-write masks. SPI and I2C functions serialize with dedicated spinlocks and poll status bits with timeouts. FPGA writes require the E-MU 1010 mutex or acquire it through a guard helper, strobing GPIO bits to latch register/value pairs. Interrupt helpers modify INTE, voice interrupt masks, half-loop masks, and loop-stop registers. `snd_emu10k1_voice_clear_loop_stop_multiple_atomic()` carefully times low/high voice release against the hardware sample cycle.

## State and Persistence
Hardware registers are the primary state. Software state includes locks, `emu->emu1010.word_clock`, card capability flags, and firmware blob content passed to FPGA upload. Register writes persist until device reset, suspend/resume restore, or another module changes them; nothing is stored on disk.

## Dependencies and Integration Points
All higher-level EMU10K1 modules depend on this file for register access. `emupcm.c` uses pointer writes, loop-stop, and interrupt helpers; `irq.c` uses interrupt-disable and voice ack helpers; `timer.c` uses `snd_emu10k1_intr_enable/disable`; `emuproc.c` uses pointer and FPGA reads; main initialization uses FPGA firmware upload and clock update. AC97 integration is via `struct snd_ac97` bus callbacks.

## Risks
The file touches device registers directly and is highly concurrency-sensitive. Incorrect locking can corrupt the shared PTR/DATA address latch. SPI/I2C polling paths can fail or stall hardware; `snd_emu10k1_i2c_write()` has a timeout counter that is not reset per retry, so timeout behavior must be read carefully before modification. FPGA reads can trigger GPIO IRQs as a side effect. Atomic loop-stop clearing disables interrupts for short but deliberate windows and can return `-EAGAIN` when timing is disturbed. Firmware upload bit-bangs GPIO and depends on hardware wiring assumptions.

## Test Signals
Regression tests need hardware or emulation. Signals include stable AC97 codec reads/writes, no pointer-register races under concurrent PCM/MIDI/proc access, I2C/SPI timeout logging only on real failures, E-MU 1010 clock LEDs/rate selection matching input clock, and successful synchronized EFX playback starts. Lockdep and IRQ latency tracing are useful around loop-stop atomic release and FPGA access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/emu10k1/io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/emu10k1/irq.c -->
# Research: sources/distributed-fs/ceph-client/sound/pci/emu10k1/irq.c

## Purpose
`irq.c` implements the top-level shared interrupt handler for EMU10K1 cards. It reads the interrupt pending register, dispatches each recognized source to module-owned callbacks, disables sources with no registered owner, acknowledges handled bits, and protects against device-removal and interrupt-storm scenarios.

## Important APIs, Types, and Functions
The sole exported handler is `snd_emu10k1_interrupt(int irq, void *dev_id)`. It uses `struct snd_emu10k1` callback fields including `hwvol_interrupt`, `capture_interrupt`, `capture_mic_interrupt`, `capture_efx_interrupt`, `midi.interrupt`, `midi2.interrupt`, `spdif_interrupt`, `dsp_interrupt`, `p16v_interrupt`, and `gpio_interrupt`. Voice-loop interrupts are dispatched through `struct snd_emu10k1_voice::interrupt`.

## Control Flow
The handler loops while `IPR` is nonzero, bails out on all-ones status as suspected removal, and caps processing at 1000 iterations. It handles PCI errors, hardware-volume buttons, channel-loop and half-loop voice interrupts, AC97/mic/EFX capture interrupts, both MIDI ports, interval timer, S/PDIF status changes, FXDSP, P16V, and Audigy GPIO. For voice loops, it reads low/high pending masks and walks voices up to the hardware-reported maximum voice number. It acknowledges all original bits at the end of each iteration with `outl(orig_status, IPR)`.

## State and Persistence
The handler owns no long-lived state beyond local status variables. It mutates interrupt-enable masks when callbacks are absent and acknowledges pending status bits. Callback installation/removal is controlled by the modules that open/close PCM, MIDI, timer, DSP, P16V, or GPIO services.

## Dependencies and Integration Points
The handler integrates every EMU10K1 subsystem: PCM period handling in `emupcm.c`, MIDI handling in `emumpu401.c`, timer handling in `timer.c`, FXDSP interrupt hooks in FX code, P16V in `p16v.c`, GPIO/FPGA for E-MU cards, and voice interrupt helpers in `io.c`.

## Risks
Ordering matters: callbacks may free or reconfigure state while interrupts are pending, so open/close paths must disable sources before clearing pointers. Acknowledging `orig_status` clears all bits observed before dispatch, including bits that were masked from local `status`; this matches the design but should be considered before adding deferred handling. The handler can disable interrupt sources silently when callbacks are missing, which prevents storms but can hide setup bugs. Voice iteration uses `IPR_CHANNELNUMBERMASK`; invalid hardware status could cause incomplete or excessive traversal if assumptions change.

## Test Signals
Generate playback, capture, MIDI, timer, FXDSP, P16V, and GPIO interrupts and verify callbacks fire once per pending event and sources are acknowledged. Test module close while interrupts are active to ensure no stale callback dereference. PCI surprise-removal simulations should produce the removal message and no endless loop. Interrupt-storm tests should trip the 1000-iteration guard rather than hanging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/emu10k1/irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/emu10k1/memory.c -->
# Research: sources/distributed-fs/ceph-client/sound/pci/emu10k1/memory.c

## Purpose
`memory.c` manages EMU10K1 sample memory and page table mappings. It maps ALSA PCM SG buffers and synthesizer sample allocations into the chip page table (PTB), maintains page-address/pointer tables, supports LRU-style eviction of unlocked mappings, and provides synth memory memset/copy helpers.

## Important APIs, Types, and Functions
Key public functions are `snd_emu10k1_memblk_map()`, `snd_emu10k1_alloc_pages()`, `snd_emu10k1_free_pages()`, `snd_emu10k1_alloc_pages_maybe_wider()`, `snd_emu10k1_synth_alloc()`, `snd_emu10k1_synth_free()`, `snd_emu10k1_synth_memset()`, and `snd_emu10k1_synth_copy_from_user()`. Internal helpers include `emu10k1_memblk_init()`, `search_empty_map_area()`, `map_memblk()`, `unmap_memblk()`, `search_empty()`, `is_valid_page()`, `synth_alloc_pages()`, `synth_free_pages()`, and `xor_range()`.

## Control Flow
PCM allocation finds an aligned free util-mem block, fills `emu->page_addr_table[]` from ALSA SG DMA addresses or the silent page, locks the mapping, and maps it into PTB entries. Synth allocation uses `__snd_util_mem_alloc()`, allocates individual DMA pages only for newly covered page ranges, maps the block, and can later be evicted from PTB if unlocked. Mapping searches the ordered mapped list for an exact or largest suitable hole; on failure, it unmaps oldest unlocked blocks until space is sufficient. Freeing unmaps PTB entries back to the silent page, releases allocated DMA pages, and returns the util memory block.

## State and Persistence
State is in `emu->memhdr`, mapped linked lists, `mapped_page`, `map_locked`, `first_page`, `last_page`, `page_addr_table[]`, `page_ptr_table[]`, `ptb_pages.area`, and `silent_page`. This state is runtime-only and rebuilt on device initialization; hardware PTB contents persist until rewritten or reset.

## Dependencies and Integration Points
`emupcm.c` relies on this file for playback buffer addressability. Synth code uses the synth alloc/free/memset/copy APIs. It depends on ALSA util memory helpers, ALSA DMA allocation, `snd_pcm_sgbuf_get_addr()`, PCI DMA masks, and EMU page constants from `sound/emu10k1.h`.

## Risks
PTB mapping correctness is critical: page zero is reserved, page-size conversion differs when `PAGE_SIZE != EMUPAGESIZE`, and invalid DMA alignment or mask violations can make hardware fetch wrong memory. The IOMMU workaround deliberately widens allocations and must remain synchronized between allocation and free. Locked PCM mappings must not be evicted; synth mappings can be evicted and remapped. `snd_emu10k1_synth_copy_from_user()` must not trust user sizes beyond the block bounds and returns `-EFAULT` on copy failure.

## Test Signals
Exercise repeated PCM `hw_params`/`hw_free` with different buffer sizes and synth allocations that fragment PTB space. Validate silent-page remapping after free and no DMA mask/alignment warnings. Test `PAGE_SIZE` configurations larger than EMUPAGESIZE if possible. User-copy tests should cover page-boundary offsets and XOR mode. IOMMU workaround hardware should be checked for no out-of-bounds device fetches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/emu10k1/memory.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/emu10k1/p16v.c -->
# Research: sources/distributed-fs/ceph-client/sound/pci/emu10k1/p16v.c

## Purpose
`p16v.c` implements the Audigy2 P16V high-definition PCM and mixer path. It exposes one 8-channel S32_LE playback PCM, one 2-channel S32_LE capture PCM, P16V volume/source/channel mixer controls, a P16V interrupt callback installed into the main EMU interrupt handler, and suspend/resume register save/restore support.

## Important APIs, Types, and Functions
Public entry points are `snd_p16v_pcm()`, `snd_p16v_mixer()`, and, under PM sleep, `snd_p16v_alloc_pm_buffer()`, `snd_p16v_free_pm_buffer()`, `snd_p16v_suspend()`, and `snd_p16v_resume()`. PCM operations include `snd_p16v_pcm_open_*`, `snd_p16v_pcm_prepare_playback()`, `snd_p16v_pcm_prepare_capture()`, triggers, and pointers. Mixer controls use `snd_p16v_volume_*`, `snd_p16v_capture_source_*`, and `snd_p16v_capture_channel_*`. `snd_p16v_interrupt()` is called from `irq.c` through `emu->p16v_interrupt`.

## Control Flow
`snd_p16v_pcm()` creates the ALSA PCM, installs playback/capture ops, preallocates managed DMA buffers, records the device offset, and registers the P16V IRQ callback. Playback prepare programs SPDIF/SRC rate fields, writes a per-period DMA descriptor table into `emu->p16v_buffer`, and configures PTR2 playback list and FIFO registers. Capture prepare selects the capture rate and programs capture DMA base, buffer size, and pointer registers. Triggers set `runtime->private_data` as a running flag, manipulate `BASIC_INTERRUPT`, and enable/disable INTE2 bits. Pointer callbacks read P16V list/pointer registers and convert byte positions to ALSA frames.

## State and Persistence
Runtime state includes `emu->pcm_p16v`, `emu->p16v_device_offset`, `emu->p16v_capture_source`, `emu->p16v_capture_channel`, `runtime->private_data` running flags, and the DMA descriptor table in `emu->p16v_buffer`. Mixer writes persist in P16V PTR2 registers. PM support saves the first channel's 0x80 PTR2 registers into `emu->p16v_saved` and restores them on resume.

## Dependencies and Integration Points
The file depends on `p16v.h` register definitions, `snd_emu10k1_ptr_read/write()` for Audigy sample-rate registers, `snd_emu10k1_ptr20_read/write()` for P16V registers, ALSA PCM/control/TLV helpers, and the main EMU IRQ path. It shares INTE2/IPR2 with `irq.c`, which treats `IPR_P16V` as a nested interrupt source.

## Risks
The code comments identify historical unload stability issues. It only practically uses channel 0 for capture and interrupt handling despite hardware supporting more channels. Playback trigger computes the channel from the original substream inside a grouped trigger loop, so changes to multi-device grouping need care. The prepare path has FIXME comments about checking `emu->p16v_buffer` size before writing descriptor tables. P16V register documentation is partly reverse-engineered; writing invalid values, especially to `BASIC_INTERRUPT`, can hang hardware according to `p16v.h`.

## Test Signals
Test 44.1, 48, 96, and 192 kHz playback/capture, period counts 2-8, and period-size integer constraints. Verify P16V INTE2/IPR2 interrupts produce exactly one ALSA period event per period and stop cleanly. Mixer tests should confirm volume inversion, capture source routing, and capture channel updates in hardware registers. PM testing should suspend/resume during idle and after PCM setup, checking restored registers and no IRQ floods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/emu10k1/p16v.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/emu10k1/p16v.h -->
# Research: sources/distributed-fs/ceph-client/sound/pci/emu10k1/p16v.h

## Purpose
`p16v.h` documents the Audigy2 P16V PTR2/DATA2 register map used by `p16v.c` and diagnostics. It defines playback/capture DMA registers, interrupt/start bits, SRC/mixer routing, volume registers, output enables, S/PDIF controls, and capture-rate/status fields.

## Important APIs, Types, and Functions
The file is macro-only. Important definitions include `PLAYBACK_LIST_ADDR`, `PLAYBACK_LIST_SIZE`, `PLAYBACK_LIST_PTR`, `PLAYBACK_DMA_ADDR`, `PLAYBACK_POINTER`, capture equivalents such as `CAPTURE_DMA_ADDR`, `CAPTURE_BUFFER_SIZE`, `CAPTURE_POINTER`, `CAPTURE_P16V_SOURCE`, `CAPTURE_RATE_STATUS`, `BASIC_INTERRUPT`, `SRCSel`, `PLAYBACK_VOLUME_MIXER*`, `SRC48_ENABLE`, `SRCMULTI_ENABLE`, `AUDIO_OUT_ENABLE`, and S/PDIF user/status registers.

## Control Flow
There is no executable flow in the header. The register constants drive control flow in `p16v.c`: prepare writes descriptor-list and DMA registers, trigger modifies `BASIC_INTERRUPT`, pointer reads list/pointer registers, mixer controls read/write volume and capture routing registers, and proc code reads `CAPTURE_RATE_STATUS`.

## State and Persistence
The macros name hardware state stored inside the P16V register bank. Values persist in the device until reset or rewritten. Comments encode discovered defaults, bit meanings, and hazardous values such as `BASIC_INTERRUPT` writes that can hang the PC.

## Dependencies and Integration Points
Included by `p16v.c` and `emuproc.c`; accessed through `snd_emu10k1_ptr20_read/write()` in `io.c`. It complements `p17v.h`, which defines related CA0108/P17V registers and I2C/SPI constants.

## Risks
The map is partly reverse-engineered, with unknown and unused ranges. Several comments state that all-ones writes clamp, pause, fail IRQs, or hang hardware. Typos such as `CAPURE_SPDIF_USER_DATA*` are ABI-internal macro names but should not be casually renamed without checking users. Any change to bit meanings can break DMA start/stop, routing, or mixer controls.

## Test Signals
Build coverage should confirm every macro consumer still compiles. Runtime validation consists of checking P16V playback/capture DMA setup, `BASIC_INTERRUPT` start/stop behavior, mixer volume routing, capture-source selection, and proc capture-rate output against known hardware behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/emu10k1/p16v.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/emu10k1/p17v.h -->
# Research: sources/distributed-fs/ceph-client/sound/pci/emu10k1/p17v.h

## Purpose
`p17v.h` defines PTR2/DATA2 register constants for Audigy2 Value Tina/P17V/CA0108-style hardware, especially SPI and I2C access to external codecs and P17V mixer/capture registers. `io.c` uses these definitions for SPI/I2C transactions, and other CA0108/P17V paths use the register names for routing and mixer setup.

## Important APIs, Types, and Functions
The file is macro-only. It defines FIFO pointer registers, playback channel/slot selection, SPI register `P17V_SPI`, I2C address/data registers `P17V_I2C_ADDR`, `P17V_I2C_0`, `P17V_I2C_1`, I2C bit masks and commands, ADC register addresses such as `ADC_TIMEOUT`, `ADC_IFC_CTRL`, `ADC_POWER`, `ADC_ATTEN_*`, `ADC_MUX`, mux bits, P17V start/capture FIFO registers, mixer volume registers, output enables, master volumes, sample-rate estimation registers, and bypass/source selection registers.

## Control Flow
The header has no execution. Its constants parameterize `snd_emu10k1_spi_write()` and `snd_emu10k1_i2c_write()` in `io.c`: SPI writes pulse `P17V_SPI`; I2C writes program `P17V_I2C_1`, trigger `P17V_I2C_ADDR`, poll `I2C_A_ADC_START`, and check `I2C_A_ADC_ABORT`. Other driver paths can use the mixer and capture constants when programming P17V audio routing.

## State and Persistence
The named registers are device-resident runtime state. Codec I2C settings alter external ADC behavior until reset or overwritten. No software persistence is defined in the header.

## Dependencies and Integration Points
Included directly by `io.c`. It aligns with CA0108 capability checks such as `emu->card_capabilities->ca0108_chip` and related mixer/register setup outside this work item.

## Risks
I2C/SPI timing and bit definitions are hardware-sensitive; incorrect values can leave codec transactions aborted or stuck. Several ADC gain/mute definitions are disabled under `#if 0` as untested, indicating incomplete validation. The comments use reverse-engineered names and unknown ranges, so adding consumers should be backed by hardware tests.

## Test Signals
Compile should catch macro drift in `io.c`. Runtime tests should verify SPI writes complete within timeout on CA0108 chips, I2C ADC writes return zero and do not log abort/timeouts, ADC mux selection works for mic/line inputs, and capture/playback FIFO pointer reads are plausible during active streams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/emu10k1/p17v.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/emu10k1/timer.c -->
# Research: sources/distributed-fs/ceph-client/sound/pci/emu10k1/timer.c

## Purpose
`timer.c` exposes the EMU10K1 hardware interval timer as an ALSA card timer. It programs the chip `TIMER` register, enables/disables interval timer interrupts, and reports sample-clock-derived timer resolution.

## Important APIs, Types, and Functions
The public constructor is `snd_emu10k1_timer(struct snd_emu10k1 *emu, int device)`. ALSA timer callbacks are `snd_emu10k1_timer_start()`, `snd_emu10k1_timer_stop()`, `snd_emu10k1_timer_c_resolution()`, and `snd_emu10k1_timer_precise_resolution()`, grouped in `snd_emu10k1_timer_hw`.

## Control Flow
Timer creation fills a `struct snd_timer_id`, calls `snd_timer_new()`, names the timer, stores `emu` in `timer->private_data`, and assigns hardware callbacks. Start converts `timer->sticks` to a delay, clamps the minimum to five ticks, enables `INTE_INTERVALTIMERENB`, and writes the delay to the hardware timer register. Stop disables the interval timer interrupt. `irq.c` turns `IPR_INTERVALTIMER` into `snd_timer_interrupt(emu->timer, emu->timer->sticks)`.

## State and Persistence
State is limited to `emu->timer`, the hardware timer register, and INTE interrupt enable bit. Resolution depends on current E-MU word clock for E-MU models and defaults to 48 kHz otherwise. No durable state is persisted.

## Dependencies and Integration Points
It depends on ALSA timer APIs, EMU register definitions, `snd_emu10k1_intr_enable/disable()` from `io.c`, and interrupt dispatch in `irq.c`. E-MU clock state comes from `emu->emu1010.word_clock`.

## Risks
Resolution must match the active sample clock; incorrect word-clock updates will make ALSA timer clients drift. The minimum delay clamp protects hardware but changes requested small periods. Start enables interrupts before writing the timer register, so ordering should not be changed without checking pending interrupt behavior.

## Test Signals
Create the card timer and verify it appears with 1024 ticks and expected resolution at 44.1 kHz and 48 kHz. Run timer clients while changing E-MU word clock and confirm reported precise resolution updates. Check start/stop does not leave `INTE_INTERVALTIMERENB` set after close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/emu10k1/timer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/emu10k1/tina2.h -->
# Research: sources/distributed-fs/ceph-client/sound/pci/emu10k1/tina2.h

## Purpose
`tina2.h` is a tiny register-constant header for the Tina2 codec/control block used by some E-MU hardware paths. It currently defines only `TINA2_VOLUME`, described as an attenuation register to prevent playback distortion.

## Important APIs, Types, and Functions
The only functional definition is `#define TINA2_VOLUME 0x71`. The file has a GPL-2.0-or-later SPDX tag and attribution comments. There are no functions or types.

## Control Flow
There is no executable control flow. Consumers include this constant when programming Tina2 volume/attenuation through the surrounding EMU 1010/FPGA or codec routing code.

## State and Persistence
The header does not store state. The macro names a hardware register or control index whose value persists in device hardware until reset or rewritten by the driver.

## Dependencies and Integration Points
This file is intended for EMU10K1/E-MU model code that needs Tina2-specific constants. It should be kept aligned with E-MU FPGA routing and mixer initialization code.

## Risks
Because the file is minimal, the main risk is semantic ambiguity: `0x71` must remain tied to the correct Tina2 register. Renaming, moving, or reusing it without checking hardware documentation can cause incorrect attenuation or distorted playback.

## Test Signals
Build tests should confirm any Tina2 consumers include the header correctly. Hardware tests should verify that writing the associated volume value attenuates playback as expected and does not affect unrelated routes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/emu10k1/tina2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/emu10k1/voice.c -->
# Research: sources/distributed-fs/ceph-client/sound/pci/emu10k1/voice.c

## Purpose
`voice.c` implements the EMU10K1 voice allocator. Voices are hardware playback/effect/synth channels; the allocator gives PCM, EFX, and synth code contiguous voice groups with correct stereo alignment and frees them safely.

## Important APIs, Types, and Functions
Public APIs are `snd_emu10k1_voice_alloc()` and `snd_emu10k1_voice_free()`. Internal helpers are `voice_alloc()` and `voice_free()`. Allocation operates on `emu->voices[]`, `emu->next_free_voice`, `struct snd_emu10k1_voice` fields `use`, `epcm`, `last`, `dirty`, `interrupt`, and optional synth reclamation callback `emu->get_synth_voice`.

## Control Flow
Allocation validates arguments, locks `emu->voice_lock`, and repeatedly calls `voice_alloc()` until the requested number of channel groups is obtained. `voice_alloc()` starts at `emu->next_free_voice`, scans round-robin across `NUM_G`, enforces even starting voices for multi-voice/stereo groups, skips used ranges efficiently, marks each voice with the requested type and `epcm`, marks the last voice in the group, and advances `next_free_voice`. If allocation fails for non-synth clients and `get_synth_voice` is available, it reclaims one synth voice and retries. Partial allocations are rolled back on failure. Freeing walks from the first voice until the `last` marker, resets dirty hardware voices through `snd_emu10k1_voice_init()`, and clears software fields.

## State and Persistence
Voice allocation state is runtime-only in `emu->voices[]` and `emu->next_free_voice`. Dirty voices reflect hardware register programming that must be reset before reuse. No persistent storage is used.

## Dependencies and Integration Points
`emupcm.c`, FX, and synth code allocate voices through this file. `irq.c` reads voice `use` and `interrupt` fields while dispatching loop interrupts. Hardware reset on dirty free depends on `snd_emu10k1_voice_init()` from main initialization code. Synth reclamation uses `emu->get_synth_voice`.

## Risks
The allocator returns `-ENOMEM` for busy voice pools, and callers must unwind cleanly. Stereo alignment is essential; changing scan behavior can break hardware assumptions. The `last` marker defines group length during free, so any corruption can over-free adjacent voices. Free must clear interrupt callbacks before reuse to avoid stale IRQ calls.

## Test Signals
Allocate/free mono, stereo, multi-channel EFX, and synth voices until exhaustion. Verify stereo groups start on even voice numbers, round-robin allocation advances, failed multi-group allocations roll back all partial state, dirty voices are reinitialized, and IRQ dispatch never calls freed voice callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/emu10k1/voice.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ens1370.c -->
# Research: sources/distributed-fs/ceph-client/sound/pci/ens1370.c

## Purpose
`ens1370.c` is the shared ALSA PCI driver source for Ensoniq AudioPCI ES1370 and, when compiled with `CHIP1371`, ES1371/ES1373/CT5880/EV1938 variants. It implements PCI probe, chip initialization, PCM playback/capture, codec/mixer setup, MIDI UART, gameport support, proc diagnostics, IRQ handling, and suspend/resume.

## Important APIs, Types, and Functions
The central state type is `struct ensoniq`, holding locks, I/O port, cached control registers, codec-specific state, PCM and MIDI objects, active substreams, DMA sizes, SPDIF fields, and optional gameport. Public registration is through `module_pci_driver(ens137x_driver)`. Major functions include `snd_ensoniq_create()`, `snd_ensoniq_chip_init()`, `snd_ensoniq_pcm()`, `snd_ensoniq_pcm2()`, `snd_ensoniq_trigger()`, prepare/pointer/open/close callbacks, codec helpers, mixer constructors, MIDI operations, `snd_audiopci_interrupt()`, and PM callbacks.

## Control Flow
Probe allocates a managed ALSA card, enables PCI, requests regions/IRQ, initializes cached registers, programs the chip, creates proc info, constructs the codec mixer, registers two PCM devices and raw MIDI, optionally creates a gameport, names the card, and registers it. PCM open records active substreams and applies rate constraints. Prepare disables the stream, writes DMA frame/size and sample-count registers, configures serial format and interrupt bits, then programs ES1370 fixed clock divisors or ES1371 SRC rates. Trigger starts/stops grouped streams by toggling `ES_DAC1_EN`, `ES_DAC2_EN`, or `ES_ADC_EN`; pause toggles serial pause bits. IRQ temporarily masks serial interrupt bits, restores them, then calls MIDI and PCM period handlers.

## State and Persistence
Runtime state is cached in `ensoniq->ctrl`, `sctrl`, `cssr`, `uartc`, `uartm`, active substream pointers, DMA/period sizes, codec mixer state, SPDIF default/stream status, joystick/gameport state, and hardware registers. ALSA controls persist only for the life of the driver instance; suspend/resume reinitializes hardware and resumes codec state.

## Dependencies and Integration Points
The ES1370 build uses AK4531 codec support; ES1371 uses AC97 codec support and SRC programming. Both use ALSA PCM/rawmidi/control/proc APIs, PCI managed resources, optional Linux gameport support, and direct I/O register access. The source is also included by `ens1371.c` after defining `CHIP1371`, making preprocessor conditionals part of the design.

## Risks
The shared-source/preprocessor design means edits can affect both chip families differently. ES1371 SRC/codec access requires strict timing and mutex serialization; comments warn that enabling SRC before programming can lock up the chip until power cycle. IRQ handling depends on cached `sctrl` restoration to retrigger future periods. ES1370 playback2 and capture share a clock divisor lock, so close paths must release `pclkdiv_lock`. SPDIF, rear-output, line-in routing, and amplifier quirks are revision/subsystem-specific. MIDI and PCM share `reg_lock`; callback ordering must avoid stale substream access.

## Test Signals
Build both ES1370 and ES1371 configurations. On ES1370, test fixed DAC1 rates, variable DAC2/capture rates, AK4531 controls, and clock-lock release. On ES1371, test AC97 read/write, SRC rates 4-48 kHz, SPDIF controls, rear/line quirks, and suspend/resume. Common tests include simultaneous DAC1/DAC2/capture grouped trigger, period interrupt cadence, MIDI duplex transfer, gameport enable/disable, proc output, and clean module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ens1370.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ens1371.c -->
# Research: sources/distributed-fs/ceph-client/sound/pci/ens1371.c

## Purpose
`ens1371.c` is a compile-time wrapper that builds the shared Ensoniq AudioPCI driver as the ES1371-family variant. It defines `CHIP1371` and includes `ens1370.c`, activating the ES1371/ES1373/CT5880/EV1938 code paths in that file.

## Important APIs, Types, and Functions
The wrapper declares no functions or types of its own. Its effective APIs are all `CHIP1371` branches from `ens1370.c`: AC97 codec access, ES1371 SRC programming, ES1371 PCI ID table entries, SPDIF/line/rear controls, joystick-port parameter handling, amplifier/reset quirks, and the `ENS1371` module metadata.

## Control Flow
Compilation enters `ens1370.c` with `CHIP1371` already defined. That selects `DRIVER_NAME "ENS1371"`, `CHIP_NAME "ES1371"`, AC97 instead of AK4531, ES1371 sample-rate converter functions, ES1371-specific mixer controls, and ES1371 PCI IDs. Runtime flow is therefore the same as the ES1371 path described in the shared source report.

## State and Persistence
The wrapper has no state. Runtime state is `struct ensoniq` from the included source, with ES1371-specific fields such as `u.es1371.ac97`, `spdif`, `spdif_default`, `spdif_stream`, and ES1371 control/status register cache values.

## Dependencies and Integration Points
It depends entirely on `ens1370.c` being preprocessor-safe for inclusion under `CHIP1371`. Build-system integration must compile `ens1370.c` and `ens1371.c` as separate translation units for their respective chip families.

## Risks
Because this file includes a `.c` file, static symbols are duplicated in separate builds by design. Any include-order change, new global without appropriate `#ifdef`, or assumption that `ens1370.c` is only compiled directly can break the ES1371 module. The tiny wrapper can look empty in code search, so maintainers must inspect the included source for real behavior.

## Test Signals
The primary test is successful ES1371-module compilation and module metadata/PIC IDs matching ES1371-family devices. Runtime tests are those for the `CHIP1371` path in `ens1370.c`: AC97, SRC, SPDIF, MIDI, PCM, PM, and quirks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ens1371.c -->
