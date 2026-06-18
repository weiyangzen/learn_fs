# subset-b-006378 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/es18xx.c -->
# sources/distributed-fs/ceph-client/sound/isa/es18xx.c

Purpose: standalone ALSA ISA/PNP driver for ESS ES18xx AudioDrive chips. It probes ES1868/1869/1878/1879/1887/1888 variants, configures chip-specific mixer and PCM capabilities, registers PCM playback/capture, OPL3, and optional MPU-401 UART devices.

Important APIs, types, and functions: `struct snd_es18xx` stores card resources, chip version/caps, active stream bits, DMA shifts, PCM substreams, rawmidi, mixer controls, locks, and PnP handles. Low-level register access is via `snd_es18xx_dsp_command()`, `snd_es18xx_read/write/bits()`, mixer helpers, and control-port helpers. PCM entry points are `snd_es18xx_playback_*`, `snd_es18xx_capture_*`, `snd_es18xx_pcm()`. Probe paths are `snd_es18xx_new_device()`, `snd_es18xx_identify()`, `snd_es18xx_probe()`, `snd_audiodrive_probe()`, ISA probe, PNPBIOS probe, and PnP-card probe. PM uses `snd_es18xx_suspend()` and `snd_es18xx_resume()`.

Control flow: module init registers an ISA driver and, when enabled, PnP and PnP-card drivers. Probing allocates an ALSA card, activates or auto-selects resources, requests I/O/IRQ/DMA, resets and identifies the chip, maps version to capability flags, initializes chip registers, creates PCM and mixer devices, then attaches OPL3 and MPU-401 when ports are valid. PCM prepare programs rate, format, period count, and ISA DMA; triggers toggle device DMA bits; interrupt dispatch reads status and calls `snd_pcm_period_elapsed()` for active DAC/ADC streams or `snd_mpu401_uart_interrupt()` for MIDI.

State and persistence: runtime state is volatile in `struct snd_es18xx`; mixer state lives in hardware registers and ALSA controls. PnP resource arrays are overwritten from activated devices. PM only saves the PM register and restores power state, so full mixer/PCM state is not deeply serialized. Active stream masks and substream pointers gate half/full-duplex restrictions.

Dependencies and integration: uses Linux ISA, PnP, ISAPnP, I/O port, IRQ, and DMA APIs; ALSA core, control, PCM, OPL3, MPU401, and initval helpers. The driver integrates with `/proc` and userspace through normal ALSA card, PCM, mixer, rawmidi, and hwdep registration.

Risks: hardware timings are busy-wait based, and comments document pops plus questionable 16-bit DMA behavior. Duplex mode has chip-specific constraints and shared DMA cases disable some capabilities. Mixer control arrays rely on exact version/capability mapping. IRQ status handling always returns handled once status is nonzero and must keep hardware ack order correct. PnP activation has legacy vendor-register side effects.

Test signals: module load with explicit/auto resources, PnP and non-PnP detection, `aplay`/`arecord` at mono/stereo 8/16-bit rates, duplex conflict checks, mixer control enumeration per chip, OPL3 and MPU-401 creation, interrupt period progress, suspend/resume smoke tests, and resource failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/es18xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/galaxy/Makefile -->
# sources/distributed-fs/ceph-client/sound/isa/galaxy/Makefile

Purpose: Kbuild glue for the Aztech Sound Galaxy ISA drivers. It defines `snd-azt1605-y := azt1605.o` and `snd-azt2316-y := azt2316.o`, then wires those composite objects to `CONFIG_SND_AZT1605` and `CONFIG_SND_AZT2316`.

Important APIs/types/functions: no C APIs are defined here; the important integration points are the Kbuild object variables and `obj-$(CONFIG_...)` module selections.

Control flow: when the corresponding Kconfig symbol is enabled, Kbuild compiles either wrapper file. Each wrapper includes `galaxy.c`, so the shared driver body is built separately with chip-specific preprocessor constants.

State and persistence: no runtime state; build output names determine loadable module identity.

Dependencies and integration: depends on ALSA ISA build infrastructure and the wrapper/source include-template pattern in the same folder. Risks are mostly build-time: changing object names or config symbols would disconnect the drivers from Kconfig. Test signals are successful kernel build with both symbols enabled independently and checking that only the selected modules are linked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/galaxy/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/galaxy/azt1605.c -->
# sources/distributed-fs/ceph-client/sound/isa/galaxy/azt1605.c

Purpose: chip-specific wrapper for the Aztech AZT1605 Sound Galaxy driver. It defines identity strings, DSP version expectations, a 24-bit configuration register layout, and then includes `galaxy.c` as the shared implementation.

Important APIs/types/functions: the file provides macros consumed by `galaxy.c`: `AZT1605`, `CRD_NAME`, `DRV_NAME`, `DEV_NAME`, `GALAXY_DSP_MAJOR/MINOR`, `GALAXY_CONFIG_SIZE`, address/enable/IRQ/DMA bit definitions, and `GALAXY_CONFIG_MASK`.

Control flow: the compiled object is effectively `galaxy.c` specialized for AZT1605. During probe, `galaxy.c` validates module parameters against these bit assignments, expects DSP version 2.1, writes three config bytes, resets after WSS mode on AZT1605, and registers WSS/MPU/OPL3 devices.

State and persistence: no independent state beyond preprocessor constants. Runtime state is in the shared `struct snd_galaxy`, static module parameter arrays, and hardware config latch restored by `snd_galaxy_free()`.

Dependencies and integration: tightly coupled to `galaxy.c`; it is not a normal header but a compilation wrapper. It integrates through the `snd-azt1605` Kbuild object and ALSA ISA driver registered by the included body.

Risks: bitfield definitions must match AZT1605 hardware exactly. Unsupported CD/unused bits are preserved through `GALAXY_CONFIG_MASK`, so mistakes can corrupt legacy board routing. Test signals are compilation, module parameter validation, DSP type/version match, WSS configuration, MPU IRQ variants including AZT1605-only IRQ 3, and unload restoring saved config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/galaxy/azt1605.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/galaxy/azt2316.c -->
# sources/distributed-fs/ceph-client/sound/isa/galaxy/azt2316.c

Purpose: chip-specific wrapper for the Aztech AZT2316 Sound Galaxy driver. It defines the AZT2316 identity, DSP version, 32-bit configuration register map, and includes the shared `galaxy.c` implementation.

Important APIs/types/functions: defines `AZT2316`, card/driver/device names, `GALAXY_DSP_MAJOR/MINOR` as 3.1, `GALAXY_CONFIG_SIZE` as 4, and the AZT2316-specific SBA, WSS, game, MPU, CD, DMA, IRQ, and mask bits. These macros drive probe-time parameter encoding in `galaxy.c`.

Control flow: Kbuild compiles the wrapper, the preprocessor folds in `galaxy.c`, and the resulting driver probes as `azt2316`. The shared probe checks user-supplied ports/IRQs/DMAs, builds a 32-bit config word with AZT2316 bit positions, writes four config bytes, enters WSS mode without the AZT1605 reset workaround, and creates WSS/MPU/OPL3 ALSA devices.

State and persistence: no direct runtime state; it shapes the shared static config arrays and saved/restored hardware latch state in `struct snd_galaxy`.

Dependencies and integration: depends on `galaxy.c`, Kbuild `snd-azt2316`, ALSA WSS/MPU401/OPL3 helpers, and ISA module parameters.

Risks: AZT2316 has more CD and DMA routing fields than AZT1605, so mask correctness matters. The shared code conditionally allows MPU IRQ 10 only for this wrapper. Test signals include compile, valid/invalid module parameter rejection, DSP version 3.1 detection, WSS duplex configuration, optional OPL3/MPU devices, and config restoration on device free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/galaxy/azt2316.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/galaxy/galaxy.c -->
# sources/distributed-fs/ceph-client/sound/isa/galaxy/galaxy.c

Purpose: shared implementation for Aztech AZT1605/AZT2316 Sound Galaxy ISA cards. It probes the Sound Blaster-compatible DSP, writes the board configuration latch, switches to WSS mode, and registers ALSA WSS PCM/mixer/timer plus optional MPU-401 and OPL3 devices.

Important APIs/types/functions: `struct snd_galaxy` stores mapped DSP/config/WSS ports, saved config, and resources. DSP helpers are `dsp_reset()`, `dsp_command()`, `dsp_get_version()`. WSS helpers are `wss_detect()` and `wss_set_config()`. Main driver functions are `snd_galaxy_match()`, `galaxy_init()`, `galaxy_set_config()`, `galaxy_config()`, `galaxy_wss_config()`, `__snd_galaxy_probe()`, and `module_isa_driver()`.

Control flow: the ISA match callback validates module parameters and encodes them into `config[n]` and `wss_config[n]`. Probe allocates an ALSA card, requests/maps SB DSP ports, verifies the DSP signature and expected version/type, requests/maps the high config port, saves current config and writes the new config, requests/maps WSS ports, validates WSS signature, writes WSS IRQ/DMA config, switches the card to WSS mode, creates WSS PCM/mixer/timer, and optionally creates MPU-401 and OPL3 resources before registering the card.

State and persistence: module parameter arrays are mutated from IRQ 2 to 9 and from unspecified optional ports to `-1`. `struct snd_galaxy.config` preserves masked board bits and `snd_galaxy_free()` restores the original config and clears WSS config on card cleanup.

Dependencies and integration: relies on wrapper macros from `azt1605.c`/`azt2316.c`, Linux ISA/I/O mapping, ALSA WSS, MPU401, OPL3, and devres card/resource cleanup.

Risks: parameter validation is strict, so auto-probe is intentionally not implemented. Config port writes are hardware-latch sensitive and preserve only masked fields. Shared WSS/MPU IRQ is rejected. Test signals are module load with known valid resources, failure on invalid resource combinations, WSS PCM playback/capture, optional MIDI/FM, and unload restoring the original config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/galaxy/galaxy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/Makefile -->
# sources/distributed-fs/ceph-client/sound/isa/gus/Makefile

Purpose: Kbuild manifest for the Gravis UltraSound family. It builds a shared `snd-gus-lib` from core GF1 helpers and links it with board modules for Classic, Extreme, MAX, InterWave, and InterWave STB.

Important APIs/types/functions: no C API, but the object lists define module composition. `snd-gus-lib-y` includes `gus_main.o`, I/O, IRQ, timer, memory, DRAM, DMA, volume, PCM, mixer, UART, and reset helpers. Board objects are `gusclassic.o`, `gusextreme.o`, `gusmax.o`, `interwave.o`, and `interwave-stb.o`.

Control flow: Kbuild includes the board object plus `snd-gus-lib.o` when a board Kconfig symbol is enabled. This makes exported GF1 helper symbols available to the board-specific module.

State and persistence: no runtime state. Build-time linkage determines which helper code is present in each module.

Dependencies and integration: ties the GUS subtree to ALSA ISA Kconfig symbols. The STB object is a wrapper that includes `interwave.c` with `SNDRV_STB`. Risks are missing helper objects or mismatched exported symbols causing link failures. Test signals are all five module configurations building alone and in combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/gus_dma.c -->
# sources/distributed-fs/ceph-client/sound/isa/gus/gus_dma.c

Purpose: queued GF1 DRAM DMA engine for PCM and synthesizer transfers. It abstracts ISA DMA programming and GF1 DRAM DMA register setup, with PCM transfers prioritized over synth transfers.

Important APIs/types/functions: `snd_gf1_dma_init()`, `snd_gf1_dma_done()`, `snd_gf1_dma_suspend()`, and `snd_gf1_dma_transfer_block()` are the public entry points. Internals include `snd_gf1_dma_ack()`, `snd_gf1_dma_program()`, `snd_gf1_dma_next_block()`, and `snd_gf1_dma_interrupt()`. It operates on `struct snd_gf1_dma_block` queues stored in `gus->gf1`.

Control flow: clients enqueue a copied DMA block under `dma_lock`. If no transfer is active, the first block is popped and programmed immediately. Hardware interrupt acks the DMA register, invokes the previous block callback, pops the next PCM or synth block, programs it, and frees the queue node. Init installs the DMA-write interrupt handler and uses a shared refcount; done tears down only when the last user leaves.

State and persistence: queue heads/tails, current ack callback/private data, shared count, and trigger flag live in `gus->gf1`; all are volatile. Suspend drains active and queued transfers, calling callbacks so waiters can finish.

Dependencies and integration: uses ISA DMA (`snd_dma_program`, `snd_dma_disable`), GF1 register helpers, `dma_lock`, `dma_mutex`, and default interrupt handlers from reset code. PCM playback uses this for DRAM block uploads.

Risks: address translation differs for 8/16-bit DMA and enhanced mode; unaligned addresses are rejected only by debug return. Callback ordering matters for close waiters. Test signals include PCM block upload progress, queued multiple blocks, synth/PCM priority, suspend while DMA active, high-DMA channels, and no leaked queue nodes after close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/gus_dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/gus_dram.c -->
# sources/distributed-fs/ceph-client/sound/isa/gus/gus_dram.c

Purpose: user-facing DRAM/ROM byte access helpers for GUS and InterWave memory windows.

Important APIs/types/functions: exported functions are `snd_gus_dram_write()` and `snd_gus_dram_read()`. Internal helpers `snd_gus_dram_poke()` and `snd_gus_dram_peek()` copy in 256-byte chunks and switch between InterWave block I/O and plain GF1 byte pokes.

Control flow: write copies data from userspace into a stack buffer and writes to card memory. Read fills a stack buffer from RAM or ROM and copies to userspace. InterWave paths select memory control mode, set the DRAM address once per chunk, then use `outsb()`/`insb()`; non-InterWave paths iterate through `snd_gf1_poke()`/`snd_gf1_peek()`.

State and persistence: hardware DRAM/ROM contents are persistent while the card is powered and driver-managed; no allocator metadata is changed here. InterWave memory-control register is temporarily changed and restored to RAM mode after ROM reads.

Dependencies and integration: used by proc memory dump entries in `gus_mem_proc.c`; depends on `copy_from_user()`, `copy_to_user()`, GF1 register locking, and low-level DRAM helpers.

Risks: caller must validate address/size against bank limits; these helpers do not enforce bounds. User copy failures return `-EFAULT`. Test signals are `/proc` RAM/ROM reads, write/readback to allocated RAM, InterWave ROM read selection, and copy fault handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/gus_dram.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/gus_io.c -->
# sources/distributed-fs/ceph-client/sound/isa/gus/gus_io.c

Purpose: low-level GF1/InterWave I/O primitives for register access, voice address conversion, DRAM byte access, AdLib timer writes, and active-voice selection.

Important APIs/types/functions: exported helpers include `snd_gf1_delay()`, `snd_gf1_write8/look8/write16/look16()`, interrupt-safe `snd_gf1_i_*()` variants, `snd_gf1_ctrl_stop()`, `snd_gf1_adlib_write()`, `snd_gf1_write_addr()`, `snd_gf1_read_addr()`, `snd_gf1_dram_addr()`, `snd_gf1_poke()`, `snd_gf1_peek()`, and `snd_gf1_select_active_voices()`.

Control flow: the internal `__snd_gf1_*` routines perform raw port writes and memory barriers. Public unlocked variants assume caller serialization; `i_` variants take `reg_lock`. Voice address helpers translate linear byte addresses into GF1 split start/end/current registers, handling enhanced mode and 16-bit addressing. `snd_gf1_select_active_voices()` clamps voice count, computes playback frequency, and writes active voice count on plain GF1.

State and persistence: writes mutate hardware registers and update `gus->gf1.active_voices` and `playback_freq`. DRAM poke/peek reads and writes onboard memory. No higher-level ALSA objects are created.

Dependencies and integration: every GUS file depends on this layer through `include/sound/gus.h`. Reset, PCM, memory detection, DMA, UART, timer, and board probes all call these helpers.

Risks: lock discipline is split between caller-locked and self-locking APIs; mixing them incorrectly can race register selection/data ports. Address conversion is hardware-specific and easy to break for enhanced/16-bit modes. Test signals are register readback during detection, voice setup, DRAM read/write, PCM pointer correctness, and running with lockdep/IRQ stress where possible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/gus_io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/gus_irq.c -->
# sources/distributed-fs/ceph-client/sound/isa/gus/gus_irq.c

Purpose: central GF1/InterWave interrupt dispatcher. It demultiplexes MIDI, voice wave/ramp, timers, and DRAM/record DMA events to handler callbacks installed in `gus->gf1`.

Important APIs/types/functions: exported `snd_gus_interrupt()` is used by board drivers and combined IRQ handlers. Debug-only `snd_gus_irq_profile_init()` creates a `gusirq` proc report. The file uses `STAT_ADD()` counters under `CONFIG_SND_DEBUG`.

Control flow: the handler reads `reg_irqstat`, returns unhandled if zero, and otherwise loops up to 100 dispatch cycles. MIDI bits call MIDI callbacks, voice bits drain `SNDRV_GF1_GB_VOICES_IRQ` until no pending voice IRQ remains, timer bits call timer handlers, and DMA bits inspect DMA control registers before invoking write/read DMA handlers. Lost voice IRQs stop wave and volume controls.

State and persistence: debug counters accumulate in `gus->gf1` and per-voice structs. Callback function pointers are mutable runtime state installed by reset, PCM, timer, DMA, and UART code.

Dependencies and integration: invoked directly from Classic/Extreme and indirectly from MAX/InterWave combined handlers. Depends on low-level locked GF1 reads/stops and ALSA proc info.

Risks: a stuck IRQ source can exhaust the loop and return `IRQ_NONE`, which is a diagnostic signal. Handler callbacks must be IRQ-safe. Voice deduping with a bitmask prevents repeated service of the same voice in one pass. Test signals are MIDI in/out interrupts, PCM wave period interrupts, timer interrupts, DMA completion, debug proc counters, and shared IRQ handlers routing only when status bits are set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/gus_irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/gus_main.c -->
# sources/distributed-fs/ceph-client/sound/isa/gus/gus_main.c

Purpose: common GUS card allocation, resource management, plain GF1 memory detection, DMA/IRQ latch programming, version detection, ALSA joystick control, and suspend/resume wrappers.

Important APIs/types/functions: exported `snd_gus_create()`, `snd_gus_initialize()`, `snd_gus_suspend()`, and `snd_gus_resume()`. Internal work is in `snd_gus_free()`, `snd_gus_init_dma_irq()`, `snd_gus_check_version()`, and `snd_gus_detect_memory()`. The file also exports symbols implemented by other GUS helper objects.

Control flow: board drivers call `snd_gus_create()` to allocate `struct snd_gus_card`, initialize locks and register addresses, request I/O/IRQ/DMA, clamp voice/channel counts, and register a low-level ALSA device. `snd_gus_initialize()` checks plain GF1 version unless InterWave, detects memory, programs DMA/IRQ latches, and starts GF1 hardware. Suspend suspends PCM then GF1; resume reprograms latches and resumes GF1.

State and persistence: `struct snd_gus_card` owns all GF1 resource descriptors, flags such as `max_flag`, `ace_flag`, `ess_flag`, DMA/IRQ sharing flags, memory bank allocator state, mixer latch state, and joystick DAC. Hardware latch state is reprogrammed on init/resume and cleared on free.

Dependencies and integration: all board drivers depend on this allocator. It integrates with ALSA `snd_device_new()`, raw ISA resource APIs, DMA APIs, and `snd_gf1_start/stop`.

Risks: manual resource cleanup is mixed with ALSA device lifetime; failure paths must call `snd_gus_free()`. Negative IRQ values are used by some board drivers to indicate shared IRQ arrangements before external request. Test signals are create/fail cleanup, plain GF1 memory sizing, version flag detection, DMA/IRQ latch programming, joystick mixer control, and PM resume restoring playback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/gus_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/gus_mem.c -->
# sources/distributed-fs/ceph-client/sound/isa/gus/gus_mem.c

Purpose: bottom-layer allocator for onboard GF1/InterWave sample memory. It tracks used blocks across 8-bit and 16-bit banks and supports shared block IDs for synth/sample reuse.

Important APIs/types/functions: exported `snd_gf1_mem_alloc()`, `snd_gf1_mem_xfree()`, and `snd_gf1_mem_free()`. Init/teardown helpers are `snd_gf1_mem_init()` and `snd_gf1_mem_done()`. Internals include ordered insertion, address lookup, share lookup, and first-fit allocation across bank descriptors.

Control flow: init creates reserved driver blocks for InterWave LFO memory and the default silent voice address. Allocation locks `memory_mutex`, optionally finds an existing shared block, computes a free aligned range in the requested 8/16-bit banks, copies share IDs, inserts the block sorted by address, and returns it. Free looks up by address and decrements share count or unlinks/frees the block. Debug builds expose a `gusmem` proc summary.

State and persistence: allocator state is a linked list plus `banks_8`/`banks_16` arrays in `gus->gf1.mem_alloc`. The actual DRAM content is separate; this file only reserves address ranges.

Dependencies and integration: PCM playback allocates `"GF1 PCM"` blocks; reset initializes default voice memory; InterWave/plain detection populates bank sizes before init. Depends on ALSA proc debug support and Linux slab/string helpers.

Risks: `snd_gf1_mem_alloc()` returns `NULL` both for allocation failure and for successful share hit after incrementing `share`, which is a legacy ambiguous contract. Bank iteration assumes valid nonzero bank arrays. Test signals include allocating/freeing 8/16-bit aligned blocks, sharing IDs, debug proc output, PCM buffer resize freeing old memory, and no leaks after `snd_gf1_mem_done()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/gus_mem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/gus_mem_proc.c -->
# sources/distributed-fs/ceph-client/sound/isa/gus/gus_mem_proc.c

Purpose: creates ALSA proc binary entries for dumping GUS RAM banks and InterWave ROM banks.

Important APIs/types/functions: `struct gus_proc_private` stores ROM flag, address, size, and card pointer. `snd_gf1_mem_proc_dump()` services reads using `snd_gus_dram_read()`. `snd_gf1_mem_proc_init()` creates `gus-ram-N` and `gus-rom-N` entries.

Control flow: init iterates RAM bank descriptors and ROM presence bits. For each non-empty bank it allocates private data, creates a card proc entry, marks it as data content, installs the read ops, sets entry size, and arranges `private_free` cleanup. Read calls into DRAM/ROM access with the supplied file position and count.

State and persistence: private proc state mirrors detected bank addresses and sizes. It does not update allocator state or hardware except through reads. Entries live with the ALSA card.

Dependencies and integration: called from `snd_gf1_start()` after memory initialization. Depends on `gus_dram.c`, ALSA info/proc infrastructure, and bank metadata from memory detection.

Risks: the dump function ignores `priv->address` and passes `pos` directly to `snd_gus_dram_read()`, so bank-relative proc offsets depend on how callers interpret addresses; this is legacy behavior worth verifying. Test signals are proc entry creation for each detected bank, correct entry sizes, successful reads, ROM-vs-RAM selection, and cleanup without leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/gus_mem_proc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/gus_mixer.c -->
# sources/distributed-fs/ceph-client/sound/isa/gus/gus_mixer.c

Purpose: ALSA mixer controls for the GF1 board mixer latch and optional ICS2101 mixer chip.

Important APIs/types/functions: exported `snd_gf1_new_mixer()`. GF1 controls use `GF1_SINGLE()` with `snd_gf1_get_single()`/`snd_gf1_put_single()`. ICS controls use `ICS_DOUBLE()` with `snd_ics_get_double()`/`snd_ics_put_double()`.

Control flow: `snd_gf1_new_mixer()` names the mixer, adds component metadata for ICS2101, then registers either simple GF1 boolean switches or full ICS volume/switch controls. Put handlers update cached `mix_cntrl_reg` or `gf1.ics_regs` under `reg_lock` and write the hardware mixer/control ports. Some ICS boards flip master/GF1 channels.

State and persistence: mixer latch and ICS register cache live in `struct snd_gus_card`. ALSA controls reflect these cached/hardware values. State is volatile and restored only by driver initialization/resume paths.

Dependencies and integration: board flags from `snd_gus_check_version()` decide whether ICS controls exist. Extreme boards later rename ES1688 controls around GF1 synth routing, while MAX/InterWave use WSS mixer code for codec paths.

Risks: non-ICS controls are minimal, and Extreme `ess_flag` limits simple GF1 controls to avoid duplicate routing. Hardware writes depend on exact port sequencing. Test signals are mixer control enumeration on Classic 2.4/3.5/3.7, switch toggling affecting latch register, ICS volume write/readback, and mixer names/components.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/gus_mixer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/gus_pcm.c -->
# sources/distributed-fs/ceph-client/sound/isa/gus/gus_pcm.c

Purpose: ALSA PCM implementation for GF1/InterWave synth playback and plain GF1 capture. Playback uploads samples into onboard DRAM and drives GF1 voices; capture uses GF1 record DMA without autoinit support.

Important APIs/types/functions: exported `snd_gf1_pcm_new()`. `struct gus_pcm_private` tracks substream, allocated voices, onboard memory, period/block state, DMA wait queue, and volume. Playback ops implement open/close/hw_params/hw_free/prepare/trigger/pointer/copy/silence. Capture ops implement open/close/hw_params/prepare/trigger/pointer. Mixer control handlers manage `"PCM Playback Volume"` or `"GPCM Playback Volume"`.

Control flow: playback open allocates private state and initializes GF1 DMA. `hw_params` allocates GF1 memory and one/two voices; copy/silence writes into runtime DMA area then either queues GF1 DMA or pokes small blocks directly. Trigger start programs voice start/current/end/pan/frequency/volume ramp; wave interrupts roll period endpoints and call `snd_pcm_period_elapsed()`. Capture programs DMA2 one period at a time and restarts it in the DMA-read interrupt.

State and persistence: per-substream state owns GF1 memory and voices until `hw_free`. Global GF1 PCM volume is cached in `gus->gf1`. Active flags, `bpos`, and DMA counts are volatile playback state.

Dependencies and integration: uses `gus_dma.c`, `gus_mem.c`, `gus_volume.c`, `gus_io.c`, reset voice allocation, ALSA PCM constraints, and ISA DMA. InterWave disables capture because codec capture is handled by WSS.

Risks: noninterleaved playback layout, onboard memory allocation, and voice IRQ rollover are tightly coupled. Close waits for pending DMA and logs serious DMA problems after timeout. Test signals are playback at 1/2 channels and 8/16-bit signed/unsigned formats, period interrupts, copy/silence correctness, volume changes during playback, capture on plain GF1, suspend stop behavior, and buffer resize freeing memory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/gus_pcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/gus_reset.c -->
# sources/distributed-fs/ceph-client/sound/isa/gus/gus_reset.c

Purpose: GF1 hardware start/stop, default interrupt handlers, voice allocation/freeing, voice stopping, and GF1 suspend/resume support.

Important APIs/types/functions: exported `snd_gf1_set_default_handlers()`, `snd_gf1_smart_stop_voice()`, `snd_gf1_stop_voice()`, `snd_gf1_stop_voices()`, `snd_gf1_alloc_voice()`, `snd_gf1_free_voice()`, `snd_gf1_start()`, `snd_gf1_stop()`, `snd_gf1_suspend()`, and `snd_gf1_resume()`. Internals initialize software state, clear registers, clear voices, and run `snd_gf1_hw_start()`.

Control flow: startup resets GF1, initializes callback pointers and voices, optionally enables enhanced mode and memory control, computes default silent voice address, clears DRAM silence bytes, clears all voices, enables IRQ/DAC, initializes timers, memory allocator/proc entries, and debug IRQ profiling. Voice allocation finds unused voices, respecting PCM reservation, and can steal idle MIDI voices. Free restores default handlers, clears hardware voice state, and invokes private cleanup.

State and persistence: mutates `gus->gf1` voice table, callback pointers, LFO flags, default voice address, timer state, memory allocator, UART command state, and hardware reset/mode registers. Resume preserves software state but restarts hardware and timers/UART.

Dependencies and integration: used by `snd_gus_initialize()`, PCM voice management, DMA/UART/timer handlers, and board PM callbacks.

Risks: voice stop ramping sleeps when not in interrupt; callers must avoid sleeping contexts. Hardware start has different initial vs resume paths. Test signals include all voices cleared after init/stop, PCM voice allocation limits, MIDI voice stealing, GF1 reset register transitions, timer/proc setup, suspend draining DMA/UART and disabling capture DMA, and resume restoring active timers/UART.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/gus_reset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/gus_tables.h -->
# sources/distributed-fs/ceph-client/sound/isa/gus/gus_tables.h

Purpose: shared declarations and optional allocation for GF1 lookup tables.

Important APIs/types/functions: defines table sizes `SNDRV_GF1_SCALE_TABLE_SIZE` and `SNDRV_GF1_ATTEN_TABLE_SIZE`. When `__GUS_TABLES_ALLOC__` is defined, it allocates `snd_gf1_atten_table`; otherwise it declares externs. A disabled scale table remains under `#if 0`.

Control flow: `gus_volume.c` defines `__GUS_TABLES_ALLOC__` before including this header, creating the attenuation table and exporting it. Other users include it for extern declarations.

State and persistence: the attenuation table is static read-only data used by synth-related code; no runtime mutation.

Dependencies and integration: exported for `snd-gus-synth` module via `EXPORT_SYMBOL(snd_gf1_atten_table)` in `gus_volume.c`. Risks are ABI/data compatibility with external synth code and accidental multiple definitions if allocation macro is misused. Test signals are successful link with one definition, synth module resolving the symbol, and table bounds matching 128 entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/gus_tables.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/gus_timer.c -->
# sources/distributed-fs/ceph-client/sound/isa/gus/gus_timer.c

Purpose: exposes the two GF1 AdLib-compatible timers as ALSA card timers.

Important APIs/types/functions: `snd_gf1_timers_init()`, `snd_gf1_timers_done()`, and `snd_gf1_timers_resume()` manage timer lifecycle. Timer hardware callbacks are `snd_gf1_timer1_start/stop()` and `snd_gf1_timer2_start/stop()`. IRQ callbacks are `snd_gf1_interrupt_timer1()` and `snd_gf1_interrupt_timer2()`.

Control flow: init installs timer interrupt handlers, creates timer #1 with 80us resolution and timer #2 with 320us resolution, and stores them in `gus->gf1`. Start writes the count register, sets `timer_enabled` bits, updates sound-blaster control, and writes AdLib timer control. IRQ callbacks call `snd_timer_interrupt()`. Done restores default handlers and frees timer devices. Resume reinstalls handlers and restarts timers that were enabled.

State and persistence: `gus->gf1.timer1`, `timer2`, and `timer_enabled` hold timer state. Hardware timer registers are volatile and reprogrammed on start/resume.

Dependencies and integration: initialized by GF1 start and used by ALSA timer clients. The main IRQ dispatcher calls the installed handlers.

Risks: timer control bits are shared with GF1 sound-blaster control register; stop/start must preserve other timer bit. Test signals include ALSA timer creation, start/stop tick delivery, interrupt counters under debug, timer free cleanup, and resume rearming previously enabled timers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/gus_timer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/gus_uart.c -->
# sources/distributed-fs/ceph-client/sound/isa/gus/gus_uart.c

Purpose: ALSA RawMIDI driver for the GF1 MIDI UART, modeled like a 6850 UART.

Important APIs/types/functions: exported `snd_gf1_rawmidi_new()`, `snd_gf1_uart_suspend()`, and `snd_gf1_uart_resume()`. RawMIDI ops implement input/output open, close, and trigger. IRQ callbacks are `snd_gf1_interrupt_midi_in()` and `snd_gf1_interrupt_midi_out()`.

Control flow: creating rawmidi registers one input and one output substream and stores the GUS card as private data. Open resets UART if needed, installs IRQ handlers, and stores active substream pointers. Input trigger toggles Rx IRQ bit; output trigger sends an initial byte when FIFO is free and enables Tx IRQ. IRQ handlers drain received bytes, report errors, transmit queued bytes, or disable Tx IRQ when empty. Close resets UART if the opposite side is inactive and restores default handlers.

State and persistence: `gus->gf1.uart_cmd`, framing/overrun counters, substream pointers, and handler callbacks are volatile. Suspend writes reset; resume restores handlers, clears pending input, and restores saved command when a substream remains active.

Dependencies and integration: main IRQ dispatcher invokes MIDI handlers. Board drivers call `snd_gf1_rawmidi_new()` when MIDI is supported/enabled. Depends on ALSA RawMIDI and low-level UART inline helpers.

Risks: receive handler reads a status/data byte pair and uses a bounded spin loop; unexpected FIFO behavior can drop bytes. Output trigger briefly unlocks to wait for Rx empty. Test signals include full-duplex MIDI, trigger start/stop, overrun/framing counters, close while other direction active, and suspend/resume with open substreams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/gus_uart.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/gus_volume.c -->
# sources/distributed-fs/ceph-client/sound/isa/gus/gus_volume.c

Purpose: GF1 volume and frequency conversion helpers plus attenuation table allocation/export.

Important APIs/types/functions: exported `snd_gf1_lvol_to_gvol_raw()` converts linear volume to GF1 exponential/mantissa format, and `snd_gf1_translate_freq()` converts fixed-point frequency to GF1 frequency register units using current playback frequency. `snd_gf1_atten_table` is allocated here and exported for the synth module.

Control flow: volume conversion clamps input to 65535, finds exponent and mantissa, and packs them into a 16-bit GF1 volume. Frequency conversion shifts input, clamps a low minimum, detects overflow, and scales by `gus->gf1.playback_freq`.

State and persistence: functions are pure except overflow logging; the attenuation table is read-only static data. `snd_gf1_translate_freq()` depends on current active-voice-derived playback frequency.

Dependencies and integration: PCM volume controls call `snd_gf1_lvol_to_gvol_raw()`, PCM trigger uses `snd_gf1_translate_freq()`, and external synth code uses `snd_gf1_atten_table`.

Risks: conversion accuracy affects playback gain and pitch. Overflow handling assigns a bitwise-negated mask-like value before scaling, which is legacy behavior and should be regression-tested before modification. Test signals are boundary values for volume, frequency conversion at supported rates/voice counts, exported symbol resolution, and audible PCM pitch/volume sanity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/gus_volume.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/gusclassic.c -->
# sources/distributed-fs/ceph-client/sound/isa/gus/gusclassic.c

Purpose: ALSA ISA driver for Gravis UltraSound Classic and ACE-style plain GF1 cards.

Important APIs/types/functions: module parameters cover card identity, port, IRQ, two DMAs, joystick DAC, active voices, and PCM channels. Main functions are `snd_gusclassic_create()`, `snd_gusclassic_detect()`, `snd_gusclassic_probe()`, and PM wrappers around `snd_gus_suspend/resume()`.

Control flow: match checks `enable[n]`. Probe allocates an ALSA card, ensures at least two PCM channels, auto-finds IRQ/DMAs/port when requested, calls `snd_gus_create()`, resets/release-tests GF1, initializes common GUS state, rejects MAX/Extreme detections, creates GF1 mixer and PCM, creates rawmidi unless ACE, appends resource info to `longname`, registers the card, and stores drvdata.

State and persistence: runtime state is mostly common `struct snd_gus_card`; this file sets `joystick_dac` and module parameter arrays. Hardware and ALSA objects are volatile across module load/unload and PM.

Dependencies and integration: uses shared `snd-gus-lib`, legacy resource auto-probe helpers, ISA driver framework, and ALSA card registration.

Risks: broad port auto-probing can touch legacy hardware ranges. Detection only checks GF1 reset bits, while later common version detection distinguishes Classic/MAX/ACE/Extreme. Test signals are module load on real/emulated GF1, auto-resource fallback, rejection of MAX/Extreme, PCM and rawmidi devices, ACE rawmidi omission, and PM suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/gusclassic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/gusextreme.c -->
# sources/distributed-fs/ceph-client/sound/isa/gus/gusextreme.c

Purpose: ALSA ISA driver for Gravis UltraSound Extreme, combining an ES1688 codec/front-end with a GF1 synth.

Important APIs/types/functions: `struct snd_gusextreme` embeds `struct snd_es1688` and a `struct snd_gus_card *`. Key functions create the ES1688 side, create GF1 side, enable GF1 access through ES1688 mixer/init ports, detect GF1, rename mixer controls, and probe/register the card.

Control flow: probe allocates one ALSA card, normalizes MPU defaults, creates ES1688 resources and optional MPU routing, sets default GF1 port relative to ES1688, creates GF1 resources, writes the ES1688 sequence that exposes GF1, validates GF1 reset behavior, initializes common GUS, requires `ess_flag`, creates ES1688 PCM/mixer, optional GF1 PCM, GF1 mixer, control renames, optional OPL3 and MPU401, and registers the card. Resume resets ES1688, re-enables GF1, then resumes GUS.

State and persistence: combines ES1688 and GF1 state in card private data. `gus->codec_flag` and `ess_flag` drive common helper behavior. Hardware routing through ES1688 is volatile and must be restored on resume.

Dependencies and integration: depends on `sound/es1688.h`, shared GUS library, OPL3, MPU401, ALSA ISA, and legacy auto-probe helpers.

Risks: GF1 enable sequence is reverse-engineered and port-sensitive. Two chips have separate IRQ/DMA resources, so longname and failure paths must reflect both. Test signals include ES1688 PCM/mixer, GF1 synth PCM/mixer, OPL3/MPU optional devices, control renames, suspend/resume re-exposing GF1, and failure when `ess_flag` is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/gusextreme.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/gusmax.c -->
# sources/distributed-fs/ceph-client/sound/isa/gus/gusmax.c

Purpose: ALSA ISA driver for Gravis UltraSound MAX, combining GF1 synth with an onboard WSS/CS4231-compatible codec and shared IRQ/DMA routing.

Important APIs/types/functions: `struct snd_gusmax` stores card, GUS, WSS, IRQ, and status registers. Key routines are `snd_gusmax_detect()`, `snd_gusmax_interrupt()`, `snd_gusmax_init()`, `snd_gusmax_mixer()`, `snd_gusmax_probe()`, and PM callbacks.

Control flow: probe allocates card private data, auto-selects IRQ/DMAs/port if needed, calls `snd_gus_create()` with negative IRQ to avoid common IRQ request, validates GF1 reset, initializes MAX routing latch, runs common GUS init, requires `max_flag`, requests a combined IRQ, creates WSS codec with shared IRQ/DMA flags at `port + 0x10c`, registers WSS PCM/mixer/timer, optional GF1 PCM, renames mixer controls for synth/CD routing, creates GF1 rawmidi, builds longname, and registers the card.

State and persistence: `max_cntrl_val` in `gus` preserves routing latch value for resume. `snd_gusmax_interrupt()` dispatches shared IRQs by polling GF1 and WSS status ports. `struct snd_gusmax` stores GUS/WSS pointers after successful registration.

Dependencies and integration: shared GUS library, ALSA WSS, ISA IRQ/DMA, and legacy resource auto-probe.

Risks: shared interrupt dispatch depends on correct status registers and bounded polling. Negative IRQ handoff between common creation and board IRQ request is subtle. Test signals include WSS playback/capture, GF1 synth PCM/rawmidi, shared IRQ activity for both chips, mixer renames, routing latch restore on resume, and cleanup on failed WSS creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/gusmax.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/interwave-stb.c -->
# sources/distributed-fs/ceph-client/sound/isa/gus/interwave-stb.c

Purpose: wrapper module for InterWave STB cards with TEA6330T tone control. It defines `SNDRV_STB` and includes `interwave.c`.

Important APIs/types/functions: this file contributes no functions itself. The `SNDRV_STB` macro enables STB-specific code in `interwave.c`: different driver names/descriptions, `port_tc` module parameter, PnP second logical device, bit-banged I2C ops, TEA6330T detection/update/restore, and mixer-control renaming.

Control flow: Kbuild builds `interwave-stb.o`, preprocessor includes the InterWave implementation with STB paths active, and the resulting module registers ISA/PNP drivers under STB-specific names.

State and persistence: runtime state is `struct snd_interwave` plus STB-only `i2c_bus` and `i2c_res`. Tone-control mixer state is restored on resume by STB code in the included implementation.

Dependencies and integration: depends on `interwave.c`, `sound/tea6330t.h`, ALSA I2C bit-bang support, and STB PnP IDs. Risks are include-template coupling and accidental divergence from non-STB InterWave behavior. Test signals are compile of `CONFIG_SND_INTERWAVE_STB`, TEA6330T detection at `port_tc`, PnP tone-control resource activation, mixer update, and resume restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/interwave-stb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/interwave.c -->
# sources/distributed-fs/ceph-client/sound/isa/gus/interwave.c

Purpose: ALSA ISA/PNP driver for AMD InterWave cards and, when included with `SNDRV_STB`, InterWave STB cards with TEA6330T tone control. It combines InterWave GF1-compatible synth, WSS codec, optional ROM/RAM bank detection, MIDI UART, and PM restoration.

Important APIs/types/functions: `struct snd_interwave` stores card, GUS, WSS, IRQ/status ports, PnP handles, and STB I2C state. Key functions include `snd_interwave_detect()`, `snd_interwave_detect_memory()`, `snd_interwave_init()`, `snd_interwave_mixer()`, `snd_interwave_pnp()`, `snd_interwave_probe_gus()`, `snd_interwave_probe()`, ISA/PNP probe paths, and PM restore helpers. STB builds add I2C bit ops and `snd_interwave_detect_stb()`.

Control flow: module init registers an ISA driver and PnP-card driver. ISA probe auto-selects IRQ/DMAs and optionally ports, creates a card, creates GUS resources, detects InterWave by reset/version-register behavior, detects STB tone control if enabled, records status ports, initializes InterWave compatibility registers, detects RAM/ROM layout, starts common GUS, requests a shared IRQ, creates WSS codec PCM/timer/mixer, optional GF1 PCM, InterWave mixer renames/additions, optional STB TEA6330T mixer, rawmidi, card names, and registers the card. PnP probe activates logical devices first and feeds resources into the same probe.

State and persistence: memory bank sizes, ROM presence, revision, joystick DAC, InterWave flags, WSS/GUS pointers, and STB I2C state live in card/GUS structs. PM resumes GUS, restores InterWave compatibility and memory-config registers, resumes WSS, and restores TEA6330T mixer if present.

Dependencies and integration: shared GUS library, ALSA WSS, Linux ISA/PNP, legacy resource helpers, optional ALSA I2C and TEA6330T. Combined IRQ routes GF1 and WSS by polling status.

Risks: InterWave memory configuration detection writes RAM test bytes and relies on known layout codes. ISA auto-port loop returns early after `snd_interwave_probe_gus()` success without running full probe in one branch, a path worth regression-checking. STB/non-STB behavior is controlled by include-time macro. Test signals include PnP and manual ISA probing, RAM/ROM proc entries, WSS codec audio, GF1 synth PCM, rawmidi with `midi` parameter, shared IRQs, STB tone-control mixer, and suspend/resume restoring memory layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/interwave.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/msnd/Makefile -->
# sources/distributed-fs/ceph-client/sound/isa/msnd/Makefile

Purpose: Kbuild manifest for Turtle Beach MultiSound/MSND ISA drivers. It builds a shared `snd-msnd-lib` and two board modules.

Important APIs/types/functions: build variables are `snd-msnd-lib-y := msnd.o msnd_pinnacle_mixer.o`, `snd-msnd-pinnacle-y := msnd_pinnacle.o`, and `snd-msnd-classic-y := msnd_classic.o`. `obj-$(CONFIG_SND_MSND_PINNACLE)` and `obj-$(CONFIG_SND_MSND_CLASSIC)` link the selected board object with the shared library.

Control flow: enabling a board config compiles the board-specific file and common MSND support into the module. This file does not participate in runtime control flow.

State and persistence: no runtime state; module composition is build-time only.

Dependencies and integration: depends on adjacent MSND C files and ALSA ISA Kconfig. Risks are link failures or missing common mixer support if object lists drift. Test signals are kernel builds with Pinnacle and Classic configs independently enabled and verifying both include `snd-msnd-lib.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/msnd/Makefile -->
