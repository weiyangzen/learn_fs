# subset-b-006377 ALSA ISA Sound Driver Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/ad1816a/ad1816a.c -->
# sources/distributed-fs/ceph-client/sound/isa/ad1816a/ad1816a.c

## Purpose

`ad1816a.c` is the card-level ALSA driver for ISA PnP sound cards built around the Analog Devices AD1815/AD1816A/AD18max10 SoundPort family. It discovers matching PnP cards, extracts audio, FM, MPU-401, IRQ, and DMA resources, creates the low-level AD1816A codec object, and wires the codec, timer, mixer, OPL3, and MPU-401 components into one ALSA card.

## Important APIs, Types, and Functions

- Module parameters expose `index`, `id`, `enable`, and `clockfreq`; PnP-derived resource arrays store `port`, `mpu_port`, `fm_port`, `irq`, `mpu_irq`, `dma1`, and `dma2`.
- `snd_ad1816a_pnpids[]` enumerates supported card IDs and their paired audio/MIDI logical devices.
- `snd_card_ad1816a_pnp()` requests and activates the PnP audio and MPU logical devices, then fills the module resource arrays.
- `snd_card_ad1816a_probe()` allocates `struct snd_card` with embedded `struct snd_ad1816a`, calls `snd_ad1816a_create()`, then registers PCM, mixer, timer, optional MPU-401, and optional OPL3 hwdep devices.
- `snd_ad1816a_pnp_detect()` assigns enabled module slots to discovered PnP cards and counts successful devices.
- PM hooks call `snd_ad1816a_suspend()` and `snd_ad1816a_resume()` from the low-level library.
- `alsa_card_ad1816a_init()` and `alsa_card_ad1816a_exit()` register/unregister the `pnp_card_driver`.

## Control Flow

Module init registers the PnP card driver. PnP core calls the detect callback for each matching card. The detect callback scans the static module slot index until an enabled slot is found, then probes that slot. Probe allocation is device-managed through `snd_devm_card_new()`, and resource discovery is delegated to `snd_card_ad1816a_pnp()`. After PnP activation, the driver creates the codec with PnP port/IRQ/DMA values, optionally overrides `chip->clock_freq`, fills card names, and registers ALSA devices in order: PCM, mixer, timer, MPU-401, OPL3, and finally the card. Failure at any stage returns the error and relies on devm cleanup.

## State and Persistence Behavior

Runtime state is mostly in module-scope resource arrays and in the embedded `struct snd_ad1816a`. The static `dev` cursor in `snd_ad1816a_pnp_detect()` persists across PnP callbacks so each card consumes the next enabled ALSA slot. `ad1816a_devices` persists the number of successfully registered devices and is used to fail module load when no card is found. PnP card drvdata stores the registered `struct snd_card` for suspend/resume. No persistent on-disk state is involved.

## Dependencies and Integration Points

The driver depends on Linux ISA PnP card matching, ALSA core card creation, and AD1816A low-level exports from `ad1816a_lib.c`. It integrates optional MIDI through `snd_mpu401_uart_new()` and FM synthesis through `snd_opl3_create()` plus `snd_opl3_hwdep_new()`. It uses `<sound/ad1816a.h>` for chip definitions, `<sound/mpu401.h>` and `<sound/opl3.h>` for auxiliary devices, and `<sound/initval.h>` for SNDRV default parameter arrays.

## Risks and Edge Cases

The driver assumes the first logical PnP device is audio and the second is MPU; bad or unusual firmware resource ordering can misconfigure the card. Missing or busy MPU resources are tolerated by disabling MIDI, but audio PnP activation failure aborts the whole probe. `clockfreq` is accepted only between 5000 and 100000; bad values silently leave hardware default scaling. The detect cursor is static, so only one slot is consumed per callback and a failed probe stops that callback with the error.

## Test Signals

Useful signals are successful module load with one of the listed PnP IDs, `/proc/asound/cards` card names showing AD1816A, functioning playback/capture devices, timer registration, optional `rawmidi` node when MPU resources exist, and OPL3 hwdep presence when FM resources exist. PM testing should verify suspend saves codec state through the low-level library and resume restores mixer/PCM operation.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/ad1816a/ad1816a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/ad1816a/ad1816a_lib.c -->
# sources/distributed-fs/ceph-client/sound/isa/ad1816a/ad1816a_lib.c

## Purpose

`ad1816a_lib.c` is the low-level ALSA implementation for AD1816A-family codecs. It owns register I/O, codec probing, IRQ handling, ISA DMA programming, PCM open/prepare/trigger/pointer callbacks, timer support, mixer controls, and PM register image save/restore.

## Important APIs, Types, and Functions

- Register helpers `snd_ad1816a_busy_wait()`, `snd_ad1816a_in()`, `snd_ad1816a_out()`, `snd_ad1816a_read()`, `snd_ad1816a_write()`, and mask variants serialize access through the chip status and indirect register window.
- `snd_ad1816a_create()` requests the I/O region, IRQ, and two DMA channels, initializes `struct snd_ad1816a`, probes chip version, and resets runtime registers.
- PCM APIs are exported through `snd_ad1816a_pcm()` and the playback/capture ops tables. Prepare callbacks program DMA, sample rate, format, and period count.
- `snd_ad1816a_interrupt()` acknowledges playback, capture, and timer interrupts and calls `snd_pcm_period_elapsed()` or `snd_timer_interrupt()`.
- `snd_ad1816a_timer()` exposes the codec timer through `struct snd_timer_hardware`.
- `snd_ad1816a_mixer()` creates controls from `snd_ad1816a_controls[]`, including volume TLVs, mute switches, capture source, capture gain, mic boost, and 3D controls.
- PM functions save 48 indirect registers into `chip->image[]` and restore them after reinitialization.

## Control Flow

Creation initializes resource sentinels, reserves ports/IRQ/DMA, stores the card and base port, initializes the spinlock, probes the version register, then calls `snd_ad1816a_init()` to disable interrupts, disable playback/capture PIO, enable WSS-related bits, clear DSP config, and power up the chip. PCM open calls `snd_ad1816a_open()` to reject duplicate mode use and enable the appropriate interrupt bit. Prepare disables the stream, programs ISA DMA with autoinit, scales the sample rate when `clock_freq` is set, writes sample format and base count, and returns. Trigger only toggles the playback or capture enable bit. Interrupt handling reads status under the lock, notifies ALSA streams outside that first critical section, then writes interrupt status to acknowledge.

## State and Persistence Behavior

`struct snd_ad1816a` holds the hardware base port, IRQ, DMA channels, current open modes, playback/capture substream pointers, DMA buffer sizes, timer pointer, chip version/hardware ID, optional clock override, and PM register image. The mode bitmask prevents concurrent opens of the same stream or timer and is cleared fully when no open mode remains. Hardware settings are stored in chip registers and are reprogrammed on each prepare; PM persists register values only in memory across suspend.

## Dependencies and Integration Points

This file depends on ISA DMA helpers from `<asm/dma.h>`, ALSA PCM/timer/control APIs, device-managed resource helpers called by the card driver, and register constants from `<sound/ad1816a.h>`. It is consumed by the card-level AD1816A driver and any other code including the AD1816A header exports. It presents normal ALSA PCM, mixer, and timer objects to userspace.

## Risks and Edge Cases

Register access ignores the return value of `snd_ad1816a_busy_wait()` in most helpers, so timed-out hardware may still be read/written after a warning. The period register uses `period_bytes / 4 - 1`; unusual formats or period sizes must match hardware expectations. Playback and capture share the same enable bit value but different registers, which the trigger code handles with an `iscapture` flag. The IRQ handler always returns `IRQ_HANDLED` after acknowledging, so shared-IRQ false positives are not distinguished. Mixer put paths mask user values but rely on ALSA control ranges to keep semantics sane.

## Test Signals

Tests should cover chip version identification, resource rejection on busy ports/IRQs/DMA, playback and capture at supported formats/rates/channels, period interrupts, pointer movement, timer ticks, mixer read/write change reporting, capture source validation, and suspend/resume restoring mixer values. Runtime debug signals include "chip busy" warnings and absence of PCM period callbacks when interrupts are misconfigured.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/ad1816a/ad1816a_lib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/ad1848/Makefile -->
# sources/distributed-fs/ceph-client/sound/isa/ad1848/Makefile

## Purpose

This Makefile builds the ALSA generic AD1848/AD1847/CS4248 ISA driver module. It maps the module object `snd-ad1848.o` to `ad1848.o` and includes it when `CONFIG_SND_AD1848` is enabled.

## Important APIs, Types, and Functions

- `snd-ad1848-y := ad1848.o` defines the object list for the module.
- `obj-$(CONFIG_SND_AD1848) += snd-ad1848.o` connects Kconfig selection to the kernel build.

## Control Flow

Kbuild evaluates the config symbol, compiles `ad1848.c` to `ad1848.o`, links it into `snd-ad1848.o`, and includes that object in the module or built-in image according to the final configuration.

## State and Persistence Behavior

The file has no runtime state. Its persistent behavior is build graph configuration: changes here affect which source files are compiled into the module.

## Dependencies and Integration Points

It depends on the kernel Kbuild system and the `CONFIG_SND_AD1848` Kconfig symbol. The resulting module depends at link/load time on ALSA WSS support used by `ad1848.c`.

## Risks and Edge Cases

The object list is single-source and simple; the main risk is build breakage if the source filename or Kconfig symbol changes without updating this file.

## Test Signals

Build testing with `CONFIG_SND_AD1848=m` should produce `snd-ad1848.ko`; built-in configuration should link the object without unresolved WSS symbols.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/ad1848/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/ad1848/ad1848.c -->
# sources/distributed-fs/ceph-client/sound/isa/ad1848/ad1848.c

## Purpose

`ad1848.c` is a generic non-PnP ISA driver for AD1848, AD1847, CS4248, and compatible WSS-style codecs. It validates user-supplied legacy resources, creates a `struct snd_wss` codec, and registers PCM and mixer devices for a single-DMA WSS card.

## Important APIs, Types, and Functions

- Module parameters configure `index`, `id`, `enable`, `port`, `irq`, `dma1`, and the `thinkpad` special case.
- `snd_ad1848_match()` rejects disabled slots and slots missing mandatory port/IRQ/DMA parameters.
- `snd_ad1848_probe()` allocates the ALSA card, calls `snd_wss_create()`, registers PCM and mixer devices, formats card identity strings, and registers the card.
- PM callbacks call the WSS codec's `suspend()` and `resume()` methods.
- `module_isa_driver(snd_ad1848_driver, SNDRV_CARDS)` registers a legacy ISA driver across standard ALSA card slots.

## Control Flow

The ISA core calls `match` for each slot. Match requires explicit legacy resources because there is no PnP discovery path in this file. Probe creates the card, creates WSS with `port[n]`, `irq[n]`, `dma1[n]`, and no second DMA, and selects `WSS_HW_THINKPAD` when requested. After WSS creation, it creates PCM and mixer devices, fills `driver`, `shortname`, and `longname`, registers the card, and stores drvdata on the ISA device.

## State and Persistence Behavior

All configuration state is module parameter arrays. Per-card runtime state is owned by `struct snd_wss`, stored in `card->private_data`, and by ALSA core objects attached to the card. Suspend/resume state is delegated to WSS callbacks. There is no persistent storage beyond module parameters.

## Dependencies and Integration Points

The driver depends on `sound/wss.h` for codec creation, PCM, mixer, and PM hooks, and on the legacy ISA driver model. It exposes normal ALSA PCM and mixer interfaces and relies on users or platform configuration to provide valid ISA resources.

## Risks and Edge Cases

Because legacy resources are mandatory, autoload without parameters fails with clear "please specify" errors. Incorrect ports may probe the wrong hardware or fail in `snd_wss_create()`. The ThinkPad flag changes hardware type selection and longname; using it on non-ThinkPad hardware may mis-detect codec behavior.

## Test Signals

Build/load tests should cover missing parameter rejection and successful registration with known-good legacy resources. Runtime tests should verify one playback/capture PCM, mixer controls, correct card longname, and PM recovery through WSS suspend/resume.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/ad1848/ad1848.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/adlib.c -->
# sources/distributed-fs/ceph-client/sound/isa/adlib.c

## Purpose

`adlib.c` is a minimal legacy ISA driver for standalone AdLib-compatible FM synthesis cards. It reserves the OPL I/O ports, creates an ALSA OPL3 device and hwdep interface, and registers a card with no PCM path.

## Important APIs, Types, and Functions

- Module parameters expose `index`, `id`, `enable`, and `port`.
- `snd_adlib_match()` requires the slot to be enabled and a concrete port to be supplied.
- `snd_adlib_probe()` allocates the ALSA card, reserves four I/O ports, creates OPL3 with `snd_opl3_create()`, creates the FM hwdep with `snd_opl3_hwdep_new()`, registers the card, and stores drvdata.
- `module_isa_driver()` registers the legacy ISA probe over `SNDRV_CARDS` slots.

## Control Flow

The legacy ISA core calls match and probe. Probe is linear: allocate card, reserve ports with devm, fill strings, create OPL3 using base and base+2, create hardware-dependent FM interface, register card, and attach it to the device. Any failure aborts probe and devm cleanup releases resources.

## State and Persistence Behavior

Runtime state is limited to ALSA card objects and the devm I/O resource stored in `card->private_data`. No mixer, PCM, DMA, IRQ, or suspend state is managed here.

## Dependencies and Integration Points

The file depends on ALSA core, the legacy ISA driver model, and `<sound/opl3.h>`. It integrates with ALSA hwdep userspace for FM programming rather than with PCM playback.

## Risks and Edge Cases

The driver cannot autodetect a port; loading without `port=` is intentionally rejected. The reserved range is only four bytes, matching OPL2/OPL3 register layout, so conflicts with broader sound-card drivers must be avoided. `snd_opl3_create()` is called with integrated access checking; false positives or bus conflicts are the main hardware risks.

## Test Signals

Successful testing shows an ALSA card named "AdLib FM", an OPL hwdep node, and working FM register access through ALSA OPL tools. Failure tests include missing port, busy port, and absent OPL hardware.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/adlib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/als100.c -->
# sources/distributed-fs/ceph-client/sound/isa/als100.c

## Purpose

`als100.c` is the ISA PnP card driver for Avance Logic ALS007/ALS100-family and DT-019X sound cards. It discovers audio, MPU-401, and OPL logical devices, configures a Sound Blaster DSP backend, attaches SB16 PCM/mixer support, and optionally exposes MIDI and OPL3 devices.

## Important APIs, Types, and Functions

- Module parameters expose ALSA slot identity and PnP-filled resource arrays for audio, MPU, FM, IRQ, MPU IRQ, 8-bit DMA, and 16-bit DMA.
- `struct snd_card_als100` stores the requested PnP devices and the `struct snd_sb` backend.
- `snd_als100_pnpids[]` maps PnP card IDs to logical devices and SB hardware type (`SB_HW_DT019X` or `SB_HW_ALS100`).
- `snd_card_als100_pnp()` requests/activates audio, MPU, and OPL devices and extracts resource assignments, with DT-019X-specific DMA ordering.
- `snd_card_als100_probe()` creates the ALSA card, calls `snd_sbdsp_create()`, registers SB16 PCM and mixer, creates optional MPU and OPL3 devices, and registers the card.
- PM hooks suspend/resume SB mixer state and reset the DSP on resume.

## Control Flow

PnP detect scans for an enabled ALSA slot, then calls probe for one card. Probe allocates card-private `struct snd_card_als100`, activates PnP devices, normalizes DT-019X to single-DMA operation, creates the SB DSP with the PnP resources, fills card names according to hardware type, and registers core audio. Optional MPU and OPL devices are attempted after PCM/mixer setup; failure to create them logs an error but does not abort unless OPL timer or hwdep creation fails after OPL detection succeeded.

## State and Persistence Behavior

The driver keeps module-scope resource arrays, a static detect cursor, a successful-device counter, and per-card PnP/backend pointers in `struct snd_card_als100`. PnP drvdata stores the ALSA card for PM. Runtime PCM/mixer state is owned by the SB helper layer. No persistent filesystem state exists.

## Dependencies and Integration Points

The driver depends on Linux PnP card APIs and ALSA SB, MPU-401, and OPL3 helper libraries. It integrates with `snd_sb16dsp_pcm()`, `snd_sbmixer_new()`, `snd_mpu401_uart_new()`, `snd_opl3_timer_new()`, and `snd_opl3_hwdep_new()`.

## Risks and Edge Cases

Optional MPU/OPL logical devices may be absent or fail activation; the code disables those features and continues. DT-019X cards use a different DMA layout and force no 16-bit DMA, while ALS100-class cards use both DMA entries. Invalid PnP resources can cause SB DSP creation failure. The OPL path aborts if timer/hwdep creation fails after hardware detection, making auxiliary device setup part of probe success in that case.

## Test Signals

Useful tests include PnP matching for every table variant, successful SB16 PCM playback/capture, mixer controls, DT-019X single-DMA behavior, optional MPU rawmidi, OPL3 timer/hwdep creation, and PM paths preserving mixer values after DSP reset.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/als100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/azt2320.c -->
# sources/distributed-fs/ceph-client/sound/isa/azt2320.c

## Purpose

`azt2320.c` is the ISA PnP ALSA driver for Aztech AZT2320 and related AZT2316/AZT300x cards. It activates PnP resources, sends a Sound-Blaster-style command sequence to enable WSS mode, creates a WSS codec backend, and attaches PCM, mixer, timer, optional MIDI, and optional OPL3 support.

## Important APIs, Types, and Functions

- Module parameters provide identity and PnP-filled resource arrays for SB command port, WSS port, MPU port, FM port, IRQ, MPU IRQ, and two DMA channels.
- `struct snd_card_azt2320` tracks device number, audio PnP device, MPU PnP device, and WSS chip pointer.
- `snd_azt2320_pnpids[]` lists supported Aztech/PB/AT card IDs.
- `snd_card_azt2320_pnp()` activates audio and optional MPU logical devices and reads port/DMA/IRQ resources.
- `snd_card_azt2320_command()` polls the DSP command port and writes command bytes.
- `snd_card_azt2320_enable_wss()` sends `0x09, 0x00` and waits to enable WSS mode.
- `snd_card_azt2320_probe()` creates WSS PCM/mixer/timer and optional MPU/OPL devices.

## Control Flow

PnP detect scans for an enabled slot and probes one card. Probe allocates card-private data, activates PnP resources, enables WSS mode through the legacy command port, creates WSS at the WSS resource port, registers PCM/mixer/timer, then attempts MPU and OPL3 creation when resources are valid. Card registration is last, and drvdata is stored on success.

## State and Persistence Behavior

Module arrays retain the resource assignments derived from PnP. Per-card state stores PnP device pointers and, intendedly, the WSS chip pointer. Suspend/resume obtains the card from PnP drvdata and delegates state save/restore to WSS callbacks. Hardware configuration is volatile and reestablished by probe/resume logic; no disk persistence is used.

## Dependencies and Integration Points

The driver depends on Linux PnP and raw ISA I/O (`inb`, `outb`, `mdelay`) for the Aztech WSS enable sequence. It integrates with ALSA WSS helpers, MPU-401 UART, and OPL3 helpers. It uses WSS timer support for the card timer.

## Risks and Edge Cases

The command polling loop is time-based and can fail with `-EBUSY` if the command port never becomes writable. The code declares `acard->chip` and PM uses it, but the probe path creates a local `chip` and does not assign it to `acard->chip`; that makes the PM callbacks dereference an uninitialized/null pointer if enabled and exercised. Optional MPU failure is tolerated. Unsupported AZT2316 cards require manual options according to the file comment because autoprobe is not reliable.

## Test Signals

Tests should verify WSS enable command success, WSS PCM/mixer/timer creation, optional MIDI/OPL creation, and card longname resources. PM testing is important because the chip pointer storage issue is a high-value regression signal. Failure tests should cover command timeout and missing optional MPU resources.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/azt2320.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/cmi8328.c -->
# sources/distributed-fs/ceph-client/sound/isa/cmi8328.c

## Purpose

`cmi8328.c` is a legacy ISA driver for jumper-configured C-Media CMI8328 cards, such as the AudioExcel AV500. It probes a small fixed set of base ports, programs CMI8328 configuration registers, creates a CS4231/WSS codec, exposes OPL3 and optional MPU-401/gameport devices, and preserves chip configuration across PM.

## Important APIs, Types, and Functions

- Static `cmi8328_ports[]` defines the only probed base addresses.
- Module parameters configure card identity, WSS IRQ/DMA, optional MPU port/IRQ, and optional gameport.
- `struct snd_cmi8328` stores base port, saved config bytes, WSS config byte, ALSA card, WSS chip, and optional gameport pointer.
- `snd_cmi8328_cfg_read()` and `snd_cmi8328_cfg_write()` perform the magic config-register access sequence.
- `snd_cmi8328_probe()` validates/configures hardware, picks free resources when set to auto, creates WSS PCM/mixer/timer, configures optional MPU and hardwired OPL3, registers the card, and optionally registers a gameport.
- `snd_cmi8328_remove()`, suspend, and resume disable/restore chip config and WSS state.

## Control Flow

Probe starts by reading CFG1 from the slot's fixed base port. It rejects invalid `0xff`, writes the SB-disable bit because enabling SB breaks WSS, disables CD-ROM and MPU/CD-ROM IRQ/DMA, then resolves IRQ and DMA resources using legacy find helpers when needed. It encodes WSS IRQ/DMA into a byte written directly to the base port. After ALSA card allocation, it creates WSS at `port + 4`, registers PCM/mixer, renames WSS Aux controls to CD/Synth names, attempts the WSS timer, resolves and programs MPU resources, creates OPL3 at hardwired `0x388`, fills card strings, registers the card, and then enables/registers gameport if requested.

## State and Persistence Behavior

The driver maintains per-slot module parameter arrays and per-card `struct snd_cmi8328`. Hardware configuration is in CFG1-CFG3 plus the WSS config byte written to the base port. Suspend saves CFG1-CFG3, enters D3hot, and delegates WSS suspend; resume restores CFG registers, rewrites WSS config, resumes WSS, and returns to D0. Remove disables SB/gameport extras and CD/MPU-related config.

## Dependencies and Integration Points

The file depends on legacy ISA probing, ALSA WSS, OPL3, MPU-401 UART, ISA DMA/IRQ/resource helpers, and optionally the Linux gameport subsystem. It integrates OPL3 as a hardwired device and uses `snd_ctl_rename_id()` to present WSS Aux controls using board-specific labels.

## Risks and Edge Cases

The warning that the SB disable bit must never be cleared is critical; code changes around CFG1 can make WSS stop working. The `dma2s[dma1[ndev] % 4]` lookup depends on DMA1 being one of the validated low DMA channels. Auto MPU resource discovery logs errors but does not abort if unavailable. Gameport registration occurs after card registration, so gameport failure is non-fatal and may leave audio usable. Probe writes hardware config before full resource acquisition; failed probes may leave the card partially disabled/configured.

## Test Signals

Test signals include detection only at the four fixed ports, correct rejection of invalid CFG1, WSS PCM/mixer operation, renamed CD/Synth controls, optional full-duplex DMA2 behavior, OPL3 hwdep at 0x388, optional MPU UART, optional gameport at 0x200, and suspend/resume restoring CFG registers and WSS audio.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/cmi8328.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/cmi8330.c -->
# sources/distributed-fs/ceph-client/sound/isa/cmi8330.c

## Purpose

`cmi8330.c` supports C-Media CMI8330 and CMI8329 ISA sound cards that expose both AD1848/WSS and SB16-compatible functions. It can use ISA PnP or manual legacy resources, creates both WSS and SB backends, presents one ALSA PCM whose playback and capture directions are delegated to different chip drivers, and builds a CMI-specific mixer over WSS extended registers.

## Important APIs, Types, and Functions

- Module parameters configure SB, WSS, FM, MPU, and PnP/legacy behavior.
- `struct snd_cmi8330` stores optional PnP logical devices, card pointer, WSS/SB backends, the wrapper PCM, per-direction copied PCM ops, and card type.
- `snd_cmi8330_controls[]` defines the main CMI extended mixer controls. Optional SB mixer support is compiled out by default.
- `snd_cmi8330_pnp()` activates capture/WSS, playback/SB16, and MPU logical devices and populates resources.
- `snd_cmi8330_pcm()` copies SB16 and WSS PCM ops and replaces only the open callbacks so each substream points at the correct backend.
- `snd_cmi8330_probe()` creates WSS and SB devices, verifies hardware type, initializes CMI extended registers, creates mixer and PCM, then optional OPL3/MPU.
- ISA and PnP detect/probe paths share `snd_cmi8330_card_new()` and `snd_cmi8330_probe()`.

## Control Flow

Module init registers legacy ISA and, when available, PnP card drivers. Legacy match requires enabled, non-PnP slot and explicit WSS/SB ports. PnP detect chooses the next enabled PnP slot, allocates a card, activates PnP resources, then runs the shared probe. The shared probe creates a WSS codec at `wssport + 4`, verifies it reports `WSS_HW_CMI8330`, creates an SB16 DSP backend and verifies `SB_HW_16`, switches WSS to MODE2, writes the default CMI mixer image to registers 16-26, adds mixer controls, creates the hybrid PCM, optionally creates OPL3 and MPU, fills card names, and registers.

## State and Persistence Behavior

State is split across module resource arrays, static registration flags, per-card WSS and SB backend state, and copied PCM ops in `struct snd_cmi8330`. The hybrid PCM mutates `substream->private_data` at open time from the wrapper card object to either `struct snd_sb` or `struct snd_wss`, then invokes the original backend open. Suspend changes power state, suspends WSS, and saves SB mixer state; resume resets SB DSP, calls the SB mixer suspend routine again in the current code, resumes WSS, and returns to D0.

## Dependencies and Integration Points

The file depends on ALSA WSS, SB16 DSP, optional SB mixer, OPL3, MPU-401 UART, legacy ISA, and PnP card APIs. The CMI8330-specific mixer uses WSS control macros over CMI extended register numbers. It integrates two independent low-level PCM implementations behind one ALSA PCM object.

## Risks and Edge Cases

The per-direction PCM private-data swap is subtle: backend ops must continue to expect their original chip type after open. The compile-time `PLAYBACK_ON_SB` choice determines whether full-duplex routing uses SB for playback and WSS for capture; changing it flips behavior. PnP device ordering distinguishes CMI8329 by a fourth logical device ID. Resume calls `snd_sbmixer_suspend()` rather than a resume helper, which is suspicious and should be regression-tested. Manual legacy mode requires correct resources for both chips.

## Test Signals

Coverage should include legacy parameter validation, PnP resource extraction, WSS/SB hardware verification failures, hybrid PCM playback and capture opening the correct backend, full-duplex behavior, extended mixer controls, optional FM/MPU setup, and PM tests that verify SB mixer state after resume.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/cmi8330.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/cs423x/Makefile -->
# sources/distributed-fs/ceph-client/sound/isa/cs423x/Makefile

## Purpose

This Makefile builds the ALSA CS423x ISA driver modules. It defines one module for generic CS4231 cards and one module for CS4232/CS4235/CS4236/CS4237/CS4238/CS4239-class cards, with the latter linked from the card driver and its CS4236 extension library.

## Important APIs, Types, and Functions

- `snd-cs4231-y := cs4231.o` defines the generic CS4231 module.
- `snd-cs4236-y := cs4236.o cs4236_lib.o` combines the CS423x card driver with CS4236-family low-level extensions.
- `obj-$(CONFIG_SND_CS4231)` and `obj-$(CONFIG_SND_CS4236)` connect Kconfig symbols to module objects.

## Control Flow

Kbuild compiles the listed objects and links them into `snd-cs4231.o` or `snd-cs4236.o` according to configuration. `cs4236_lib.o` is linked only into the CS4236-family module from this Makefile.

## State and Persistence Behavior

There is no runtime state. The file persistently defines build composition and therefore which low-level helpers are available in each module.

## Dependencies and Integration Points

It depends on kernel Kbuild and `CONFIG_SND_CS4231`/`CONFIG_SND_CS4236`. The resulting modules integrate with ALSA WSS and, for CS4236, the extension library in the same directory.

## Risks and Edge Cases

The main risk is unresolved symbols or missing functionality if `cs4236_lib.o` is removed from `snd-cs4236-y` or if Kconfig symbol names drift.

## Test Signals

Build with `CONFIG_SND_CS4231=m` and `CONFIG_SND_CS4236=m` should produce separate modules, and `snd-cs4236.ko` should contain the exported CS4236 creation, PCM, and mixer paths.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/cs423x/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/cs423x/cs4231.c -->
# sources/distributed-fs/ceph-client/sound/isa/cs423x/cs4231.c

## Purpose

`cs4231.c` is a generic legacy ISA ALSA driver for CS4231-compatible WSS codecs. It requires manually supplied legacy resources, creates WSS PCM/mixer/timer devices, and optionally attaches an MPU-401 UART.

## Important APIs, Types, and Functions

- Module parameters expose ALSA identity plus `port`, `mpu_port`, `irq`, `mpu_irq`, `dma1`, and `dma2`.
- `snd_cs4231_match()` validates that the slot is enabled and has concrete port, IRQ, and primary DMA settings.
- `snd_cs4231_probe()` allocates the card, creates the WSS codec, registers PCM, mixer, timer, optional MPU-401, and the card.
- PM callbacks delegate suspend/resume to the WSS chip callbacks.
- `module_isa_driver()` registers the legacy ISA driver across standard card slots.

## Control Flow

ISA match rejects disabled or under-specified slots. Probe creates a card, calls `snd_wss_create()` with optional second DMA, stores `chip` in `card->private_data`, creates PCM, fills card naming, creates mixer and timer, optionally creates MPU-401 after normalizing auto IRQ to polled mode `-1`, registers the card, and stores drvdata.

## State and Persistence Behavior

Configuration persists in module parameter arrays. Runtime codec state is owned by `struct snd_wss`. The second DMA controls whether longname reports single or dual DMA. Suspend/resume state is handled by WSS. No on-disk persistence exists.

## Dependencies and Integration Points

The driver depends on ALSA WSS helper APIs, the legacy ISA driver model, and optional MPU-401 UART support. Userspace sees ALSA PCM, mixer, timer, and optional rawmidi interfaces.

## Risks and Edge Cases

Like other non-PnP ISA drivers, incorrect resources are the primary risk. MPU setup is optional and warning-only. The driver calls WSS hardware auto-detection, so cards that require CS4236-style control ports belong in the CS423x driver rather than here.

## Test Signals

Tests should cover parameter rejection, single and dual DMA card naming, PCM playback/capture, mixer controls, timer events, optional MIDI creation, and WSS PM restore.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/cs423x/cs4231.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/cs423x/cs4236.c -->
# sources/distributed-fs/ceph-client/sound/isa/cs423x/cs4236.c

## Purpose

`cs4236.c` is the card-level driver for CS4232 and CS4235-CS4239 ISA sound chips. It supports manual legacy ISA resources, PnP BIOS devices, and ISA PnP card devices, discovers WSS/control/MPU/FM/SB resources, chooses generic WSS or CS4236-family enhanced setup, and registers PCM, mixer, timer, OPL3, and optional MPU devices.

## Important APIs, Types, and Functions

- Module parameters configure identity, PnP selection, WSS port, control port, MPU/FM/SB ports, IRQs, and two DMA channels.
- `struct snd_card_cs4236` stores the WSS chip and PnP logical device pointers.
- `snd_cs423x_pnpbiosids[]` and `snd_cs423x_pnpids[]` cover many CS423x board IDs.
- `snd_cs423x_pnp_init_wss()`, `_ctrl()`, and `_mpu()` activate logical devices and fill resources.
- `snd_card_cs423x_pnp()` handles PnP BIOS pairing of WSS and control devices; `snd_card_cs423x_pnpc()` handles ISA PnP card logical devices.
- `snd_cs423x_probe()` creates the chip via `snd_cs4236_create()`, selects enhanced or generic PCM/mixer registration based on hardware flags, and attaches timer/OPL3/MPU.
- ISA, PnP BIOS, and PnP card detect paths share card allocation and common probe.

## Control Flow

Module init registers the legacy ISA driver and, when PnP is enabled, both PnP BIOS and PnP card drivers. Legacy match requires explicit port, cport, IRQ, and DMA unless PnP is selected for that slot. PnP BIOS detect skips ISA PnP devices, finds a sibling control device by changing the PnP ID suffix, activates resources, then probes. PnP card detect requests WSS, control, and optional MPU logical devices, activates each requested resource set, then probes. The shared probe reserves optional SB port, calls `snd_cs4236_create()`, chooses enhanced `snd_cs4236_pcm()`/`snd_cs4236_mixer()` when `WSS_HW_CS4236B_MASK` is present, otherwise generic WSS PCM/mixer, sets card names, creates timer, optional OPL3 and MPU, and registers the card.

## State and Persistence Behavior

State includes per-slot module resource arrays, registration flags for each driver type, static slot cursors in PnP detect paths, and per-card `struct snd_card_cs4236`. Runtime codec state is owned by `struct snd_wss` and possibly extended by `cs4236_lib.c`. PnP drvdata stores the card for suspend/resume. Suspend/resume delegates entirely to the chip's callbacks, which may be generic WSS or enhanced CS4236 callbacks.

## Dependencies and Integration Points

The file depends on ALSA WSS and CS4236 extension exports, PnP BIOS/card APIs, legacy ISA registration, OPL3 helpers, and MPU-401 UART. It integrates older CS4232-compatible boards and newer CS4235+ chips through one common probe that falls back gracefully when enhanced hardware is not detected.

## Risks and Edge Cases

Resource extraction varies by PnP table entry; some boards lack MPU logical devices or second DMA. For CS4236+ chips, a valid control port is mandatory and verified by `cs4236_lib.c`; wrong cport causes probe failure. The PnP BIOS sibling lookup assumes a related ID convention. Optional SB port is only reserved, not used for SB PCM here. Registration returns success if any of the ISA/PnP registrations succeeds, so mixed availability must be tested.

## Test Signals

Test signals include legacy resource validation, PnP BIOS and ISA PnP detection, correct cport validation, enhanced mixer presence on CS4235+ hardware, generic WSS fallback on older hardware, timer, OPL3, optional MPU, and suspend/resume restoring enhanced registers.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/cs423x/cs4236.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/cs423x/cs4236_lib.c -->
# sources/distributed-fs/ceph-client/sound/isa/cs423x/cs4236_lib.c

## Purpose

`cs4236_lib.c` provides the low-level extensions for CS4235, CS4236B, CS4237B, CS4238B, and CS4239 chips on top of the generic WSS layer. It validates the CS4236 control port, initializes extended/control registers, installs custom PCM rate/format callbacks, implements PM register image save/restore, and creates enhanced mixer, IEC958, and 3D controls.

## Important APIs, Types, and Functions

- `snd_cs4236_ext_map[]` is the default image for 18 extended indirect registers.
- `snd_cs4236_ctrl_out()` and `snd_cs4236_ctrl_in()` access control registers through `cport + 3/4` while updating `chip->cimage`.
- `snd_cs4236_xrate()` applies an eight-entry ratnum rate constraint and `divisor_to_rate_register()` converts ALSA selected divisors into DAC/ADC rate register values.
- `snd_cs4236_playback_format()` and `snd_cs4236_capture_format()` set WSS format registers and CS4236 DAC/ADC rate registers.
- `snd_cs4236_create()` wraps `snd_wss_create()`, validates enhanced hardware and cport, initializes control and extended registers, and overrides WSS callbacks.
- `snd_cs4236_pcm()` creates WSS PCM and clears joint-duplex info.
- Mixer helper families implement single/double controls over extended registers, control registers, and mixed WSS/extended registers.
- `snd_cs4236_mixer()` selects CS4235/CS4239 or CS4236-family control sets, then adds hardware-specific 3D and IEC958 controls.

## Control Flow

Creation first creates a WSS chip, then returns it unchanged if enhanced CS4236 bits are absent. Enhanced chips require a non-auto control port; the library reads control register 1 and extended version and requires them to match. It then initializes control registers for reset/digital-output defaults, installs custom rate and format callbacks, installs PM callbacks, writes the default extended image, and initializes compatible WSS registers. PCM creation delegates to `snd_wss_pcm()` and adjusts flags. Mixer creation adds a base control table based on hardware type, then appends 3D controls for CS4235/CS4237B/CS4238B variants and IEC958 controls for CS4237B/CS4238B.

## State and Persistence Behavior

State is stored in the generic `struct snd_wss`: `image[]` for base WSS registers, `eimage[]` for CS4236 extended registers, `cimage[]` for control registers, callback pointers for rate/format/PM behavior, and the control port. Suspend snapshots base registers 0-31, all 18 extended registers, and control registers 2-8. Resume enters MCE, restores base registers except special/version registers, restores extended/control registers except selected reserved control register 7, and exits MCE.

## Dependencies and Integration Points

The file depends on generic WSS helper functions, CS4236 register macros from `<sound/wss.h>`, ALSA PCM constraint APIs, ALSA control/TLV APIs, IEC958 constants from `<sound/asoundef.h>`, and ISA I/O. It is linked into `snd-cs4236.o` and used by `cs4236.c`.

## Risks and Edge Cases

The cport validation is critical; a wrong control port may otherwise write arbitrary ISA I/O locations. Rate selection depends on `params->rate_den` matching the ratnum constraint; unexpected divisors trigger `snd_BUG()`. IEC958 enable toggles MCE and resets channel-status state with timing delays, which is sensitive to locking and hardware timing. The mixer put helper for different left/right extended registers writes both values; correctness depends on the cached image matching hardware. Hardware-specific control tables differ substantially, so wrong hardware ID produces incorrect mixer semantics.

## Test Signals

Tests should cover enhanced and fallback creation, cport mismatch failure, rate-constraint negotiation, playback/capture format changes, suspend/resume image restore, mixer get/put change reporting, CS4235/CS4239 versus CS4236B/CS4237B/CS4238B control sets, IEC958 enable and channel status controls, and 3D controls on the appropriate chip IDs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/cs423x/cs4236_lib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/es1688/Makefile -->
# sources/distributed-fs/ceph-client/sound/isa/es1688/Makefile

## Purpose

This Makefile builds the ESS ES1688/ES688 ALSA ISA modules. It separates the reusable ES1688 low-level library from the card driver and links the library into both the normal ES1688 driver and the Gravis UltraSound Extreme driver.

## Important APIs, Types, and Functions

- `snd-es1688-lib-y := es1688_lib.o` defines the low-level library module object.
- `snd-es1688-y := es1688.o` defines the ES1688 card driver object.
- `obj-$(CONFIG_SND_ES1688) += snd-es1688.o snd-es1688-lib.o` builds both card and library modules for ES1688.
- `obj-$(CONFIG_SND_GUSEXTREME) += snd-es1688-lib.o` reuses the low-level library for GUS Extreme support.

## Control Flow

Kbuild compiles and links the ES1688 card and library objects according to selected config symbols. The library object can be built without the standalone ES1688 card module when another driver needs its exported functions.

## State and Persistence Behavior

The Makefile has no runtime state. Its persistent effect is build composition and symbol availability for drivers that depend on `es1688_lib.o`.

## Dependencies and Integration Points

It depends on Kbuild and `CONFIG_SND_ES1688`/`CONFIG_SND_GUSEXTREME`. The exported functions in `es1688_lib.c` form the integration point for the standalone and GUS Extreme paths.

## Risks and Edge Cases

Because two configs can reference `snd-es1688-lib.o`, build changes must avoid duplicate or missing module-object definitions. Removing the library from either object list can break external users of its exported symbols.

## Test Signals

Build testing should cover `CONFIG_SND_ES1688=m`, `CONFIG_SND_GUSEXTREME=m`, and both enabled together, confirming the library object is produced and linked without duplicate symbol issues.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/es1688/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/es1688/es1688.c -->
# sources/distributed-fs/ceph-client/sound/isa/es1688/es1688.c

## Purpose

`es1688.c` is the card-level ALSA driver for ESS ES1688/ES688/ES968 AudioDrive ISA cards. It supports legacy ISA probing with optional auto resource selection and a single-card ES968 ISA PnP path, then uses the reusable ES1688 low-level library to create PCM, mixer, optional OPL3, and optional MPU-401 devices.

## Important APIs, Types, and Functions

- Module parameters configure identity, PnP selection, audio port, FM port, MPU port, IRQs, and 8-bit DMA.
- `snd_es1688_match()` selects enabled non-PnP legacy slots.
- `snd_es1688_legacy_create()` chooses free IRQ/DMA if requested and probes possible base ports `0x220`, `0x240`, and `0x260` unless a port is supplied.
- `snd_es1688_probe()` registers PCM, mixer, card names, optional OPL3, optional MPU-401, and the card.
- ES968 PnP helpers activate the single audio logical device and call `snd_es1688_create()`.
- Module init prefers the ES968 PnP path; if no PnP card is probed, it unregisters PnP and falls back to legacy ISA registration.

## Control Flow

In legacy mode, ISA match selects enabled slots with PnP disabled. Probe allocates a card with embedded `struct snd_es1688`, creates the low-level chip using either configured or iterated base ports, then calls the common ALSA-device setup. In PnP mode, module init registers the ES968 PnP card driver and returns success immediately if one card is probed; otherwise it unregisters PnP and registers the legacy ISA driver. The common setup creates PCM and mixer, fills names, defaults FM port to the audio port when auto, attempts OPL3, creates MPU only if a real MPU IRQ and chip MPU port are present, and registers the card.

## State and Persistence Behavior

State includes module resource arrays, optional PnP enable flags, and `snd_es968_pnp_is_probed`, which prevents multiple ES968 PnP cards and controls exit behavior. Per-card state is the embedded `struct snd_es1688` from the low-level library. PM for this card driver only changes ALSA power state and resets the chip on resume; detailed mixer/PCM state persistence is limited.

## Dependencies and Integration Points

The file depends on the ES1688 low-level exports from `es1688_lib.c`, ALSA OPL3 and MPU-401 helpers, legacy ISA registration, and ISA PnP card APIs. It also uses ALSA legacy free-resource helpers for auto IRQ/DMA selection.

## Risks and Edge Cases

Module init does not check the return value of `pnp_register_card_driver()` before testing whether a card was probed; if registration fails, it still falls back to ISA. ES968 PnP is single-card only by design. Legacy autoprobe iterates ports but uses the first selected IRQ/DMA for all attempts. MPU creation requires `mpu_irq` to be real and `chip->mpu_port` to have been accepted by the low-level create path.

## Test Signals

Tests should cover ES968 PnP success and fallback, legacy auto IRQ/DMA selection, base-port probing, PCM/mixer registration, FM port defaulting and OPL3 creation, MPU creation, single-card PnP guard reset on remove, and resume reset behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/es1688/es1688.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/es1688/es1688_lib.c -->
# sources/distributed-fs/ceph-client/sound/isa/es1688/es1688_lib.c

## Purpose

`es1688_lib.c` is the reusable low-level driver for ESS ES1688/ES688/ES488-family AudioDrive hardware. It implements DSP command/register access, reset/probe/init, IRQ and DMA management, half-duplex PCM playback/capture, mixer controls, and exported creation/PCM/mixer APIs used by the standalone ES1688 and GUS Extreme drivers.

## Important APIs, Types, and Functions

- DSP/register helpers include `snd_es1688_dsp_command()`, `snd_es1688_dsp_get_byte()`, `snd_es1688_write()`, `snd_es1688_read()`, `snd_es1688_mixer_write()`, and `snd_es1688_mixer_read()`.
- `snd_es1688_reset()` performs hardware reset and enables ESS extended mode.
- `snd_es1688_probe()` performs the ESS enable sequence, resets the chip, reads identification, rejects ES488 and unknown chips, and disables IRQ/DMA before initialization.
- `snd_es1688_init()` configures joystick/OPL/MPU bits, IRQ bits, DMA bits, and reset state.
- PCM callbacks program custom ES1688 sample-rate dividers, ISA DMA, format/channel command sequences, trigger register `0xb8`, and pointer reporting.
- `snd_es1688_create()` requests I/O/IRQ/DMA resources, probes and initializes the chip, and registers a low-level ALSA device with explicit free handling.
- `snd_es1688_pcm()` creates a half-duplex PCM; `snd_es1688_mixer()` adds mixer controls and initializes mixer registers.
- Exported symbols are `snd_es1688_reset`, `snd_es1688_mixer_write`, `snd_es1688_create`, `snd_es1688_pcm`, and `snd_es1688_mixer`.

## Control Flow

Creation validates the caller-provided chip storage, reserves ports `port + 4` through `port + 15`, requests IRQ and 8-bit DMA, initializes locks and resource fields, normalizes MPU port, then probes. Probe runs a repeated enable-port read sequence, resets the chip, sends identification command `0xe7`, collects major/minor bytes, validates the version, disables IRQ/DMA, and enables joystick while disabling OPL3. Initialization configures optional MPU bits, reads status registers, and programs IRQ/DMA registers when enabled. PCM open enforces half-duplex by rejecting playback while capture is open and vice versa. Prepare resets the chip, sets rate, writes mode/format command sequences, programs ISA DMA autoinit, and writes the negative period count. Trigger writes start/stop values into register `0xb8`. Interrupt dispatch uses `trigger_value` to decide whether to notify playback or capture and acknowledges by reading DATA_AVAIL.

## State and Persistence Behavior

`struct snd_es1688` stores card pointer, port, IRQ, DMA, hardware/version, accepted MPU resources, spinlocks, current playback/capture substream, DMA size, trigger value, PCM pointer, and resource handle. The PCM is explicitly `SNDRV_PCM_INFO_HALF_DUPLEX`, and open state is enforced by substream pointers. Mixer state lives in hardware mixer/extended registers and is initialized from `snd_es1688_init_table`. Cleanup disables hardware, releases region/IRQ/DMA manually, and is registered with ALSA's low-level device lifecycle.

## Dependencies and Integration Points

The file depends on raw ISA I/O, ISA DMA APIs, ALSA PCM/control/core APIs, ES1688 register macros from `<sound/es1688.h>`, and `<sound/initval.h>`. It exports symbols for multiple card-level drivers. Userspace integration is through ALSA PCM and mixer controls.

## Risks and Edge Cases

DSP command loops are fixed-count polling loops; slow or absent hardware causes timeouts and probe failures. The version parser only accepts `0x6880` family and rejects ES488 because another driver should handle it. `snd_es1688_put_double()` appears to write `val1` to both left and right registers in the different-register path, which is a potential mixer right-channel bug. IRQ handling relies on `trigger_value`, so stale trigger state can send period notifications to the wrong stream. PM resume from the card driver resets the chip but does not explicitly restore mixer values.

## Test Signals

Tests should cover reset ACK `0xaa`, identification acceptance/rejection, IRQ/DMA validation, half-duplex open rejection, playback/capture across 8/16-bit mono/stereo modes, rate constraint negotiation, period interrupts, pointer reporting, mixer read/write paths including stereo controls, cleanup resource release, and symbol reuse by another driver.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/es1688/es1688_lib.c -->
