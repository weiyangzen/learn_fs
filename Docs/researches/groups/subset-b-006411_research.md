# subset-b-006411 Research

Grouped research for ALSA PCI and PCMCIA driver sources under `sources/distributed-fs/ceph-client/sound`. Each section preserves the source path and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/via82xx.c -->
# sources/distributed-fs/ceph-client/sound/pci/via82xx.c

Purpose: Implements the ALSA PCI driver for VIA VT82C686 and VT8233-family AC97 audio controllers. It binds PCI IDs `PCI_DEVICE_ID_VIA_82C686_5` and `PCI_DEVICE_ID_VIA_8233_5`, creates ALSA cards/PCM devices, exposes AC97 mixer access, optional MPU-401/gameport support for VIA686, VIA8233 DXS and multichannel playback, capture, SPDIF routing, proc register dumps, and suspend/resume behavior.

Important APIs/types/functions: `struct via82xx` is the persistent chip object stored as `card->private_data`; it tracks PCI resources, AC97 bus/codec, per-stream `struct viadev` objects, rate locks, DXS/SPDIF flags, saved PCI/config state, and optional gameport/rawmidi. `build_via_table()` and `clean_via_table()` allocate/free the scatter-gather descriptor table and `idx_table` used by pointer calculation. AC97 bus callbacks are `snd_via82xx_codec_write()`, `snd_via82xx_codec_read()`, and `snd_via82xx_codec_wait()`. PCM callbacks are split between VIA686 and VIA8233 variants: prepare functions program rates, table pointers, format bits, DXS volumes, multichannel slot maps, and capture FIFO state; `snd_via82xx_pcm_trigger()` starts, pauses, or terminates the hardware channel; pointer callbacks recover from several known bogus count/index values. Probe flows through `snd_via82xx_probe()` -> `__snd_via82xx_probe()` -> `snd_via82xx_create()`, mixer creation, PCM creation, chip-specific misc controls, reset of all channels, proc setup, and `snd_card_register()`.

Control flow: Hardware initialization enables the PCI device, requests regions and IRQ, saves legacy config, resets ACLink if needed, waits for the primary codec, applies VIA8233 MC97 and DXS workarounds, initializes playback volume registers, and sets PCI bus mastering. Interrupt flow reads `VIA_REG_SGD_SHADOW`, checks `chip->intr_mask`, scans active `viadev` entries, updates `hwptr_done` on period/end-of-list status, temporarily drops `reg_lock` around `snd_pcm_period_elapsed()`, and acknowledges channel status. PCM open increments a direction-specific rate lock and adapts runtime constraints for SPDIF, fixed DXS, DXS SRC, or current shared AC97 rate. Close decrements the rate lock and powers down AC97 DAC/ADC rates when no stream uses that direction.

State and persistence: Persistent state lives in `struct via82xx` for the ALSA card lifetime. Runtime stream state lives in `struct viadev` and includes DMA table memory, last valid pointer, fragment/buffer sizes, interrupt status, and running flag. Suspend resets channels, suspends AC97, and saves VIA8233 SPDIF/capture-source registers; resume reinitializes the chip, restores legacy/SPDIF/capture source state, resumes AC97, resets channels, and returns the card to D0. Free restores VIA686 legacy registers and unregisters gameport.

Dependencies/integration: Depends on Linux PCI, IO port accessors, IRQs, ALSA core/PCM/info/tlv/ac97/mpu401, optional gameport, and AC97 codec quirks. It integrates with ALSA via `snd_devm_card_new`, `snd_pcm_new`, PCM ops, AC97 bus/mixer, mixer controls, rawmidi MPU401, chmaps, procfs, PM ops, and `module_pci_driver`.

Risks: The driver relies on hardware-specific timing (`udelay`, `msleep(500)` unless `nodelay`) and undocumented reset/control bits. Pointer calculation has many chip errata workarounds and can regress period accounting if descriptor size/count/index handling changes. Rate locking can reject concurrent playback/capture rates, so tests need multi-stream cases. DXS support is quirk-driven and may break specific boards. IRQ handlers drop and reacquire locks around ALSA callbacks, making ordering and stale substream state important. Legacy MIDI/gameport configuration must be restored on teardown.

Test signals: Build with `CONFIG_SND_VIA82XX`, probe supported PCI IDs, verify `aplay`/`arecord` on VIA686 and VIA8233 modes, run simultaneous DSX streams, multichannel playback, capture from both sources where available, SPDIF DXS3 switch/rate filtering, suspend/resume playback recovery, AC97 mixer controls and quirks, proc `via82xx` register dump presence, and interrupt/pointer stability under small periods and buffer wrap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/via82xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/via82xx_modem.c -->
# sources/distributed-fs/ceph-client/sound/pci/via82xx_modem.c

Purpose: Implements the ALSA modem-class driver for VIA VT82xx MC97/AC97 modem function `0x1106:0x3068`. It is derived from the VIA audio driver but exposes a narrow mono modem PCM device, modem AC97 mixer access, MC97 codec selection, proc register dump, and PM hooks.

Important APIs/types/functions: `struct via82xx_modem` stores PCI/card resources, SGD interrupt mask, two `viadev` streams, AC97 bus/codec, selected secondary codec state, and `reg_lock`. `build_via_table()` builds 255-entry descriptor tables for the modem input/output channels and `clean_via_table()` releases them. `snd_via82xx_codec_write()` and `snd_via82xx_codec_read()` implement AC97 bus access, with special handling for `AC97_GPIO_STATUS` through `VIA_REG_GPI_STATUS`. `snd_via82xx_pcm_trigger()`, `snd_via686_pcm_pointer()`, `snd_via82xx_hw_params()`, and `snd_via82xx_pcm_prepare()` are the modem PCM callbacks. `snd_via686_pcm_new()` creates one `SNDRV_PCM_CLASS_MODEM` PCM with one playback and one capture stream.

Control flow: Probe allocates an ALSA card, initializes PCI resources and IRQ in `snd_via82xx_create()`, initializes MC97/ACLink in `snd_via82xx_chip_init()`, detects secondary codec validity, creates an AC97 mixer with `AC97_SCAP_SKIP_AUDIO`, creates the modem PCM, resets both channels, registers a proc entry, then registers the card. PCM open constrains rates to 8000, 9600, 12000, and 16000 Hz and integer periods. HW params build the descriptor table and write modem line rate/level registers. Prepare resets the selected channel, programs the descriptor base, and enables autostart/EOL/flag interrupts. The IRQ handler reads `VIA_REG_SGD_SHADOW`, checks modem read/write bits, scans the two channels, calls `snd_pcm_period_elapsed()` for running substreams, and acknowledges status.

State and persistence: Persistent device state is `struct via82xx_modem`; per-stream state is `struct viadev` with descriptor memory, stream pointer, running flag, last position, and buffer metadata. AC97 bus/codec pointers are nulled through private free callbacks. Suspend resets all channels and suspends AC97; resume reinitializes MC97/ACLink, resumes AC97, resets channels, and restores card power state. Teardown resets channels and releases managed PCI/IRQ resources through devres/card cleanup.

Dependencies/integration: Uses Linux PCI, IRQ, IO ports, ALSA core/PCM/info/ac97/initval, and PC-style port access. ALSA integration is via modem-class PCM, AC97 bus/mixer, procfs, PM ops, and `module_pci_driver`.

Risks: The trigger callback treats `SNDRV_PCM_TRIGGER_SUSPEND` like START, which is surprising and should be preserved only if intentional for this legacy driver. Descriptor splitting uses page-size calculations rather than `snd_pcm_sgbuf_get_chunk_size()` used in the audio driver, so scatterlist changes need scrutiny. AC97 secondary codec detection is timing-sensitive. Pointer recovery is less robust than the audio driver and depends on last valid position. IRQ handling is shared and must avoid false positives on non-modem VIA SGD bits.

Test signals: Build with `CONFIG_SND_VIA82XX_MODEM`, probe the MC97 PCI function, verify ALSA modem PCM class and mono rate constraints, exercise playback/capture at all supported rates, check AC97 modem controls and GPIO-status write behavior, inspect proc `via82xx`, test suspend/resume, and run with shared IRQ activity to ensure no spurious handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/via82xx_modem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/vx222/Makefile -->
# sources/distributed-fs/ceph-client/sound/pci/vx222/Makefile

Purpose: Defines the ALSA build recipe for the Digigram VX222 PCI driver module. The module object `snd-vx222.o` is composed from `vx222.o` and `vx222_ops.o`, and is built when `CONFIG_SND_VX222` is enabled.

Important APIs/types/functions: This file does not define runtime APIs; it establishes the compilation unit boundary that links the PCI probe/PM code in `vx222.c` with the low-level board operation table in `vx222_ops.c`.

Control flow: Kbuild uses `snd-vx222-y := vx222.o vx222_ops.o` to aggregate objects, then `obj-$(CONFIG_SND_VX222) += snd-vx222.o` to conditionally include the module in the sound PCI build.

State and persistence: No runtime state. Build state is controlled by Kconfig selection and Kbuild object composition.

Dependencies/integration: Integrates with the ALSA PCI build and the shared VX core library included by the C files through `<sound/vx_core.h>`.

Risks: Adding a new VX222 source file without updating this object list would silently omit code. Removing either object breaks driver registration or hardware operations.

Test signals: Kernel build with `CONFIG_SND_VX222=m` should emit `snd-vx222.ko` containing symbols from both source objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/vx222/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/vx222/vx222.c -->
# sources/distributed-fs/ceph-client/sound/pci/vx222/vx222.c

Purpose: Provides the PCI-facing ALSA driver for Digigram VX222 old, VX222 v2, and VX222 Mic cards. It selects hardware capability descriptors, allocates a VX core-backed card object, maps PLX/DSP IO ports, installs the shared VX IRQ handlers, loads firmware through the VX core, and registers PM callbacks.

Important APIs/types/functions: Module parameters are card arrays `index`, `id`, `enable`, plus `mic` hardware selection and capture `ibl`. `snd_vx222_ids[]` distinguishes old PLX9050 and newer PLX9030 designs. `vx222_old_hw`, `vx222_v2_hw`, and `vx222_mic_hw` describe VX core hardware capabilities, analog IO counts, type, output level maxima, and TLV scales. `snd_vx222_create()` enables the PCI device, sets bus mastering, selects `vx222_old_ops` or `vx222_ops`, calls `snd_vx_create()`, requests regions, records BAR1/BAR2 IO ports, and requests threaded IRQ handlers. `snd_vx222_probe()` chooses the hardware descriptor, calls create, sets IBL, configures firmware device pointer, runs `snd_vx_setup_firmware()`, and registers the card.

Control flow: Probe is gated by the static `dev` index and `enable[dev]`. Old hardware uses `VX_TYPE_BOARD` and `vx222_old_ops`; new hardware selects Mic or v2 based on module parameter. Card longname is generated from the two IO ports and IRQ. Firmware setup must complete before `snd_card_register()`. Suspend/resume delegate to `snd_vx_suspend()` and `snd_vx_resume()` on the embedded `vx_core`.

State and persistence: Runtime state lives in `struct snd_vx222` embedded in the VX core allocation. This file initializes PCI pointer, IO ports, IRQ, core IBL size, and card private data. Firmware-loaded DSP/core state is owned by the VX library and operation callbacks. PM state is handled by the VX core rather than local register save arrays.

Dependencies/integration: Depends on Linux PCI/IRQ/module support, ALSA core/initval/TLV, `vx222.h`, and the shared VX core library. It integrates with devres-managed PCI regions, threaded IRQs (`snd_vx_irq_handler` and `snd_vx_threaded_irq_handler`), VX firmware loading, and `module_pci_driver`.

Risks: The static `dev` index is monotonically incremented, so failed probes after some operations can affect later card parameter indexing. BAR assumptions are fixed to resources 1 and 2. Firmware setup is mandatory; missing VX firmware prevents registration. Mic hardware selection is module-parameter based for the same PCI ID and must match physical board variant.

Test signals: Build `snd-vx222`, probe old and new PCI IDs, verify correct card name/type for `mic=0/1`, confirm firmware loading and threaded IRQ registration, test suspend/resume through VX core, and validate ALSA controls/PCM supplied by the VX library.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/vx222/vx222.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/vx222/vx222.h -->
# sources/distributed-fs/ceph-client/sound/pci/vx222/vx222.h

Purpose: Declares the VX222-specific chip wrapper, exported operation tables, and register/bit definitions used by the Digigram VX222 PCI driver.

Important APIs/types/functions: `struct snd_vx222` embeds `struct vx_core`, then adds PCI pointer, two IO port bases, cached `regCDSP`, `regCFG`, and `regSELMIC` register values, and Mic-board input/mic levels. `to_vx222()` converts a `vx_core` pointer back to the containing VX222 object. `VX2_AKM_LEVEL_MAX` defines the AKM gain lookup range. `vx222_ops` and `vx222_old_ops` are external `struct snd_vx_ops` instances implemented in `vx222_ops.c`.

Control flow: No executable control flow, but the definitions shape all low-level access: register constants identify DSP/PLX offsets, interrupt-enable bits, codec/DSP reset bits, GPIO masks, clock/data source selection bits, status bits, and Mic input selector fields. The C files use cached register fields from this header to perform read-modify-write operations without rereading every hardware register.

State and persistence: The header defines persistent per-card software mirrors (`regCDSP`, `regCFG`, `regSELMIC`, input levels) that survive across operation callbacks for the card lifetime and are re-applied during resets or mixer control changes.

Dependencies/integration: Depends on `<sound/vx_core.h>` and is included by both `vx222.c` and `vx222_ops.c`. It is the contract between the PCI wrapper and VX core operation implementation.

Risks: Register bit definitions are hardware contracts; incorrect masks can reset DSP/codec, disable IRQs, or misroute digital/analog input. The cached register model requires all writers to update the mirror before writing hardware. Mic selector bit definitions combine input mode, preamp, compression, threshold, and phantom power; mixing these incorrectly can produce audible or electrical side effects.

Test signals: Compile both VX222 objects, exercise reset, IRQ, clock source, audio source, AKM level, and Mic capture controls to validate that the header constants match observed hardware behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/vx222/vx222.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/vx222/vx222_ops.c -->
# sources/distributed-fs/ceph-client/sound/pci/vx222/vx222_ops.c

Purpose: Implements VX222 low-level hardware operations consumed by the shared VX core: register IO, DSP/Xilinx loading, pseudo-DMA transfer, IRQ acknowledge/enable, codec reset and gain programming, clock/audio source selection, board reset, and Mic-specific controls.

Important APIs/types/functions: `vx2_reg_offset[]` and `vx2_reg_index[]` map VX core register enums to PLX or DSP IO windows. `vx2_inb/outb/inl/outl()` implement IO access. `vx2_reset_dsp()`, `vx2_test_xilinx()`, `vx2_load_xilinx_binary()`, and `vx2_load_dsp()` cover firmware stages. `vx2_dma_write()` and `vx2_dma_read()` stream PCM data through pseudo-DMA using `VX_DMA` and maintain `pipe->hw_ptr` with buffer wrap. `vx2_test_and_ack()` validates/acknowledges memory IRQs. `vx2_validate_irq()` toggles PLX PCI interrupt and CDSP IRQ bits. `vx2_write_akm()`, `vx2_old_write_codec_bit()`, and `vx2_reset_codec()` program codecs. Mic controls use `vx_input_level_*`, `vx_mic_level_*`, and `vx2_set_input_level()`. Operation tables `vx222_ops` and `vx222_old_ops` expose callbacks to `snd_vx_create()`.

Control flow: Firmware load stage 1 resets and serial-loads the Xilinx image bit-by-bit via PLX control/GPIO lines, then tests it; stage 2 boots the DSP; stage 3 loads the DSP image. During PCM transfer, pseudo-DMA enables host request mode, copies 32-bit words to/from the DMA register with wrap handling, then disables request mode. IRQ handling first checks that Xilinx is loaded and that `VX_STATUS_MEMIRQ_MASK` is set, then pulses acknowledge bits. Codec reset toggles DSP/codec reset lines and, for AKM hardware, powers and mutes/unmutes DAC/ADC state; Mic boards additionally initialize SELMIC.

State and persistence: Uses `struct snd_vx222` cached registers for CDSP/CFG/SELMIC and mixer levels. Mic capture and mic gains are persistent ALSA control state, protected by the VX core `mixer_mutex`. DMA pointer state is held in VX core pipe structures. Firmware-loaded FPGA/DSP state is reflected in VX core chip status.

Dependencies/integration: Depends on Linux firmware, delays, IO ports, mutexes, ALSA core/control/TLV, VX core callback contracts, and `vx222.h`. It integrates with shared VX firmware and PCM code via `struct snd_vx_ops`.

Risks: Xilinx bitstream loading is timing-sensitive and uses `cond_resched()` inside a large loop. Pseudo-DMA requires 4-byte counts and correct wrap math. `vx2_validate_irq()` must keep PLX and CDSP interrupt bits synchronized. AKM gain mapping uses a fixed lookup table and bounds checks; off-by-one changes can mute or overdrive output. Mic preamp calculation assumes a fixed encoded dB model. Old and new board operation tables differ in codec programming callback.

Test signals: Validate Xilinx/DSP firmware load on old and new boards, confirm IRQ ack path, run playback/capture with buffer wrap, test analog/digital source and clock selection, verify AKM output levels and Mic capture/mic volume controls, and suspend/resume through VX core with IRQ revalidation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/vx222/vx222_ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ymfpci/Makefile -->
# sources/distributed-fs/ceph-client/sound/pci/ymfpci/Makefile

Purpose: Defines the Kbuild composition for the Yamaha DS-1/YMFPCI ALSA module. `snd-ymfpci.o` is linked from `ymfpci.o` and `ymfpci_main.o`, and included when `CONFIG_SND_YMFPCI` is enabled.

Important APIs/types/functions: No runtime APIs are declared. The build contract links the PCI probe/legacy-resource wrapper in `ymfpci.c` with the hardware, PCM, mixer, timer, firmware, IRQ, and PM implementation in `ymfpci_main.c`.

Control flow: Kbuild aggregates objects through `snd-ymfpci-y := ymfpci.o ymfpci_main.o`; `obj-$(CONFIG_SND_YMFPCI)` controls conditional module inclusion.

State and persistence: No runtime state. Build output depends on Kconfig.

Dependencies/integration: Integrates into ALSA PCI build and expects both C objects to share `ymfpci.h`.

Risks: Missing either object causes unresolved symbols or an incomplete driver. Any new companion object must be added here.

Test signals: Kernel build with `CONFIG_SND_YMFPCI=m` should produce `snd-ymfpci.ko` with PCI registration and exported helper symbols resolved.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ymfpci/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ymfpci/ymfpci.c -->
# sources/distributed-fs/ceph-client/sound/pci/ymfpci/ymfpci.c

Purpose: Provides the PCI probe/module wrapper for Yamaha DS-1 family cards (`YMF724`, `YMF724F`, `YMF740`, `YMF740C`, `YMF744`, `YMF754`). It handles module parameters, card creation, legacy FM/MPU/gameport resource configuration, calls the core YMFPCI initialization routines, and registers the ALSA card.

Important APIs/types/functions: Module arrays configure card index/id/enable, optional FM and MPU IO ports, optional joystick port, and rear/line-in switch. `snd_ymfpci_ids[]` lists supported PCI IDs. `snd_ymfpci_create_gameport()` and `snd_ymfpci_free_gameport()` manage optional gameport resources and PCI legacy registers. `__snd_card_ymfpci_probe()` performs card allocation, model naming, legacy register selection, resource requests, calls `snd_ymfpci_create()`, creates PCM/SPDIF/mixer/timer interfaces, optional 4-channel and secondary capture PCMs, optional MPU401 rawmidi, optional OPL3 hwdep, gameport, and finally card registration.

Control flow: Probe is gated by static `dev` and `enable[dev]`. Newer YMF744/754 chips can autodetect FM/MPU/gameport bases from PCI BARs/config registers; older chips restrict ports to fixed legacy choices encoded in `PCIR_DSXG_ELEGACY`. The code writes legacy control registers before calling `snd_ymfpci_create()` and preserves old legacy control for cleanup. Optional MPU and OPL3 failures disable the corresponding legacy IRQ/enable bits but do not fail the whole sound card unless hwdep creation fails after OPL3 creation.

State and persistence: Persistent chip state is allocated as `card->private_data` and initialized in `ymfpci_main.c`; this file contributes legacy resource choices, `old_legacy_ctrl`, optional rawmidi/OPL3/gameport setup, and card naming. Gameport state is stored in `chip->gameport`.

Dependencies/integration: Depends on Linux PCI/module/time, ALSA core/initval, MPU401, OPL3, optional gameport, and the `ymfpci.h` helper API. Integrates with `module_pci_driver`, ALSA card lifecycle, and legacy PC IO port resource management.

Risks: Legacy IO port encoding differs before and after YMF744/754, so resource validation regressions can break FM/MPU/gameport. The static `dev` index can be consumed by disabled or failed probes. Card longname is initially formatted before `snd_ymfpci_create()` sets `reg_area_phys`/IRQ, so later registration behavior should be checked if user-facing names matter. Optional feature failures must leave PCI legacy registers consistent.

Test signals: Probe each supported PCI ID, test module parameter combinations for FM/MPU/gameport/rear switch, verify `snd_ymfpci_create()` plus PCM/mixer/timer creation, check MPU401 and OPL3 optional devices, confirm gameport registration and teardown, and suspend/resume through `snd_ymfpci_pm`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ymfpci/ymfpci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ymfpci/ymfpci.h -->
# sources/distributed-fs/ceph-client/sound/pci/ymfpci/ymfpci.h

Purpose: Defines the Yamaha DS-XG/YMFPCI hardware register map, PCI legacy configuration bits, DMA bank structures, voice/PCM/chip state, PM save lists, and cross-file function prototypes.

Important APIs/types/functions: `YMFREG()` maps register names to MMIO offsets. `YDSXGR_*` constants cover interrupt flags, global/mode/control registers, AC97 command/status, mixer volumes, capture formats/slots, playback/capture/effect/work base registers, and DSP/controller instruction RAM. `PCIR_DSXG_*` constants define PCI config legacy/FM/MPU/joy bases. Bank structs (`snd_ymfpci_playback_bank`, `capture_bank`, `effect_bank`) mirror hardware DMA/control memory layouts. `struct snd_ymfpci_voice` tracks one playback voice and its interrupt callback. `struct snd_ymfpci_pcm` tracks ALSA runtime state for playback/capture routing. `struct snd_ymfpci` is the primary persistent chip object.

Control flow: No executable flow, but the header defines the state machines used by `ymfpci_main.c`: voices are allocated from 64 playback slots, playback/capture/effect banks are double-buffered, `active_bank` selects the current hardware bank, `start_count` gates DSP engine start/stop, and saved register arrays define suspend/resume restore order.

State and persistence: `struct snd_ymfpci` stores MMIO mapping, old legacy PCI state, DMA work allocation, bank base addresses, voice pool, AC97 bus/codec, rawmidi/timer/PCM devices, capture/effect substream pointers, SPDIF bits, per-PCM mixer controls, locks/waitqueue, firmware pointers, and saved registers. This is the cross-module persistence contract for the entire driver.

Dependencies/integration: Includes ALSA PCM/rawmidi/ac97/timer, Linux gameport, and is shared by `ymfpci.c` and `ymfpci_main.c`. It exposes creation functions for PCM, mixer, timer, and PM ops used by the PCI wrapper.

Risks: Hardware structure packing and endianness are critical because these structs are written into DMA memory consumed by the DSP. Register constants and saved register lists must match chip revisions. The voice pool and `src441_used` special slot are shared mutable state protected by locks; new code must honor those locks. Firmware size constants must match requested blobs.

Test signals: Compile both YMFPCI objects, verify firmware download writes instruction RAM, run playback/capture/SPDIF/4ch paths, suspend/resume restore saved registers, and use lockdep or stress playback to catch voice/bank state races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ymfpci/ymfpci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ymfpci/ymfpci_main.c -->
# sources/distributed-fs/ceph-client/sound/pci/ymfpci/ymfpci_main.c

Purpose: Implements the Yamaha DS-XG/YMFPCI hardware engine: MMIO access, AC97 bus, firmware loading, DSP/bank memory allocation, voice allocation, PCM playback/capture/SPDIF/4ch, mixer controls, timer, IRQ handling, proc diagnostics, ACLink reset, PM save/restore, and chip creation.

Important APIs/types/functions: MMIO helpers wrap `read/write[bwl]`. AC97 callbacks are `snd_ymfpci_codec_write()` and `snd_ymfpci_codec_read()`. `snd_ymfpci_request_firmware()` requests `yamaha/ds1_dsp.fw`, `yamaha/ds1_ctrl.fw`, or `yamaha/ds1e_ctrl.fw`; `snd_ymfpci_download_image()` writes instruction RAM and enables DSP. `snd_ymfpci_memalloc()` allocates one DMA work area and partitions it into playback control, double-buffered playback/capture/effect banks, and work memory. Voice APIs allocate/free playback voices and start/stop the hardware engine. PCM APIs create four logical devices: main PCM, AC97/direct recording PCM, IEC958 PCM, and rear PCM. Mixer APIs create DS-XG volume, SPDIF, direct-recording, GPIO rear switch, 4ch duplicate, and per-substream PCM controls. `snd_ymfpci_create()` wires all initialization together.

Control flow: Creation enables PCI, requests MMIO/IRQ, resets ACLink, checks AC97 readiness, loads firmware, allocates/control-registers DMA banks, initializes AC3 effect scratch, and adds proc diagnostics. Playback open allocates a `snd_ymfpci_pcm`, sets route flags, and may enable rear/SPDIF extension mode. HW params allocate one or paired voices. Prepare fills both banks with DMA base, loop end, format, pitch delta, low-pass filter values, gains, and optional 44.1 kHz slot state. Trigger writes or clears playback control entries. Interrupt handling updates `active_bank`, calls each voice/capture interrupt callback, acknowledges status, services timer and MPU401. Capture prepare programs format/rate registers and capture banks; trigger maps/unmaps capture bank bits.

State and persistence: Persistent state is the `snd_ymfpci` card object. Stream state lives in allocated `snd_ymfpci_pcm` runtime objects and voice bank memory. Firmware pointers persist until card free. Suspend saves selected MMIO and PCI legacy registers plus mode, suspends AC97, mutes output, and disables DSP. Resume resets ACLink, reloads firmware, restores saved registers and PCI config, resumes AC97, and restarts mode if streams were active. Free mutes outputs, disables DSP, clears base registers, frees AC3 scratch, releases gameport, restores legacy config, and releases firmware.

Dependencies/integration: Depends on Linux firmware/PCI/IRQ/MMIO/delay/sched/slab, ALSA core/control/info/TLV/ac97/timer/MPU401, and `ymfpci.h`. Integrates with ALSA PCM ops, timer subsystem, AC97 mixer, procfs, PM ops, and firmware loader.

Risks: Firmware blobs and exact sizes are mandatory. DMA bank layout uses hardware-reported sizes and 0x100 alignment; misalignment breaks DSP operation. Voice allocation starts/stops the engine via `start_count`, so leaks or double frees can leave hardware running. IRQ code iterates all voices under `voice_lock` and calls callbacks that may invoke ALSA period notifications; lock ordering must remain consistent. SPDIF/rear extension state uses shared counters/flags. Suspend/resume must restore MMIO and PCI config in the right order after firmware reload.

Test signals: Load firmware successfully, verify main playback/capture with small periods, run concurrent substreams across 32 playback voices, test SPDIF open/control/status behavior, 4-channel and duplicate mode on SDAC codecs, direct recording source on YMF754, hardware timer interrupts, MPU401 coexistence, proc `ymfpci`, and suspend/resume while streams are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ymfpci/ymfpci_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pcmcia/Kconfig -->
# sources/distributed-fs/ceph-client/sound/pcmcia/Kconfig

Purpose: Defines the ALSA PCMCIA sound-device configuration menu and the selectable VXpocket and PDAudioCF drivers.

Important APIs/types/functions: `menuconfig SND_PCMCIA` is a boolean parent requiring `PCMCIA` and `HAS_IOPORT`, defaulting to yes. `config SND_VXPOCKET` is tristate and selects `SND_VX_LIB`. `config SND_PDAUDIOCF` is tristate and selects `SND_PCM`.

Control flow: Kconfig exposes child options only inside `if SND_PCMCIA && PCMCIA`. The selected symbols drive the PCMCIA Makefile and subdirectory builds.

State and persistence: No runtime state. Configuration state persists in the kernel `.config` and determines whether drivers are built-in, modules, or omitted.

Dependencies/integration: Integrates with the Linux Kconfig system, ALSA sound tree, PCMCIA core, IO port availability, VX shared library, and PCM core.

Risks: Because `SND_PCMCIA` defaults to yes when dependencies are met, child prompts may appear broadly. Missing `select` dependencies could cause link errors; overly broad selects can enlarge builds. Drivers rely on IO ports, so `HAS_IOPORT` is required.

Test signals: Run Kconfig with and without PCMCIA/HAS_IOPORT, verify child prompts visibility, build `snd-vxpocket` and `snd-pdaudiocf` as modules and built-ins, and confirm dependency selection of `SND_VX_LIB`/`SND_PCM`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pcmcia/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pcmcia/Makefile -->
# sources/distributed-fs/ceph-client/sound/pcmcia/Makefile

Purpose: Adds ALSA PCMCIA driver subdirectories to the build when the ALSA core is enabled.

Important APIs/types/functions: No runtime APIs. The only build rule is `obj-$(CONFIG_SND) += vx/ pdaudiocf/`.

Control flow: If `CONFIG_SND` is enabled, Kbuild descends into both `vx` and `pdaudiocf`; each subdirectory then applies its own Kconfig-controlled object rules.

State and persistence: No runtime state. Build inclusion is determined by Kconfig.

Dependencies/integration: Integrates PCMCIA sound subdirectories with the ALSA tree. It delegates actual module selection to subdirectory Makefiles and Kconfig symbols.

Risks: The parent uses `CONFIG_SND` rather than `CONFIG_SND_PCMCIA`, so subdirectory Makefiles must correctly gate objects. Adding a new PCMCIA driver requires updating this directory list.

Test signals: Kernel build with `CONFIG_SND=y/m` should descend into both subdirectories while only configured child modules are emitted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pcmcia/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pcmcia/pdaudiocf/Makefile -->
# sources/distributed-fs/ceph-client/sound/pcmcia/pdaudiocf/Makefile

Purpose: Defines the build composition for the Sound Core PDAudioCF PCMCIA/CompactFlash ALSA module.

Important APIs/types/functions: `snd-pdaudiocf-y` links `pdaudiocf.o`, `pdaudiocf_core.o`, `pdaudiocf_irq.o`, and `pdaudiocf_pcm.o`. `obj-$(CONFIG_SND_PDAUDIOCF)` conditionally emits `snd-pdaudiocf.o`.

Control flow: Kbuild aggregates the card-service/probe file, core hardware helpers, IRQ handling, and PCM implementation into one module when `CONFIG_SND_PDAUDIOCF` is enabled.

State and persistence: No runtime state. Object composition determines which implementation files are linked.

Dependencies/integration: Integrates with ALSA PCMCIA build and the PDAudioCF header shared by all four C files.

Risks: Omitting any listed object would remove required probe, core, interrupt, or PCM behavior. New helper files must be added here.

Test signals: Build with `CONFIG_SND_PDAUDIOCF=m` and confirm `snd-pdaudiocf.ko` links all four source objects without unresolved `snd_pdacf_*` or IRQ/PCM symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pcmcia/pdaudiocf/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pcmcia/pdaudiocf/pdaudiocf.c -->
# sources/distributed-fs/ceph-client/sound/pcmcia/pdaudiocf/pdaudiocf.c

Purpose: Implements the PCMCIA driver front-end for the Sound Core PDAudioCF sound card. It handles card allocation, PCMCIA IO/IRQ/device configuration, low-level chip creation handoff, resource assignment, card registration, detach, suspend/resume callbacks, and PCMCIA device ID matching.

Important APIs/types/functions: Module parameters are `index`, `id`, and `enable` arrays. `card_list[]` tracks allocated ALSA cards by slot. `snd_pdacf_probe()` allocates an ALSA card, calls `snd_pdacf_create()`, registers a low-level `snd_device` with `snd_pdacf_dev_free()`, initializes PCMCIA resource flags/config fields, and calls `pdacf_config()`. `pdacf_config()` requests IO, requests a threaded IRQ (`pdacf_interrupt` and `pdacf_threaded_irq`), enables the PCMCIA device, calls `snd_pdacf_assign_resources()`, and sets `card->sync_irq`. `snd_pdacf_assign_resources()` stores port/IRQ, marks configured, creates AK4117, names the card, creates PCM, and registers the card. `snd_pdacf_detach()` powers down configured hardware, marks stale, disconnects the card, and frees it when closed.

Control flow: Probe finds an unused card slot, honors `enable[]`, creates software state, binds it to `link->priv`, sets IO width and config registers, then performs resource configuration. Failure paths free IRQ/disable device as appropriate and release the card. Detach marks the chip stale before disconnecting so other paths can reject hardware access. PM callbacks delegate to `snd_pdacf_suspend()`/`snd_pdacf_resume()` only when a chip exists and the PCMCIA device is present.

State and persistence: Persistent per-card state is `struct snd_pdacf` allocated by `snd_pdacf_create()` and freed by the low-level snd_device callback. This file owns slot index, `card_list` membership, `p_dev` binding, configured status, IO port/IRQ assignment, and card naming. PCMCIA resources persist until `pdacf_release()` frees IRQ and disables the device.

Dependencies/integration: Depends on ALSA core/initval, Linux module/slab/init, PCMCIA CIS/config APIs, and PDAudioCF core/IRQ/PCM helpers from `pdaudiocf.h`. Integrates with `module_pcmcia_driver`, ALSA card lifecycle, threaded IRQs, and PCMCIA resource negotiation.

Risks: `pdacf_release()` unconditionally calls `free_irq()` and `pcmcia_disable_device()`, so error paths and partially configured devices must keep resource ownership clear. `card_list` must be cleared on failures/free to avoid slot leaks. Detach can race with open PCM users; the stale/disconnect/free-when-closed sequence is the safety mechanism. PCMCIA config uses fixed index `0x5` and 16-byte IO window, which must match the card CIS/hardware expectations.

Test signals: Insert/remove a matching PCMCIA card, verify IO/IRQ assignment and threaded IRQ registration, confirm AK4117 and PCM creation, run capture, remove while PCM is open, test suspend/resume with device present, and verify slot reuse after detach/failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pcmcia/pdaudiocf/pdaudiocf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pcmcia/pdaudiocf/pdaudiocf.h -->
# sources/distributed-fs/ceph-client/sound/pcmcia/pdaudiocf/pdaudiocf.h

Purpose: Defines PDAudioCF hardware register offsets, bit masks, chip status flags, the main `snd_pdacf` state structure, inline IO helpers, and cross-file function prototypes for the PDAudioCF driver.

Important APIs/types/functions: Register offsets describe music data, write/read data pointers, test control, status/control, interrupt status/enable, and AK interface. Bit masks cover FPGA/AKM/SRAM reset, powerdown, clock divider, recording, data detected, LED control, data format, FPGA revision, buffer/overrun/AKM IRQs, LED duty/modulation, and half-rate behavior. `struct snd_pdacf` stores ALSA card/index, IO port/IRQ, `reg_lock`, software register map, suspend SCR, AK4117 state/lock, chip status flags, PCM runtime/copy bookkeeping, and PCMCIA device pointer. `pdacf_reg_write()` updates the software regmap and writes a 16-bit IO register; `pdacf_reg_read()` reads a 16-bit IO register.

Control flow: No top-level executable flow, but the header defines how C files coordinate: card-service code creates/configures `snd_pdacf`, core code powers/reinitializes and creates AK4117, IRQ code services hardware interrupts, and PCM code uses the PCM fields for capture transfer accounting.

State and persistence: `regmap[]` mirrors writable hardware registers for restore and coordinated updates. `suspend_reg_scr` preserves SCR through PM. `chip_status` tracks stale/configured/suspended lifecycle. PCM fields persist while a stream is active and include format conversion flags, frame/sample sizes, total/period done counters, hardware pointer, and mapped area.

Dependencies/integration: Includes ALSA PCM and AK4117, Linux IO/IRQ, and PCMCIA CIS/device headers. Prototypes connect `pdaudiocf.c` with `pdaudiocf_core.c`, `pdaudiocf_irq.c`, and `pdaudiocf_pcm.c`.

Risks: IO helpers assume 16-bit port access and valid `reg >> 1` indexing into an eight-entry regmap; new registers must fit that model. Status bits gate hardware access after detach/suspend; callers must check stale/configured state. PCM bookkeeping is shared with IRQ/threaded paths, so lock and interrupt expectations in implementation files matter.

Test signals: Build all PDAudioCF objects, exercise register read/write paths, verify PM restores SCR/regmap, test AK4117 creation and interrupt handling, and run capture with different sample formats to validate PCM bookkeeping fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pcmcia/pdaudiocf/pdaudiocf.h -->
