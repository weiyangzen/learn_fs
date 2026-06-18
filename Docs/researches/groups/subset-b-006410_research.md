# subset-b-006410 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/sis7019.c -->
# sources/distributed-fs/ceph-client/sound/pci/sis7019.c

## Purpose
This file is the ALSA PCI driver for the SiS7019 Audio Accelerator. It owns card probing, controller reset, AC97 codec discovery, PCM playback and capture devices, interrupt handling, and suspend/resume. It is a self-contained single-card driver using the register definitions in `sis7019.h`.

## Important APIs, types, and functions
The main private objects are `struct sis7019` and `struct voice`. `struct sis7019` stores PCI/card/PCM/AC97 handles, mapped I/O, IRQ number, codec presence bits, the AC97 mutex, voice allocation lock, 64 playback voices, one capture voice, and suspend/silence pages. `struct voice` stores per-channel flags, ALSA substream, timing state, register bases, and optional timing voice linkage.

Important entry points are `snd_sis7019_probe()`, `__snd_sis7019_probe()`, `sis_chip_create()`, `sis_chip_init()`, `sis_mixer_create()`, and `sis_pcm_create()`. ALSA stream callbacks are grouped in `sis_playback_ops` and `sis_capture_ops`, including `sis_playback_open()`, `sis_capture_open()`, `sis_pcm_playback_prepare()`, `sis_capture_hw_params()`, `sis_pcm_capture_prepare()`, `sis_pcm_trigger()`, and `sis_pcm_pointer()`. AC97 accesses go through `sis_ac97_rw()`, `sis_ac97_read()`, and `sis_ac97_write()`. Power management is handled by `sis_suspend()`, `sis_resume()`, and `DEFINE_SIMPLE_DEV_PM_OPS`.

## Control flow
Probe checks the `enable` module parameter, normalizes the expected `codecs` bitmask, allocates an ALSA card with private driver storage, creates and initializes the chip, creates AC97 mixers, creates a PCM with 64 playback substreams and one capture substream, then registers the card. Chip creation enables the PCI device, restricts DMA to 30 bits, requests regions, maps the 16 KiB MMIO parameter area, allocates four suspend pages, resets and initializes the controller, requests the shared IRQ, enables bus mastering, and assigns register bases for every voice.

Playback open allocates one free hardware voice. Playback prepare programs DMA format, base address, loop/end offsets, interrupt mode, rate delta, and wave-engine parameters. If the buffer has more than two periods, playback uses stop-sample-offset interrupts and `sis_update_sso()` advances the next period target. Capture open reserves the single capture voice and constrains rates from the primary AC97 ADC. Capture hardware params set the AC97 ADC rate and may allocate a muted playback timing voice when capture has more than two periods. Capture prepare programs the capture DMA channel and, when needed, configures the timing voice against the silence buffer.

`sis_pcm_trigger()` walks the ALSA synchronized trigger group, builds record and playback bitmasks, marks each peer done, and writes start/stop registers. `sis_interrupt()` filters for playback/capture DMA IRQ sources, drains playback bank A, playback bank B, and capture status registers, calls `sis_update_voice()` or `snd_pcm_period_elapsed()`, acknowledges per-channel status, then acknowledges the global status.

## State and persistence behavior
Runtime state is in memory and hardware registers only. Voice flags track allocation, capture role, SSO timing, and synchronized timing. The silence buffer uses `suspend_state[0]`; it is DMA-mapped on first timing-voice user and unmapped when the last user exits. Suspend frees the IRQ, suspends present AC97 codecs, and copies four 4 KiB MMIO pages into `suspend_state[]`. Resume reinitializes the chip, reacquires IRQ, restores the saved MMIO pages, clears the silence buffer, resumes AC97 codecs, and returns the card to D0.

## Dependencies and integration points
The file integrates with Linux PCI managed resources, IRQ handling, DMA mapping, ALSA core, ALSA PCM, and ALSA AC97. It depends on `sis7019.h` for all register offsets and bit fields. User-visible integration is via ALSA card registration, AC97 mixer controls, PCM playback/capture nodes, module parameters, and PCI ID `PCI_VENDOR_ID_SI:0x7019`.

## Risks and test signals
Key risks are hardware timing edge cases, AC97 semaphore timeouts, capture timing drift, DMA mask limitations, suspend/resume register restore correctness, and single-capture-channel limits. The capture timing path is especially sensitive because it uses a muted playback voice and periodic SSO corrections to emulate capture period interrupts. Test signals include successful probe and card registration, AC97 mixer discovery for expected codecs, clean playback and capture at 8/44.1/48 kHz, synchronized start with grouped streams, capture with one, two, and more-than-two periods, no IRQ storms on shared IRQ lines, and suspend/resume with active PCM streams suspended by ALSA.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/sis7019.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/sis7019.h -->
# sources/distributed-fs/ceph-client/sound/pci/sis7019.h

## Purpose
This header is the register and bitfield map for the SiS7019 Audio Accelerator used by `sis7019.c`. It has no functions or storage; it provides symbolic offsets for global control, interrupts, AC97 command/status, DMA parameter RAM, mixer routing, and wave-engine channel parameters.

## Important APIs, types, and definitions
The header exposes macros only. Global registers include `SIS_GCR`, `SIS_GIER`, `SIS_GISR`, and `SIS_DMA_CSR`. Playback and record start/stop/status registers are represented by `SIS_PLAY_START_A_REG`, `SIS_PLAY_START_B_REG`, `SIS_PLAY_STOP_A_REG`, `SIS_PLAY_STOP_B_REG`, `SIS_RECORD_START_REG`, `SIS_RECORD_STOP_REG`, `SIS_PISR_A`, `SIS_PISR_B`, and `SIS_RISR`. AC97 access uses `SIS_AC97_CMD`, `SIS_AC97_SEMA`, `SIS_AC97_STATUS`, `SIS_AC97_CONF`, and `SIS_AC97_PSR`.

Parameter RAM helpers include `SIS_PLAY_DMA_ADDR()`, `SIS_CAPTURE_DMA_ADDR()`, `SIS_MIXER_START_ADDR()`, `SIS_MIXER_ADDR()`, and `SIS_WAVE_ADDR()`. These macros derive byte addresses inside the 16 KiB mapped parameter area. Format/control fields cover sample width, signedness, mono/stereo, loop enable, interrupt-at-LEO/MLP/SSO, DMA base, and SSO/ESO programming. Mixer fields describe attenuation and routing destinations. Wave fields cover wave/music volume, articulation delta, and channel-control bits such as first sample, amplifier enable, filter enable, and interpolation enable.

## Control flow
There is no executable control flow. The operational flow is established by the C driver: reset/configuration code writes global and AC97 registers; PCM prepare paths write DMA and wave parameter RAM; IRQ code reads and acknowledges playback/capture/global status; mixer initialization writes mixer route tables.

## State and persistence behavior
The header does not persist state. Its constants define hardware state locations and masks. Driver state becomes persistent only while held in device registers or in the driver's in-memory structures. The address macros assume that the caller supplies the mapped MMIO base and a valid channel number.

## Dependencies and integration points
This file is tightly coupled to `sis7019.c`. The register names are not namespaced beyond the `SIS_` prefix and are intended for this driver, not a generic subsystem interface. It encodes hardware layout assumptions: 64 playback channels, capture channels including AC97 PCM/mic/line inputs, 4-byte mixer entries, 0x40-byte wave entries, and a 0x4000 MMIO parameter aperture.

## Risks and test signals
Risks are mostly maintenance risks: incorrect masks or offsets would cause silent hardware misprogramming, DMA corruption, missed interrupts, or broken AC97 access. The misspelled `ATTENUTATION` macro names are harmless but part of the local API. Test signals are indirect: successful chip reset, codec detection, valid playback/capture interrupts, correct period pointers, no channel cross-talk after mixer routing setup, and no MMIO out-of-range access when all 64 voices are initialized.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/sis7019.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/sonicvibes.c -->
# sources/distributed-fs/ceph-client/sound/pci/sonicvibes.c

## Purpose
This file is the ALSA PCI driver for S3 SonicVibes `86c617` hardware. It implements PCI probing, enhanced-port register access, DDMA playback/capture, mixer controls, MPU-401 MIDI, OPL3 hardware dependency, optional gameport registration, `/proc` diagnostics, and card teardown.

## Important APIs, types, and functions
The central `struct sonicvibes` stores I/O ports, DDMA resources, cached indirect-register state, stream pointers, ALSA objects, register lock, DMA sizes, and optional gameport. Module parameters control card index/id/enable, reverb, MIC gain, and fallback DDMA I/O base.

Register helpers are `snd_sonicvibes_out1()`, `snd_sonicvibes_out()`, `snd_sonicvibes_in1()`, and `snd_sonicvibes_in()`. DDMA helpers are `snd_sonicvibes_setdmaa()`, `snd_sonicvibes_setdmac()`, `snd_sonicvibes_getdmaa()`, and `snd_sonicvibes_getdmac()`. PCM behavior is handled by `snd_sonicvibes_pcm()`, playback/capture open/close/prepare/trigger/pointer callbacks, and `snd_sonicvibes_interrupt()`. Rate setup is split between DAC divisor programming and ADC PLL programming through `snd_sonicvibes_pll()`, `snd_sonicvibes_setpll()`, `snd_sonicvibes_set_adc_rate()`, and `snd_sonicvibes_set_dac_rate()`. Mixer controls are generated by `SONICVIBES_SINGLE`, `SONICVIBES_DOUBLE`, and `SONICVIBES_MUX`.

## Control flow
Probe allocates an ALSA card, initializes the device through `snd_sonicvibes_create()`, fills card names, creates PCM, mixer, MPU-401 UART, MIDI controls, OPL3 hwdep, optional gameport, then registers the card. Device creation enables PCI, enforces a 24-bit coherent DMA mask, requests PCI regions, requests IRQ, restores or assigns DDMA channel I/O ports, requests DDMA regions, enables enhanced DDMA in PCI config space, resets the chip, programs power/rate/mixer defaults, unmasks DMA and up/down interrupts, and creates `/proc` output.

Playback prepare computes format bits, programs DAC rate, programs DDMA-A with the ALSA buffer address and size, and writes period counts to indirect DMA-A registers. Capture prepare does the same for DDMA-C, but DDMA-C is word-mode, so byte counts are shifted. Trigger toggles the playback/capture enable bits in `SV_IREG_PC_ENABLE`. Pointers subtract the current DDMA residual count from the cached buffer size.

The interrupt handler checks DMA-A, DMA-C, MIDI, and up/down-button status. DMA interrupts call `snd_pcm_period_elapsed()` on cached substream pointers. MIDI interrupts delegate to the MPU-401 helper. Up/down-button interrupts adjust analog master volume/mute registers under the register lock and notify ALSA controls.

## State and persistence behavior
Driver state is volatile. Cached fields such as `enable`, `irqmask`, `format`, `srs_space`, `srs_center`, `mpu_switch`, and `wave_source` mirror hardware settings. The free path unregisters the gameport and writes original DDMA ports back into PCI config dwords. There is no explicit suspend/resume implementation in this file.

## Dependencies and integration points
The file integrates with PCI managed resources, ALSA PCM/control/info, raw MIDI via `snd_mpu401_uart_new()`, OPL3 via `snd_opl3_create()` and `snd_opl3_hwdep_new()`, and optional Linux gameport support. It depends on legacy I/O port access and direct PCI config writes for DDMA channel setup.

## Risks and test signals
The source comment states two known hardware risks: rev 3 may not support DDMA buffers above 16 MiB and the driver can sometimes hang for unknown reasons. A concrete code risk is that `snd_sonicvibes_interrupt()` dereferences `sonic->master_mute` and `sonic->master_volume` on up/down IRQs, but this file declares and clears those pointers without assigning them when creating the master controls. Other risks include 24-bit DMA constraints, global `dmaio` fallback allocation across cards, no PM restore path, and register-lock correctness around indirect register accesses. Test signals include probe on systems with and without BIOS DDMA config, playback/capture period interrupts, MIDI input IRQ unmask/mask behavior, OPL3 creation, gameport registration when configured, mixer get/put round trips, and no null dereference on hardware volume button interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/sonicvibes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/trident/Makefile -->
# sources/distributed-fs/ceph-client/sound/pci/trident/Makefile

## Purpose
This Makefile defines the ALSA Trident module composition. It builds one module, `snd-trident`, from the PCI wrapper, shared hardware engine, and TLB memory allocator.

## Important APIs, types, and functions
There are no C APIs here. The key build variables are `snd-trident-y := trident.o trident_main.o trident_memory.o` and `obj-$(CONFIG_SND_TRIDENT) += snd-trident.o`. The first line defines the objects linked into the composite module; the second connects the module to the kernel configuration symbol.

## Control flow
Kbuild compiles `trident.c`, `trident_main.c`, and `trident_memory.c`, then links them into `snd-trident.o` when `CONFIG_SND_TRIDENT` is enabled as built-in or module. `trident.c` provides module metadata and PCI registration. `trident_main.c` provides most exported and internal device logic. `trident_memory.c` provides TLB allocation helpers referenced by the main implementation.

## State and persistence behavior
The Makefile has no runtime state. It controls whether the runtime state defined in the C files is present in the built kernel/module.

## Dependencies and integration points
The file depends on Linux Kbuild composite-object conventions and the `CONFIG_SND_TRIDENT` Kconfig symbol defined elsewhere. It establishes that all three source files must remain ABI-compatible within one module, including exported symbols used by other Trident-related ALSA components.

## Risks and test signals
Risks are build integration risks: removing one object would leave unresolved references such as `snd_trident_create()` or `snd_trident_alloc_pages()`, and adding objects without updating this file would omit functionality. Test signals are `make M=sound/pci/trident` or full kernel/module builds with `CONFIG_SND_TRIDENT=m/y`, plus `modinfo snd-trident` showing a single module built from these objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/trident/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/trident/trident.c -->
# sources/distributed-fs/ceph-client/sound/pci/trident/trident.c

## Purpose
This file is the PCI/module wrapper for the Trident 4DWave DX/NX and SiS SI7018 ALSA driver. It declares module parameters and PCI IDs, allocates the ALSA card, calls the shared device constructor in `trident_main.c`, creates device-specific PCM/MIDI/gameport surfaces, and registers the card.

## Important APIs, types, and functions
Module parameters are `index`, `id`, `enable`, `pcm_channels`, and `wavetable_size`. Supported IDs are Trident 4DWave DX, Trident 4DWave NX, and SiS 7018. The only substantive function is `snd_trident_probe()`. It calls exported helpers declared in `trident.h`: `snd_trident_create()`, `snd_trident_pcm()`, `snd_trident_foldback_pcm()`, `snd_trident_spdif_pcm()`, and `snd_trident_create_gameport()`. It also optionally creates an integrated MPU-401 UART for non-SiS devices.

## Control flow
The PCI driver invokes `snd_trident_probe()` for matching devices. The function enforces the `SNDRV_CARDS` index limit and per-card `enable` flag, allocates an ALSA card with `struct snd_trident` private data, and calls `snd_trident_create()`. The `pcm_spdif_device` argument is `1` for SiS7018 and `2` for Trident devices so later IEC958 controls bind to the right PCM device index.

After core creation, the wrapper selects card driver strings by detected device, creates the main PCM, creates foldback PCM only for DX/NX, creates S/PDIF PCM only for NX/SI7018, creates MPU-401 only for non-SiS devices, attempts gameport creation, registers the card, stores PCI driver data, and increments the static card index.

## State and persistence behavior
The file has little runtime state beyond module-parameter arrays and the static `dev` probe counter. Device state lives in `struct snd_trident`, allocated by `snd_devm_card_new()` and initialized by `trident_main.c`. No suspend/resume code is implemented here, but the PCI driver attaches `snd_trident_pm` when `CONFIG_PM_SLEEP` is enabled.

## Dependencies and integration points
This wrapper integrates Linux PCI matching, ALSA card allocation, ALSA MPU-401 UART support, module parameters, and the shared Trident implementation. It depends on `trident.h` for device IDs, private structure declarations, helper prototypes, and PM ops.

## Risks and test signals
Risks include static `dev` indexing behavior across disabled cards, device-specific PCM ordering assumptions, and best-effort gameport creation whose failure is ignored. Test signals include probe for each of DX, NX, and SI7018, correct card names, expected PCM device count/order, absence of MPU-401 on SI7018, presence of S/PDIF on NX/SI7018, and PM ops being present in builds with sleep support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/trident/trident.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/trident/trident.h -->
# sources/distributed-fs/ceph-client/sound/pci/trident/trident.h

## Purpose
This header defines the shared Trident/SiS7018 driver contract: device IDs, register offsets, bit definitions, private structures, voice and TLB memory models, exported helper prototypes, and PM ops used across `trident.c`, `trident_main.c`, and `trident_memory.c`.

## Important APIs, types, and definitions
Important constants include `TRIDENT_DEVICE_ID_DX`, `TRIDENT_DEVICE_ID_NX`, `TRIDENT_DEVICE_ID_SI7018`, voice type constants, `SNDRV_TRIDENT_PAGE_SIZE`, and `SNDRV_TRIDENT_MAX_PAGES`. Register definitions cover global control, miscellaneous interrupts, legacy DMA registers, voice start/stop/status banks, MPU-401, NX S/PDIF, joystick, NX TLB control, voice channel registers, DX/NX AC97 registers, and SI7018 AC97/serial/GPIO/S/PDIF registers.

Core structures are `struct snd_trident`, `struct snd_trident_voice`, `struct snd_trident_tlb`, `struct snd_4dwave`, `struct snd_trident_pcm_mixer`, and `struct snd_trident_port`. `struct snd_trident` is the device object containing PCI/card handles, ports, IRQ, S/PDIF state, AC97 handles, voice allocation maps, locks, TLB state, PCM devices, raw MIDI, and gameport. `struct snd_trident_voice` models each hardware channel and carries both register-programming fields and PCM/synth ownership metadata.

Public prototypes include device construction, PCM creation, gameport creation, voice allocation/free/start/stop/register write, TLB page allocation/free, and `snd_trident_pm`.

## Control flow
The header has no executable flow, but it defines the shared state transitions used by the implementation: wrapper probe calls `snd_trident_create()`, PCM open allocates `snd_trident_voice`, prepare fills voice register fields, trigger starts/stops voice banks, IRQ updates voice sync state, and close/free returns voice/TLB resources.

## State and persistence behavior
The header defines all persistent in-memory state for the module. Hardware-facing state is duplicated in cached fields such as `spdif_bits`, `spdif_ctrl`, `musicvol_wavevol`, `pcm_mixer[]`, `ChanMap[]`, `bDMAStart`, and per-voice register fields. TLB state includes both the DMA-visible table and the ALSA util memory header used to allocate virtual pages.

## Dependencies and integration points
The header depends on ALSA PCM, MPU-401, AC97, and util memory headers. It is the integration boundary among the three objects linked by the local Makefile and any related Trident synth code that uses the exported voice helpers.

## Risks and test signals
Risks include bitfield drift across DX/NX/SI7018 variants, different voice register layouts, 30-bit DMA/TLB assumptions, and structure fields that are manipulated under different locks. Test signals are compile coverage of all three objects, successful probe on all supported device IDs, TLB allocation only on NX, correct S/PDIF and rear-path controls on supported hardware, and no lockdep or race symptoms during concurrent PCM open/close/trigger.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/trident/trident.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/trident/trident_main.c -->
# sources/distributed-fs/ceph-client/sound/pci/trident/trident_main.c

## Purpose
This is the shared hardware engine for Trident 4DWave DX/NX and SiS SI7018. It implements AC97 access, hardware initialization, voice allocation and register programming, ALSA PCM operations for playback/capture/foldback/S/PDIF, mixer and IEC958 controls, optional gameport support, `/proc` diagnostics, interrupt handling, and suspend/resume.

## Important APIs, types, and functions
External entry points include `snd_trident_create()`, `snd_trident_pcm()`, `snd_trident_foldback_pcm()`, `snd_trident_spdif_pcm()`, `snd_trident_alloc_voice()`, `snd_trident_free_voice()`, `snd_trident_start_voice()`, `snd_trident_stop_voice()`, and `snd_trident_write_voice_regs()`. AC97 ops are `snd_trident_codec_read()` and `snd_trident_codec_write()`, with device-specific register paths for DX, NX, and SI7018. Voice programming helpers write CSO, ESO, volume, pan, reverb, chorus, and full register sets.

PCM implementation includes memory allocation (`snd_trident_allocate_pcm_mem()`), extra interrupt voice allocation (`snd_trident_allocate_evoice()`), prepare callbacks for playback, legacy capture, SI7018 capture, foldback, and S/PDIF, the shared `snd_trident_trigger()`, and pointer callbacks. Mixer logic includes wave/music volume controls, per-PCM front/pan/reverb/chorus controls, S/PDIF default/mask/stream/switch controls, and NX rear-path control.

## Control flow
`snd_trident_create()` enables PCI, sets a 30-bit DMA mask, initializes locks and stream limits, requests regions and IRQ, allocates NX TLB state when needed, initializes S/PDIF defaults, runs the per-device hardware init, creates mixers, initializes the 64 voice objects and PCM mixer defaults, enables ESO/MIDLP interrupts, and creates proc diagnostics.

PCM open allocates a bank-B PCM voice and stores it in `runtime->private_data`. Playback prepare computes rate delta and spurious IRQ threshold, selects either TLB offset or DMA address, fills voice registers, and optionally prepares an extra muted voice as a period interrupt generator when the buffer is not exactly two periods. Legacy capture configures legacy DMA registers and uses a PCM voice to generate synchronized period interrupts. SI7018 capture uses voice attributes and optional extra voice instead of legacy DMA. Foldback routes a mixer capture channel through `T4D_RCI`. S/PDIF uses NX hardware S/PDIF registers on NX and SI serial/S/PDIF registers on SI7018.

The shared trigger walks ALSA synchronized stream groups, collects voice masks, toggles running state, starts/stops voices, enables/disables bank-B interrupts, updates S/PDIF registers, and starts/stops legacy capture DMA for non-SI capture. The IRQ handler filters `ADDRESS_IRQ` and `MPU401_IRQ`, reads bank interrupt status, drops spurious interrupts based on the sample timer threshold, adjusts sync voices when needed, calls `snd_pcm_period_elapsed()` outside the register lock, acknowledges interrupts, and delegates MPU-401 IRQs.

## State and persistence behavior
Persistent runtime state lives in `struct snd_trident`: AC97 handles, TLB table, voice maps, PCM mixer settings, S/PDIF bits, music/wave volume, spurious IRQ counters, and per-device flags. Per-voice state mirrors hardware register values and ALSA stream ownership. Suspend marks `in_suspend`, changes power state, and suspends AC97 codecs. Resume reruns per-device init, resumes codecs, restores music/wave volume, reenables ESO interrupts, and clears `in_suspend`; it does not restore each active PCM voice directly, relying on ALSA suspend semantics.

## Dependencies and integration points
This file depends on ALSA core, PCM, control, TLV, info, AC97, raw MIDI integration from the wrapper, Linux PCI/IRQ/I/O, optional gameport, and `trident_memory.c` for NX virtual memory. It provides module-internal services consumed by `trident.c` and TLB allocation services consumed during PCM hw_params.

## Risks and test signals
Risks include variant-specific register programming, complex extra-voice synchronization, spurious interrupt heuristics, legacy capture DMA setup, inconsistent S/PDIF hardware differences, TLB versus physical DMA address paths, and lock handoff around `snd_pcm_period_elapsed()`. There is a likely naming/assignment bug in `snd_trident_spdif_open()`: SI7018 selects `snd_trident_spdif` while non-SI selects `snd_trident_spdif_7018`, which appears reversed by the hardware definitions. Test signals include full probe on DX/NX/SI7018, playback across many period layouts, capture on DX/NX and SI7018, foldback channel naming and capture, S/PDIF control activation while stream is open, MIDI IRQ delivery, gameport raw/cooked reads, no spurious IRQ floods, TLB allocation/free under repeated hw_params changes, and suspend/resume followed by mixer and PCM reuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/trident/trident_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/trident/trident_memory.c -->
# sources/distributed-fs/ceph-client/sound/pci/trident/trident_memory.c

## Purpose
This file implements virtual memory page allocation for Trident 4DWave-NX TLB-backed PCM buffers. The chip can address only a limited DMA window at one time, so the driver maps ALSA DMA buffer pages into a hardware TLB and hands voice programming a virtual offset.

## Important APIs, types, and functions
The exported functions are `snd_trident_alloc_pages()` and `snd_trident_free_pages()`. Internal allocation paths are `snd_trident_alloc_sg_pages()` for ALSA scatter-gather buffers and `snd_trident_alloc_cont_pages()` for contiguous device DMA buffers. `search_empty()` allocates aligned regions from the ALSA util memory block list. `is_valid_page()` verifies that DMA addresses fit the hardware mask and are 4 KiB aligned.

Macros adapt the hardware 4 KiB Trident page model to the kernel `PAGE_SIZE`. For 4 KiB pages, one aligned page maps one TLB entry. For 8 KiB pages, one aligned page maps two TLB entries. For larger page sizes, `UNIT_PAGES` maps each kernel page to multiple hardware TLB entries. `set_tlb_bus()` writes bus addresses into the TLB table; `set_silent_tlb()` resets entries to the driver's silent page.

## Control flow
PCM hw_params in `trident_main.c` calls `snd_trident_alloc_pages()` when TLB entries exist and the buffer changed. The allocator selects SG or contiguous mode from `substream->dma_buffer.dev.type`, locks the util memory header, finds a free virtual page range, validates every physical page, and writes corresponding TLB entries. On validation failure it frees the just-created memory block and returns NULL. Hardware voice setup later uses `voice->memblk->offset` as the loop begin address.

On hw_free or buffer replacement, `snd_trident_free_pages()` locks the same memory header, rewrites the block's TLB entries to the silent page, frees the util memory block, and returns.

## State and persistence behavior
The allocator mutates `trident->tlb.entries`, the DMA-visible TLB table allocated in `trident_main.c`, and `trident->tlb.memhdr`, the software allocation map. `struct snd_trident_memblk_arg` stores first and last aligned page numbers in each util memory block. Freed TLB slots intentionally remain mapped to the silent page rather than stale user buffer pages.

## Dependencies and integration points
The file depends on `struct snd_trident_tlb` from `trident.h`, ALSA util memory internals, ALSA PCM SG helpers, DMA addresses from PCM runtime buffers, and Linux I/O/endian helpers. It is meaningful only for devices where `trident->tlb.entries` was allocated, currently NX initialization.

## Risks and test signals
Risks include page-size-specific mapping errors, off-by-one range handling in `search_empty()`, physical address validation failures, concurrency around the util memory block list, and stale TLB mappings if free paths are skipped. Test signals include NX playback using SG buffers, repeated hw_params with changing buffer sizes, allocation failure cleanup, freeing resetting entries to the silent page, validation rejection of unaligned or too-large DMA addresses, and no memory leaks reported by ALSA util memory diagnostics in `/proc`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/trident/trident_memory.c -->
