# subset-b-006412 ALSA PCMCIA and PowerPC audio research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pcmcia/pdaudiocf/pdaudiocf_core.c -->
# sources/distributed-fs/ceph-client/sound/pcmcia/pdaudiocf/pdaudiocf_core.c

## Purpose

This file is the core hardware setup and lifecycle layer for the Sound Core PDAudioCF PCMCIA capture card. It initializes the `snd_pdacf` object, exposes a proc status entry, controls FPGA reset/powerdown, bridges the AK4117 S/PDIF receiver into ALSA, and restores register state across reinitialization and power management.

## Important APIs, types, and functions

`snd_pdacf_create()` allocates and attaches `struct snd_pdacf` to the ALSA card, initializes `reg_lock` and `ak4117_lock`, and creates `/proc/asound/.../pdaudiocf`. `snd_pdacf_ak4117_create()` resets the FPGA, creates the AK4117 helper with `pdacf_ak4117_read()` and `pdacf_ak4117_write()`, programs FPGA test/control, sample format, LED, and interrupt-enable registers, and installs `snd_pdacf_ak4117_change()` as the lock/error callback. `pdacf_reinit()`, `snd_pdacf_powerdown()`, `snd_pdacf_suspend()`, and `snd_pdacf_resume()` own the restore path.

## Control flow

AK4117 register access waits for the PDAUDIOCF serial-port-busy bit, performs 16-bit port I/O through the FPGA AK interface register, and times out with device errors. Card bring-up calls `pdacf_reset()`, constructs the AK4117 instance, configures 24-bit input and interrupt/LED behavior, then updates LED status from AK4117 lock state. Suspend disables hardware interrupt sources with raw `inw/outw` so the cached register map is preserved, marks the chip suspended, powers down, and resume resets, restores SCR/TCR/IER, reinitializes AK4117, waits briefly for PLL lock, and returns ALSA power state to D0.

## State and persistence behavior

The file persists FPGA state in `chip->regmap`, AK4117 state in `chip->ak4117`, suspend SCR in `chip->suspend_reg_scr`, and status bits in `chip->chip_status`. `reg_lock` protects cached register updates; `ak4117_lock` serializes AK4117 port transactions. Direct raw writes are intentionally used during suspend/powerdown to avoid corrupting the saved register cache.

## Dependencies and integration points

It depends on `pdaudiocf.h` register helpers, ALSA core/proc/power APIs, and `sound/ak4117` receiver support. It is called by the PCMCIA front-end and by `pdaudiocf_pcm.c` close/prepare paths. IRQ and PCM code rely on `chip->ak4117`, interrupt enable bits, and the cached SCR/TCR/IER values established here.

## Risks and test signals

Risks include busy-wait timeout behavior on card removal, stale cached register values after raw port writes, AK4117 interrupt masking mistakes on edge-triggered PCMCIA IRQs, and races between suspend and IRQ/PCM handling. Useful signals are card probe/resume logs, AK4117 lock/rate reporting, proc FPGA revision output, capture start after suspend/resume, and absence of interrupt storms when digital input lock changes.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pcmcia/pdaudiocf/pdaudiocf_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pcmcia/pdaudiocf/pdaudiocf_irq.c -->
# sources/distributed-fs/ceph-client/sound/pcmcia/pdaudiocf/pdaudiocf_irq.c

## Purpose

This file implements the PDAudioCF interrupt path and the PIO transfer routines that drain captured audio samples from the card SRAM FIFO into ALSA's vmalloc PCM buffer. It separates the hard IRQ status/rate check from the threaded IRQ bulk data movement.

## Important APIs, types, and functions

`pdacf_interrupt()` is the top-half handler. It validates chip status, reads `PDAUDIOCF_REG_ISR`, reports SRAM overrun, decides whether a threaded handler is needed, and asks AK4117 to check rate/errors when in real interrupt context. `pdacf_threaded_irq()` computes available FIFO frames from RDP/WDP, drains them, updates `pcm_tdone` and `pcm_hwptr`, and calls `snd_pcm_period_elapsed()`. `pdacf_transfer()` dispatches to mono/stereo, 16/24/32-bit, little/big-endian, and byte-swapped transfer helpers.

## Control flow

The top half ignores stale, unconfigured, or suspended chips, checks FIFO-level/overrun bits, and wakes the threaded handler only when a PCM substream exists. The threaded handler verifies the capture stream is running, computes FIFO occupancy modulo 64 KiB, leaves slack when more than 64 frames are pending, then copies wrapped regions into the ALSA ring buffer. Period notification is done under `reg_lock` only long enough to update counters; the lock is dropped before ALSA callback entry.

## State and persistence behavior

The transfer path mutates `chip->pcm_tdone`, `pcm_hwptr`, and indirectly the PCM ring buffer at `pcm_area`. Format interpretation comes from state precomputed by `pdaudiocf_pcm.c`: `pcm_sample`, `pcm_frame`, `pcm_channels`, `pcm_little`, `pcm_swab`, and `pcm_xor`. No persistent hardware state is created here beyond clearing FIFO data by reading the MD register.

## Dependencies and integration points

It depends on PCMCIA IRQ threading, raw port I/O, AK4117 rate/error checks, and ALSA PCM period notification. `pdaudiocf_pcm.c` sets the runtime fields this file consumes; the PCMCIA driver registers these handlers. It is tightly coupled to FPGA FIFO word packing documented by the transfer helpers.

## Risks and test signals

Risks include off-by-one FIFO occupancy, endian/sign conversion errors, non-atomic access to PCM state during stop/close, and underrun/overrun handling that logs but continues. Test with all advertised formats (`S16`, `S24_3`, `S32`, LE/BE), mono/stereo capture, ring-buffer wraparound, period interrupt cadence, hot-unplug while IRQs are pending, and forced SRAM overrun diagnostics.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pcmcia/pdaudiocf/pdaudiocf_irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pcmcia/pdaudiocf/pdaudiocf_pcm.c -->
# sources/distributed-fs/ceph-client/sound/pcmcia/pdaudiocf/pdaudiocf_pcm.c

## Purpose

This file exposes PDAudioCF as an ALSA capture-only PCM device. It defines hardware capabilities, prepares the FPGA and AK4117 for the selected sample format, starts/stops capture, and reports the current hardware pointer.

## Important APIs, types, and functions

`snd_pdacf_pcm_new()` creates the PCM named `PDAudioCF`, installs capture ops, uses vmalloc managed buffers, and builds AK4117 controls for the capture substream. `pdacf_pcm_capture_open()` advertises rates from 32 kHz through 192 kHz, mono/stereo, and 16/24/32-bit formats. `pdacf_pcm_prepare()` clears SRAM, computes byte-order/sample-format state, programs FPGA data format and AK4117 digital-interface width, enables FIFO-level IRQs, and records buffer/period pointers. `pdacf_pcm_trigger()` validates digital lock/rate and toggles the RECORD bit.

## Control flow

Open stores the active substream. Prepare rejects stale hardware, derives `pcm_little`, `pcm_swab`, `pcm_xor`, `pcm_sample`, and `pcm_frame`, drains existing SRAM data, and synchronizes the FPGA data format with AK4117 `REG_IO`. Start zeroes software counters, verifies AK4117 is locked and the external rate equals `runtime->rate`, increments `pcm_running`, and sets `PDAUDIOCF_RECORD`; stop clears the bit and decrements the run count. Close reinitializes the device and clears the substream pointer.

## State and persistence behavior

Per-stream state is held in `struct snd_pdacf`: runtime format metadata, capture buffer location, buffer and period sizes, `pcm_hwptr`, `pcm_tdone`, and `pcm_running`. Register updates go through the cached helper under `reg_lock`; PCM buffers are vmalloc-backed, not bus-master DMA-backed.

## Dependencies and integration points

It depends on `pdaudiocf_core.c` for AK4117 setup/reinit and on `pdaudiocf_irq.c` for actual data movement and period accounting. ALSA PCM core calls the ops; AK4117 provides external rate/lock validation and user-visible S/PDIF status controls.

## Risks and test signals

Risks include starting capture on a changed external S/PDIF clock, stale `pcm_xor` for signed formats if not reset between prepares, SRAM clear timeout, and mismatches between advertised formats and transfer helper packing. Test open/close/reprepare cycles, all supported formats, start rejection on unlocked or wrong-rate input, pause/resume triggers, and pointer monotonicity across buffer wrap.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pcmcia/pdaudiocf/pdaudiocf_pcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pcmcia/vx/Makefile -->
# sources/distributed-fs/ceph-client/sound/pcmcia/vx/Makefile

## Purpose

This Makefile builds the ALSA PCMCIA Digigram VXPocket module.

## Important APIs, types, and functions

It declares `snd-vxpocket-y := vxpocket.o vxp_ops.o vxp_mixer.o` and wires `obj-$(CONFIG_SND_VXPOCKET) += snd-vxpocket.o`.

## Control flow

Kbuild links the PCMCIA probe/lifecycle code, low-level VX hardware operations, and mixer controls into one module when `CONFIG_SND_VXPOCKET` is enabled.

## State and persistence behavior

There is no runtime state. Build state is controlled entirely by Kconfig and Kbuild object selection.

## Dependencies and integration points

The module depends on the shared VX core APIs used by `vxp_ops.c` and `vxpocket.c`, plus PCMCIA and ALSA core configuration selected elsewhere.

## Risks and test signals

Risks are missing object membership or config drift. Build `CONFIG_SND_VXPOCKET=m/y` and confirm `snd-vxpocket.ko` contains all three objects and resolves `snd_vxpocket_ops` and `vxp_add_mic_controls`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pcmcia/vx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pcmcia/vx/vxp_mixer.c -->
# sources/distributed-fs/ceph-client/sound/pcmcia/vx/vxp_mixer.c

## Purpose

This file adds VXPocket-specific ALSA mixer controls for microphone input level or boost. Common playback, routing, and DSP controls are handled by the shared VX core; this file only covers the analog mic differences between VXPocket and VXPocket440.

## Important APIs, types, and functions

`vxp_add_mic_controls()` initializes `chip->mic_level`, programs the hardware default using `vx_set_mic_level()` or `vx_set_mic_boost()`, and adds either `Mic Capture Volume` for `VX_TYPE_VXPOCKET` or `Mic Boost` for `VX_TYPE_VXP440`. The get/put callbacks read and update `struct snd_vxpocket::mic_level`, validate ranges, and serialize changes with `vx_core::mixer_mutex`.

## Control flow

During VX core control creation, `snd_vxpocket_ops.add_controls` calls `vxp_add_mic_controls()`. Put callbacks compare the requested value against cached `mic_level`; changed values are sent through low-level hardware helpers in `vxp_ops.c` before updating the cache and returning ALSA's changed flag.

## State and persistence behavior

The only persistent mixer state is `mic_level`, interpreted as 0-8 analog level for VXPocket or boolean boost for VXPocket440. Hardware CDSP/MICRO registers are not read back here, so cache correctness depends on serialized ALSA control writes and resume reinitialization elsewhere.

## Dependencies and integration points

It depends on ALSA control APIs, TLV dB scale metadata, `vxpocket.h`, and exported low-level functions from `vxp_ops.c`. It is integrated through `snd_vxpocket_ops`.

## Risks and test signals

Risks include cache/hardware divergence after reset, wrong type-specific control exposure, and invalid dB-scale expectations because the VXPocket scale is coarse and remapped. Test mixer enumeration on both V2 and 440 cards, invalid values, repeated no-op puts, source switching to microphone, and suspend/resume retaining effective mic level.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pcmcia/vx/vxp_mixer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pcmcia/vx/vxp_ops.c -->
# sources/distributed-fs/ceph-client/sound/pcmcia/vx/vxp_ops.c

## Purpose

This file adapts the shared Digigram VX core to the VXPocket PCMCIA register map. It supplies low-level register access, Xilinx/DSP firmware loading, interrupt acknowledgement, pseudo-DMA transfer, codec programming, input source switching, clock source switching, and mic hardware programming.

## Important APIs, types, and functions

`snd_vxpocket_ops` is the exported callback table consumed by `snd_vx_create()`. Important callbacks include `vxp_inb()`, `vxp_outb()`, `vxp_test_and_ack()`, `vxp_validate_irq()`, `vxp_write_codec_reg()`, `vxp_load_dsp()`, `vxp_dma_write()`, `vxp_dma_read()`, `vxp_change_audio_source()`, `vxp_set_clock_source()`, `vxp_reset_dsp()`, `vxp_reset_codec()`, and `vxp_reset_board()`. Public helpers `vx_set_mic_boost()` and `vx_set_mic_level()` are used by the mixer.

## Control flow

Firmware load is staged: boot image, Xilinx bitstream, DSP boot, then DSP image. The Xilinx path enters reprogramming mode, saves CSUER/RUER, handshakes through ISR/RX/TX registers, validates the magic byte, restores registers, resets codec and DSP, and returns errors on handshake failure. Runtime DMA enables pseudo-DMA mode in DIALOG/ICR, transfers 16-bit words with wraparound through the PCM buffer, then disables the mode. Interrupt acknowledgement checks MEMIRQ, pulses ACK, and the shared VX threaded IRQ performs higher-level work.

## State and persistence behavior

`struct snd_vxpocket` caches `regCDSP`, `regDIALOG`, `port`, and `mic_level`. The code mutates cached CDSP/DIALOG bits and writes them to hardware, because several register bits are write-only control state. PCM pipe positions are persisted in shared `struct vx_pipe::hw_ptr`.

## Dependencies and integration points

It depends on `sound/vx_core.h` helpers such as `vx_wait_isr_bit()`, `vx_wait_for_rx_full()`, `snd_vx_load_boot_image()`, and shared PCM/control orchestration. PCMCIA resource setup in `vxpocket.c` supplies the I/O base and IRQ. `vxp_mixer.c` consumes mic helpers; VX core consumes the ops table.

## Risks and test signals

Risks include firmware handshake timeouts, corrupted cached write-only bits, pseudo-DMA alignment mistakes, off-by-one ring wrap during DMA read/write, interrupt ACK races, and model-specific mic bit handling. Test firmware loading through all four indexes, playback/capture wraparound, IRQ validation, digital/line/mic source switching, clock switching, and both VXPocket and VXPocket440 mic paths.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pcmcia/vx/vxp_ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pcmcia/vx/vxpocket.c -->
# sources/distributed-fs/ceph-client/sound/pcmcia/vx/vxpocket.c

## Purpose

This file is the PCMCIA module front-end for Digigram VXPocket and VXPocket440 cards. It handles module parameters, card allocation, PCMCIA resource configuration, IRQ registration, hardware variant detection, firmware setup, suspend/resume, and ALSA card lifetime.

## Important APIs, types, and functions

`vxpocket_probe()` allocates an ALSA card, reserves a card index, calls `snd_vxpocket_new()`, and runs `vxpocket_config()`. `snd_vxpocket_new()` creates a `vx_core` with VXPocket hardware data and `snd_vxpocket_ops`, stores PCMCIA config requirements, and returns the embedded `snd_vxpocket`. `vxpocket_config()` selects VXPocket440 metadata based on CIS product string, requests I/O, registers a shared threaded IRQ using VX core handlers, enables the PCMCIA device, and calls `snd_vxpocket_assign_resources()` to load firmware. `vxpocket_detach()` disconnects and frees safely.

## Control flow

Probe finds a free module slot, honors `enable[]`, creates the ALSA card, creates the VX core, configures PCMCIA, and leaves card registration to the VX firmware/setup path. Config failure unwinds IRQ and PCMCIA resources. Detach marks the core stale, disconnects ALSA, releases IRQ/device resources, and defers card memory free until users close the card.

## State and persistence behavior

Global `card_alloc` tracks occupied module parameter slots. Per-device state lives in `struct snd_vxpocket` and embedded `vx_core`; `link->priv` points to the core. Hardware capabilities are persisted in `chip->hw` and `chip->type`, overwritten for 440 cards.

## Dependencies and integration points

It depends on PCMCIA CIS/resource APIs, ALSA card/module APIs, shared VX core firmware setup, and `vxp_ops.c` for hardware callbacks. It uses `request_threaded_irq()` with `snd_vx_irq_handler` and `snd_vx_threaded_irq_handler`.

## Risks and test signals

Risks include CIS string assumptions, card-index leaks on partial failure, IRQ/resource ordering during detach, and stale state while user file handles remain open. Test insertion/removal, disabled module slot behavior, V2 versus 440 detection, firmware load failure unwind, suspend/resume with card present, and hot-unplug during PCM use.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pcmcia/vx/vxpocket.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pcmcia/vx/vxpocket.h -->
# sources/distributed-fs/ceph-client/sound/pcmcia/vx/vxpocket.h

## Purpose

This header defines the VXPocket private device structure, shared declarations, and PCMCIA hardware bit masks used by `vxpocket.c`, `vxp_ops.c`, and `vxp_mixer.c`.

## Important APIs, types, and functions

`struct snd_vxpocket` embeds `struct vx_core`, stores I/O port, mic level, cached CDSP/DIALOG register values, ALSA card index, and `struct pcmcia_device *`. `to_vxpocket()` converts from `vx_core` to the containing type. The header declares `snd_vxpocket_ops`, `vx_set_mic_boost()`, `vx_set_mic_level()`, and `vxp_add_mic_controls()`.

## Control flow

There is no executable control flow. The macros define how control flow in `vxp_ops.c` manipulates CDSP reset/source/clock/IRQ/mic bits and DIALOG Xilinx/DMA/ACK bits.

## State and persistence behavior

The important persisted state is cached write-only register content in `regCDSP` and `regDIALOG`. Bit masks in this header define which portions of that cache select DSP reset, codec reset, input source, mic mode, IRQ validation, Xilinx reprogramming, pseudo-DMA, and MEMIRQ acknowledgement.

## Dependencies and integration points

It depends on `sound/vx_core.h` and PCMCIA headers. All VXPocket implementation files include it, and the shared VX core indirectly depends on the ops and container layout declared here.

## Risks and test signals

Risks are incorrect bit definitions for VXPocket variants, stale cached register semantics, and container layout assumptions. Build coverage plus hardware tests for reset, IRQ, source selection, and pseudo-DMA mode are the primary signals.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pcmcia/vx/vxpocket.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/ppc/Kconfig -->
# sources/distributed-fs/ceph-client/sound/ppc/Kconfig

## Purpose

This Kconfig file defines ALSA PowerPC sound driver configuration for legacy PowerMac onboard audio and PS3 audio.

## Important APIs, types, and functions

`SND_PPC` gates the submenu on `PPC`. `SND_POWERMAC` depends on `I2C`, `INPUT`, and `PPC_PMAC`, selects `SND_PCM` and `SND_VMASTER`, and builds `snd-powermac`. `SND_POWERMAC_AUTO_DRC` optionally controls automatic dynamic range compression toggling for Tumbler/Snapper. `SND_PS3` depends on `PS3_PS3AV`, selects `SND_PCM`, and builds `snd_ps3`. `SND_PS3_DEFAULT_START_DELAY` provides the driver default silent startup delay.

## Control flow

Kconfig choices determine which Makefile objects are built and which code paths guarded by config macros compile, especially PowerMac PM/auto-DRC behavior and PS3 module defaults.

## State and persistence behavior

There is no runtime state. The selected options become build-time state and default module behavior, including PS3 startup delay.

## Dependencies and integration points

The file integrates the PPC sound subtree with ALSA core, I2C/input subsystems, PowerMac platform support, and PS3 AV support.

## Risks and test signals

Risks include stale dependencies as platform APIs evolve and enabling drivers without required platform services. Test with `allyesconfig`, `allmodconfig`, PowerMac-only, and PS3-only builds, plus dependency checks for `snd-powermac` and `snd_ps3`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/ppc/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/ppc/Makefile -->
# sources/distributed-fs/ceph-client/sound/ppc/Makefile

## Purpose

This Makefile links ALSA PowerPC sound modules for PowerMac and PS3 hardware.

## Important APIs, types, and functions

It builds `snd-powermac` from `powermac.o`, `pmac.o`, `awacs.o`, `burgundy.o`, `daca.o`, `tumbler.o`, `keywest.o`, and `beep.o`. It builds `snd_ps3.o` directly for `CONFIG_SND_PS3`.

## Control flow

Kbuild includes each module according to `CONFIG_SND_POWERMAC` and `CONFIG_SND_PS3`.

## State and persistence behavior

No runtime state exists. Object membership is build metadata and determines which codec-specific functions are available to the PowerMac probe switch.

## Dependencies and integration points

The PowerMac link unit requires all codec/mixer helpers because `powermac.c` may select AWACS, Burgundy, DACA, Tumbler, or Snapper at runtime. PS3 is independent.

## Risks and test signals

Risks are missing object dependencies or dead declarations when Kconfig changes. Build module and built-in configurations and confirm symbols such as `snd_pmac_awacs_init`, `snd_pmac_keywest_init`, and PS3 module init resolve.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/ppc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/ppc/awacs.c -->
# sources/distributed-fs/ceph-client/sound/ppc/awacs.c

## Purpose

This file implements codec programming, mixer controls, optional CUDA amplifier controls, suspend/resume replay, and automute for PowerMac AWACS and Screamer codecs.

## Important APIs, types, and functions

`snd_pmac_awacs_init()` is the exported initialization entry. Low-level writers `snd_pmac_awacs_write()`, `snd_pmac_awacs_write_reg()`, and `snd_pmac_awacs_write_noreg()` program codec registers and maintain `chip->awacs_reg[]`. `snd_pmac_awacs_set_format()` is installed as `chip->set_format`. Numerous ALSA controls are generated through `AWACS_VOLUME` and `AWACS_SWITCH`; optional `struct awacs_amp` controls are used on CUDA amplifier systems. `snd_pmac_awacs_detect_headphone()` and `snd_pmac_awacs_update_automute()` integrate jack detection.

## Control flow

Initialization chooses model-specific mixer sets based on Open Firmware machine compatibility and device id, seeds codec register cache with muted defaults, writes all registers, reads manufacturer/revision, optionally initializes the external amplifier, builds ALSA controls, installs PM and automute callbacks, and updates mute routing. Format changes update the sample-rate bits in codec register 1. Resume restores cached registers, recalibrates Screamer when needed, and replays amplifier state.

## State and persistence behavior

`chip->awacs_reg[0..7]` is the authoritative codec cache. Additional state includes `chip->hp_stat_mask`, `chip->master_sw_ctl`, `speaker_sw_ctl`, `hp_detect_ctl`, and optional `struct awacs_amp` in `chip->mixer_data`. The code uses `reg_lock` around cached register updates.

## Dependencies and integration points

It depends on `pmac.c` for MMIO mapping, control interrupt handling, PCM format callbacks, and `snd_pmac_add_automute()`. It uses AWACS register definitions from `awacs.h`, Open Firmware machine matching, NVRAM history comments, ALSA control/vmaster APIs, and optional CUDA ADB I2C-like amplifier access.

## Risks and test signals

Risks include model-detection mistakes, cached register divergence, long Screamer recalibration delays, a likely typo in `snd_pmac_awacs_put_volume()` returning `oldval != reg`, and fragile automute differences across iMac/PowerBook/G4 variants. Test mixer enumeration per machine family, headphone/speaker automute notifications, suspend/resume audio restoration, rate switching, and external amplifier controls where available.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/ppc/awacs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/ppc/awacs.h -->
# sources/distributed-fs/ceph-client/sound/ppc/awacs.h

## Purpose

This header describes the AWACS/Screamer MMIO register layout and bit fields used by PowerMac PCM, codec, interrupt, sample-rate, mixer, jack-detect, clipping, and DBDMA status code.

## Important APIs, types, and functions

`struct awacs_regs` defines the mapped control, codec control/status, clip count, and byteswap registers. Macros define control interrupt/rate/subframe bits, codec command format, codec register addresses, gain/mux/mute/volume/sample-rate fields, Screamer mic boost, codec status bits, jack sense masks, clip counters, and rate encodings.

## Control flow

No code executes here. The macros drive control flow in `pmac.c`, `awacs.c`, and codec-specific interrupt paths by naming bits that are tested, set, cleared, or cached.

## State and persistence behavior

The header defines hardware state layout rather than storing state. `awacs.c` persists codec values in `chip->awacs_reg[]`; `pmac.c` reads/writes `struct awacs_regs` through MMIO.

## Dependencies and integration points

It is included by `pmac.h`, which makes these definitions available to most PowerMac sound files. The definitions align with Open Firmware resources mapped in `pmac.c`.

## Risks and test signals

Risks are incorrect bit masks or ambiguous reused encodings such as 48/44.1 kHz sharing a rate code. Test by compiling all users and exercising control interrupts, byteswap, jack detection, and all supported sample-rate indexes on real hardware or emulation with register tracing.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/ppc/awacs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/ppc/beep.c -->
# sources/distributed-fs/ceph-client/sound/ppc/beep.c

## Purpose

This file implements the optional PowerMac input-subsystem bell/tone device using the normal audio playback DBDMA path. It synthesizes a small stereo waveform into a coherent DMA buffer and exposes an ALSA mixer control for beep volume.

## Important APIs, types, and functions

`struct pmac_beep` stores running state, volume, cached tone parameters, waveform buffer, DMA address, and input device. `snd_pmac_attach_beep()` allocates state, coherent waveform memory, an input device, and `Beep Playback Volume`. `snd_pmac_beep_event()` handles `EV_SND` `SND_BELL` and `SND_TONE`. `snd_pmac_beep_stop()` and `snd_pmac_detach_beep()` are called from PCM start, suspend/free, and detach paths.

## Control flow

Attach registers an input device named `PowerMac Beep`. On a nonzero tone request, the handler validates frequency against the selected sample rate, refuses to run while playback/capture/beep are active, regenerates the waveform if frequency or volume changed, and starts looped DMA through `snd_pmac_beep_dma_start()`. A zero tone stops DMA under `reg_lock`.

## State and persistence behavior

Beep state persists under `chip->beep`. The waveform cache avoids recomputation for repeated same-frequency/same-volume tones. The beep shares playback DMA, so starting normal PCM calls `snd_pmac_beep_stop()` first.

## Dependencies and integration points

It depends on input core, ALSA controls, coherent DMA allocation, `snd_pmac_rate_index()`, and beep DMA helpers implemented in `pmac.c`. It is optionally attached by `powermac.c` via the `enable_beep` module parameter.

## Risks and test signals

Risks include playback/beep contention, invalid frequency fallback, DMA buffer lifetime during input unregister, and spinlock interactions around event callbacks. Test bell and tone events, volume changes, concurrent PCM playback/capture suppression, module removal, and suspend while a beep is active.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/ppc/beep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/ppc/burgundy.c -->
# sources/distributed-fs/ceph-client/sound/ppc/burgundy.c

## Purpose

This file implements low-level register access, default programming, ALSA controls, and automute for the PowerMac Burgundy codec.

## Important APIs, types, and functions

`snd_pmac_burgundy_init()` is the exported initializer. Register helpers `snd_pmac_burgundy_wcw()/rcw()` and `wcb()/rcb()` access 32-bit word and byte codec registers using AWACS codec command/status cycles. Control helper families implement 0-100 volumes, two-byte volumes, gain/attenuation, word switches, and byte switches. The mixer arrays select common, iMac-specific, and PowerMac-specific controls. `snd_pmac_burgundy_detect_headphone()` and `snd_pmac_burgundy_update_automute()` handle jack routing.

## Control flow

Initialization checks whether the codec appears disabled, writes output/input/gain/attenuation/default volume registers, sets the headphone-detect mask, builds common and model-specific ALSA controls, creates master/speaker/line/headphone switches, registers automute controls, installs detect/update callbacks, and applies initial routing. Control puts write hardware, read back values, and report changes based on hardware-observed state.

## State and persistence behavior

Unlike AWACS, Burgundy control state is mostly read back from hardware rather than cached in a large software register array. Persistent driver state is mainly `chip->hp_stat_mask`, ALSA control pointers, and common `snd_pmac` fields. Register read/write sequences are protected by `reg_lock` for read paths.

## Dependencies and integration points

It depends on AWACS MMIO command/status registers, `burgundy.h` register definitions, Open Firmware `of_machine_is_compatible("iMac")`, ALSA controls, and `snd_pmac_add_automute()` from `pmac.c`. It is selected by `powermac.c` when `snd_pmac_detect()` reports `PMAC_BURGUNDY`.

## Risks and test signals

Risks include busy/extend wait timeouts, inconsistent locking for write helpers, model-specific output mask mistakes, returning success from init when MacOS disabled the codec, and fragile read-back based change detection. Test Burgundy iMac and non-iMac mixer maps, all input/output switches, headphone automute, register timeout logs, and suspend/removal behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/ppc/burgundy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/ppc/burgundy.h -->
# sources/distributed-fs/ceph-client/sound/ppc/burgundy.h

## Purpose

This header provides Burgundy codec register addresses, default initialization constants, output-enable bit masks, headphone-detect masks, and volume offset definitions.

## Important APIs, types, and functions

Macros name input boost/select, gain, per-source volume, capture/output select, mixer volume, master volume, output enable, attenuation, and host-interface registers. Defaults such as `DEF_BURGUNDY_OUTPUTENABLES`, `DEF_BURGUNDY_MORE_OUTPUTENABLES`, and `DEF_BURGUNDY_MASTER_VOLUME` are consumed during codec initialization. Output bits such as `BURGUNDY_HP_LEFT` and detect bits such as `BURGUNDY_HPDETECT_IMAC_UPPER` drive automute.

## Control flow

There is no executable control flow. `burgundy.c` converts these address macros with `BASE2ADDR/ADDR2BASE` and uses the defaults to program startup state.

## State and persistence behavior

The header defines codec state addresses and constants, not software state. The volume offset of 155 is central to converting ALSA 0-100 values into Burgundy hardware volume values.

## Dependencies and integration points

It is included by `burgundy.c` and `powermac.c` includes it for codec-specific declarations through the build unit. It assumes the AWACS codec command transport used by Burgundy access helpers.

## Risks and test signals

Risks are wrong register constants, unsafe default loudness, and incorrect iMac versus PowerMac output masks. Test by comparing register traces against expected startup defaults and exercising all Burgundy controls.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/ppc/burgundy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/ppc/daca.c -->
# sources/distributed-fs/ceph-client/sound/ppc/daca.c

## Purpose

This file implements support for the PowerMac DACA I2C audio codec, including I2C initialization, output volume, deemphasis, amplifier switch, cleanup, and resume replay.

## Important APIs, types, and functions

`struct pmac_daca` embeds `struct pmac_keywest` and caches left/right volume, deemphasis, and amplifier state. `snd_pmac_daca_init()` loads `i2c-powermac`, allocates mixer state, initializes Keywest I2C at address `0x4d`, creates three ALSA mixer controls, and installs cleanup/resume callbacks. `daca_init_client()` programs sample-rate and global config registers; `daca_set_volume()` writes the two-byte analog volume/deemphasis register.

## Control flow

Probe initializes the I2C client, writes DACA defaults, then adds `Deemphasis Switch`, `Master Playback Volume`, and `Power Amplifier Switch`. Control puts validate values, update cached state, and write the affected DACA register. Resume replays sample-rate, amplifier config, and cached volume/deemphasis.

## State and persistence behavior

Mixer state persists in `chip->mixer_data` as `struct pmac_daca`. Hardware state is replayed from that cache because the codec is controlled over I2C and may lose configuration over suspend.

## Dependencies and integration points

It depends on `keywest.c` for dynamic Keywest I2C client discovery, ALSA control APIs, and `pmac.c` model selection. DACA systems are playback-only in `snd_pmac_detect()`, so this codec integrates with PowerMac PCM without capture.

## Risks and test signals

Risks include deferred or missing I2C adapter discovery, leaked mixer data when `snd_pmac_keywest_init()` fails after allocation, unchecked I2C errors in some control paths, and cache mismatch after failed writes. Test DACA probe deferral, mixer writes, amplifier off/on, resume replay, and module removal.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/ppc/daca.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/ppc/keywest.c -->
# sources/distributed-fs/ceph-client/sound/ppc/keywest.c

## Purpose

This file provides a small shared I2C binding layer for PowerMac audio codecs connected through the Keywest/mac-io I2C bus, used by DACA and Tumbler/Snapper.

## Important APIs, types, and functions

`snd_pmac_keywest_init()` registers an I2C driver, records a single global `pmac_keywest` context, scans consecutive adapters for names beginning with `mac-io`, and instantiates a `keywest` I2C client when one was not already created by `i2c-powermac`. `snd_pmac_keywest_cleanup()` unregisters the client and driver. `snd_pmac_tumbler_post_init()` calls the current context's `init_client()` after the I2C client exists.

## Control flow

Initialization refuses concurrent contexts, grabs adapter 0, registers `keywest_driver`, returns immediately if probe already bound a device, otherwise scans adapters and tries `keywest_attach_adapter()`. Probe stores the client in the current context. Cleanup tears down the global context. Tumbler post-init requires a bound client and runs codec-specific initialization.

## State and persistence behavior

Global `keywest_ctx` stores the active audio I2C context and `keywest_probed` remembers that the driver has bound at least once. This intentionally supports only one active PowerMac audio I2C codec context.

## Dependencies and integration points

It depends on Linux I2C core, `i2c-powermac` naming behavior, and `struct pmac_keywest` declarations in `pmac.h`. DACA calls `snd_pmac_keywest_init()` directly; Tumbler/Snapper use this layer plus `snd_pmac_tumbler_post_init()`.

## Risks and test signals

Risks include global singleton conflicts, adapter reference leaks on the `keywest_probed` early return, unsafe logging through `i2c->client` if driver registration fails before a client exists, and assumptions about adapter numbering/names. Test probe deferral, pre-instantiated and manually-instantiated clients, cleanup/reprobe, and DACA/Tumbler coexistence constraints.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/ppc/keywest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/ppc/pmac.c -->
# sources/distributed-fs/ceph-client/sound/ppc/pmac.c

## Purpose

This file is the low-level PowerMac sound engine. It detects supported Open Firmware audio devices, maps AWACS/DBDMA resources, manages PCM playback/capture through DBDMA command rings, handles interrupts, exposes common automute controls, controls power/suspend state, and provides beep DMA helpers.

## Important APIs, types, and functions

Exports include `snd_pmac_new()`, `snd_pmac_pcm_new()`, `snd_pmac_rate_index()`, `snd_pmac_beep_dma_start()`, `snd_pmac_beep_dma_stop()`, `snd_pmac_add_automute()`, `snd_pmac_suspend()`, and `snd_pmac_resume()`. Core internals include `snd_pmac_detect()`, `snd_pmac_pcm_prepare()`, `snd_pmac_pcm_trigger()`, `snd_pmac_pcm_update()`, `snd_pmac_pcm_dead_xfer()`, DBDMA alloc/free/reset helpers, and IRQ handlers for TX/RX/control.

## Control flow

`snd_pmac_new()` allocates `struct snd_pmac`, detects model/capabilities/sample rates, allocates DBDMA command buffers, maps MMIO resources, requests control/TX/RX IRQs, enables the platform sound feature, handles PowerBook-specific input latches, resets DBDMA, and registers a low-level ALSA device. PCM prepare builds a circular DBDMA command ring for periods and constrains the opposite stream to the same rate/format. Trigger programs AWACS rate/byteswap and starts/stops DBDMA. TX/RX interrupts scan completed DBDMA commands, recover from `DEAD` transfers with an emergency command, advance periods, and notify ALSA.

## State and persistence behavior

`struct snd_pmac` persists Open Firmware nodes/resources, mapped registers, stream structures, IRQs, DBDMA command memory, active format/rate, feature flags, automute controls, and codec callback pointers. `struct pmac_stream` persists ring command state and current period. Static `emergency_dbdma` and `emergency_in_use` are global recovery state shared by streams.

## Dependencies and integration points

It depends on PCI/mac-io/Open Firmware resource APIs, PowerMac feature calls, DBDMA definitions, ALSA PCM/control APIs, and codec files that install `set_format`, mixer, suspend/resume, and automute callbacks. `powermac.c` calls this file to create the hardware object and later dispatches codec-specific init.

## Risks and test signals

Risks include fragile platform detection, missing resource cleanup on rare map/request failures, DBDMA DEAD recovery loops, global emergency DBDMA contention, half-duplex constraints, hardware byteswap quirks, and suspend/resume ordering with active streams. Test model detection, playback/capture formats and rates, IRQ period cadence, DEAD recovery, open constraints for duplex, hot suspend/resume, and cleanup after partial probe failure.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/ppc/pmac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/ppc/pmac.h -->
# sources/distributed-fs/ceph-client/sound/ppc/pmac.h

## Purpose

This header defines the shared private interface for the `snd-powermac` module: DBDMA command storage, stream state, hardware model/capability state, callback hooks, Keywest I2C context, and exported functions used by codec, beep, and platform files.

## Important APIs, types, and functions

`struct pmac_dbdma` describes coherent DBDMA command storage. `struct pmac_stream` stores PCM stream state, DBDMA registers, command ring, substream, and current rate/format masks. `enum snd_pmac_model` identifies AWACS, Screamer, Burgundy, DACA, Tumbler, and Snapper. `struct snd_pmac` is the central device object. Function declarations cover low-level creation, PCM creation, beep attachment/control, PM, codec initialization, Keywest I2C, and automute.

## Control flow

No code executes here, but callback fields in `struct snd_pmac` define runtime flow: codec files install `set_format`, `update_automute`, `detect_headphone`, `suspend`, and `resume`; `pmac.c` calls them from PCM/control/PM paths.

## State and persistence behavior

The header defines all persistent PowerMac driver state: resources, MMIO mappings, AWACS register cache, stream rings, IRQs, mixer pointers, controls, feature flags, and codec hooks. It also fixes the maximum DBDMA fragment count at `PMAC_MAX_FRAGS`.

## Dependencies and integration points

It includes ALSA control/PCM, AWACS definitions, ADB/PMU/CUDA/NVRAM, TTY/VT, DBDMA, Open Firmware, machine, and PowerMac feature headers. All PowerMac sound implementation files depend on this contract.

## Risks and test signals

Risks include central-struct ABI drift inside the module, callback misuse, and compile breakage from platform header changes. Test by building every PowerMac codec combination and checking runtime callback installation for each detected model.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/ppc/pmac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/ppc/powermac.c -->
# sources/distributed-fs/ceph-client/sound/ppc/powermac.c

## Purpose

This file is the ALSA platform-driver wrapper for legacy PowerMac onboard audio. It creates the ALSA card, invokes low-level PowerMac detection/setup, dispatches to the proper codec initializer, creates PCM and optional beep support, registers the card, and bridges platform PM callbacks.

## Important APIs, types, and functions

`snd_pmac_probe()` is the platform probe entry. It calls `snd_card_new()`, `snd_pmac_new()`, codec initializers (`snd_pmac_awacs_init()`, `snd_pmac_burgundy_init()`, `snd_pmac_daca_init()`, `snd_pmac_tumbler_init()` plus post init), `snd_pmac_pcm_new()`, optional `snd_pmac_attach_beep()`, and `snd_card_register()`. Module init registers `snd_pmac_driver` and a simple platform device named `snd_powermac`.

## Control flow

Module init registers the driver then creates a matching platform device to force probe on supported PowerMac systems. Probe switches on `chip->model`, fills card names, initializes codec-specific mixer/hardware, creates PCM, marks the chip initialized, optionally attaches beep, and registers the card. Remove frees the card. PM sleep callbacks forward to `snd_pmac_suspend()` and `snd_pmac_resume()`.

## State and persistence behavior

Global `device` stores the synthetic platform device. Module parameters persist requested ALSA index/id and whether PCM beep is enabled. Per-card state is stored as `card->private_data`.

## Dependencies and integration points

It depends on Linux platform driver APIs, ALSA module/card APIs, and all PowerMac codec entry points linked by the Makefile. It is the visible module boundary for `snd-powermac`.

## Risks and test signals

Risks include registering the synthetic device even if driver registration succeeded but device creation failed, codec switch naming drift, and error unwind depending on `snd_card_free()` to release partially initialized low-level resources. Test module load/unload, unsupported hardware path, each codec model, `enable_beep=0/1`, and platform suspend/resume.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/ppc/powermac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/ppc/snd_ps3.c -->
# sources/distributed-fs/ceph-client/sound/ppc/snd_ps3.c

## Purpose

This file implements the PlayStation 3 ALSA playback driver. It maps PS3 audio MMIO and DMA regions, programs the PS3 AV audio mode, manages a noninterleaved stereo DMA ring, handles audio FIFO interrupts, exposes IEC958 controls, and registers a PS3 system-bus sound driver.

## Important APIs, types, and functions

The single global `the_card` is `struct snd_ps3_card_info`. PCM ops include `snd_ps3_pcm_open()`, `close()`, `prepare()`, `trigger()`, and `pointer()`. DMA helpers include `snd_ps3_program_dma()`, `snd_ps3_kick_dma()`, `snd_ps3_wait_for_dma_stop()`, and `snd_ps3_verify_dma_stop()`. AV helpers include `snd_ps3_change_avsetting()`, `snd_ps3_set_avsetting()`, and `snd_ps3_init_avsetting()`. Platform lifecycle is handled by `snd_ps3_driver_probe()`, `snd_ps3_driver_remove()`, `snd_ps3_init()`, and `snd_ps3_exit()`.

## Control flow

Module init checks for PS3 LV1 firmware and registers a PS3 system-bus driver. Probe opens the hypervisor device, maps MMIO, creates a DMA region, sets a 32-bit DMA mask, programs audio base address, allocates IRQ, creates ALSA card/controls/PCM, allocates a null buffer, initializes AV settings with silent data, and registers the card. Playback prepare updates AV rate/width and ring pointers. Trigger start primes silent DMA, starts chained DMA requests, and interrupt handling refills four FIFO stages per empty event, using silent fill for startup delay or underflow recovery before reporting periods.

## State and persistence behavior

All runtime state is global in `the_card`: mapped MMIO, IRQ, AV settings, PCM/substream pointers, DMA ring start/next/last pointers for left and right halves, buffer size, running flag, silent countdown, null buffer, and start delay. `dma_lock` protects ring pointers and running transitions.

## Dependencies and integration points

It depends on PS3 LV1 calls, PS3 system bus, PS3 AV APIs, ALSA PCM/control/memalloc, coherent DMA, and register definitions in `snd_ps3_reg.h`. It exposes a single SPDIF playback PCM with IEC958 controls backed by `ps3av_mode_cs_info`.

## Risks and test signals

Risks include global singleton assumptions, DMA address truncation to 32 bits, underflow recovery latency, silent delay period accounting, IRQ cleanup ordering, incomplete trigger command validation, and synchronization between interrupt and stop. Test module probe/remove, rates 44.1/48/88.2/96 kHz, 16/24-bit BE formats, IEC958 default changes, underflow recovery, stop while IRQs fire, and startup delay behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/ppc/snd_ps3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/ppc/snd_ps3.h -->
# sources/distributed-fs/ceph-client/sound/ppc/snd_ps3.h

## Purpose

This header defines the PS3 sound driver's private data structures, enums, constants, DMA sizing, and driver name.

## Important APIs, types, and functions

Enums identify output channels, DMA fill modes, and left/right channels. `struct snd_ps3_avsetting_info` caches PS3AV audio channel/rate/width/format/source and IEC958 channel-status bytes. `struct snd_ps3_card_info` stores system-bus device, ALSA card/PCM/substream, MMIO, IRQ outlet/number, AV settings, DMA ring pointers, running/silent state, null buffer, and startup delay. Constants define FIFO stage/count/size, DMA block size, preallocation, DMA region size, and audio IOID.

## Control flow

There is no executable logic. The enum values drive control flow in `snd_ps3_program_dma()` and interrupt handling by distinguishing first-fill/running and silent/non-silent programming.

## State and persistence behavior

This header specifies the persistent global state held by `snd_ps3.c`. The left and right DMA rings are represented as separate pointer sets into a split noninterleaved ALSA buffer.

## Dependencies and integration points

It depends on Linux IRQ types and constants from `snd_ps3_reg.h` for DMA size expressions. It is private to the PS3 sound driver.

## Risks and test signals

Risks include constants drifting from hardware register definitions, insufficient preallocation for supported periods, and state fields not covered by locking. Test with compile checks, runtime period constraints, pointer reporting, and lockdep around `dma_lock`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/ppc/snd_ps3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/ppc/snd_ps3_reg.h -->
# sources/distributed-fs/ceph-client/sound/ppc/snd_ps3_reg.h

## Purpose

This header documents and defines the PS3 audio hardware register offsets, field masks, field values, FIFO destination addresses, DMA kick events/statuses, and source/destination encoding used by `snd_ps3.c`.

## Important APIs, types, and functions

It defines interrupt/config registers, `PS3_AUDIO_DMAC_REGBASE()`, `PS3_AUDIO_KICK/SOURCE/DEST/DMASIZE()`, audio mute/buffer pointer/interrupt registers, 3-wire serial control registers, S/PDIF control/status/user-bit registers, and field macros such as `PS3_AUDIO_AX_IE_ASOBEIE()`, `PS3_AUDIO_AO_3WMCTRL_ASOEN()`, `PS3_AUDIO_KICK_EVENT_AUDIO_DMA()`, `PS3_AUDIO_KICK_STATUS_MASK`, and `PS3_AUDIO_AO_3W_LDATA/RDATA()`.

## Control flow

No code executes here. `snd_ps3.c` uses the macros to poll DMA status, clear interrupts, program chained DMA events, reset serial buffers, enable 3-wire output, choose LSB data placement, and target audio FIFO left/right data ports.

## State and persistence behavior

The header describes MMIO state and documented field behavior, including write-one-to-clear status bits, sticky CLEAR behavior, buffer reset semantics, and DMA status progression. Software state is held in `snd_ps3_card_info`.

## Dependencies and integration points

It is consumed by the PS3 sound driver and must match the PS3 audio hardware specification and LV1/PS3AV setup expectations. The DMA sizing macro in `snd_ps3.h` depends on `PS3_AUDIO_DMASIZE_BLOCKS_MASK`.

## Risks and test signals

Risks include incorrect bit positions, stale comments versus hardware behavior, writes to reserved fields, and event-chain mistakes that can starve the FIFO or create interrupt storms. Test with register traces during playback start/stop, underflow recovery, rate/width changes, and DMA channel status polling.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/ppc/snd_ps3_reg.h -->
