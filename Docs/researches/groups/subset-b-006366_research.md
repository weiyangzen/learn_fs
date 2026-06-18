# subset-b-006366 HDA codec research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/ca0132_regs.h -->
# sources/distributed-fs/ceph-client/sound/hda/codecs/ca0132_regs.h

## Purpose

This header is the register-map and address helper layer for Creative CA0132 DSP memory, DSP DMA, and debug/control blocks. It does not execute code by itself; it gives the CA0132 codec driver symbolic names for X/Y/auxiliary RAM spaces, microcontroller memory, DMA channel registers, bit fields, valid memory ranges, and logical offsets.

## Important APIs, types, and functions

The file exports only preprocessor definitions. Important groups are `DSP_DBGCNTL_*` for debug-control fields, `XRAM_*`, `YRAM_*`, `UC_*`, `AXRAM_*`, and `AYRAM_*` for memory-space sizes and instance offsets, and `DSPDMAC_*` for per-channel DMA config, DSP address offsets, transfer counts, interrupt counts, audio channel selection, channel start/status/property, and active status. The functional macros include `*_INST_OFFSET(chan)`, `X_RANGE_*`, `Y_RANGE_*`, `UC_RANGE`, `X_OFF`, `Y_OFF`, `AX_OFF`, `AY_OFF`, and split-size helpers for transfers crossing main/aux memory boundaries.

## Control flow

There is no runtime control flow. The macros are expanded by CA0132 code that validates memory addresses, chooses address spaces, composes coefficient/register addresses, and programs DSP DMA transactions. The range macros use start address plus `(size - 1) * increment` tests to decide whether an operation fits into main memory, auxiliary memory, extended memory, or all valid memory.

## State and persistence behavior

The header stores no state. Persistence is entirely in the hardware registers and DSP memory addressed by these constants. Because many macros map logical indices to physical chip offsets, wrong values can persist as corrupted DSP memory or stalled DMA state in the codec until reset/reinitialization.

## Dependencies and integration points

It is included by the CA0132 HDA codec implementation. Its constants integrate with HDA verb/coefficient accessors and CA0132 firmware/DSP loader code that needs stable hardware offsets. It depends only on C preprocessor arithmetic and unsigned integer semantics.

## Risks and test signals

Risks are off-by-one range validation, integer overflow in `(a) + ((s)-1) * incr`, address-space confusion between main and auxiliary RAM, channel index overflow beyond the 12 DMA channels, and field masks drifting from hardware documentation. Test signals include CA0132 firmware load success, DSP DMA read/write round trips across X/Y/UC and aux boundaries, invalid-address rejection, suspend/resume with DSP reinitialization, and audio-path tests that exercise DSP effects and microphone processing.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/ca0132_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/cirrus/Kconfig -->
# sources/distributed-fs/ceph-client/sound/hda/codecs/cirrus/Kconfig

## Purpose

This Kconfig fragment exposes Cirrus Logic HDA codec support and its per-driver build switches. `SND_HDA_CODEC_CIRRUS` is the parent menu option; the CS420x, CS421x, and CS8409 drivers are selected beneath it.

## Important APIs, types, and functions

The important symbols are `SND_HDA_CODEC_CIRRUS`, `SND_HDA_CODEC_CS420X`, `SND_HDA_CODEC_CS421X`, and `SND_HDA_CODEC_CS8409`. CS420x and CS421x select `SND_HDA_GENERIC`; CS8409 selects both `SND_HDA_GENERIC` and `SND_HDA_SCODEC_COMPONENT` because it can bind side-codec amplifier components.

## Control flow

Kconfig control flow is declarative. Enabling the parent exposes the children. CS420x and CS421x default to `y` under the parent, while individual toggling is hidden unless `EXPERT` is set. CS8409 is explicit and remains separately selectable. The comments warn about module autoloading when the HDA core is built-in but a codec driver is modular.

## State and persistence behavior

There is no runtime state. The selected symbols persist in kernel configuration and control which object files are compiled or loadable. Misconfiguration can leave matching HDA codec IDs without a driver at runtime.

## Dependencies and integration points

This file integrates with the ALSA HDA codec build system and the Cirrus `Makefile`. Runtime integration is through the module aliases emitted by each compiled driver. The CS8409 dependency on `SND_HDA_SCODEC_COMPONENT` is an integration requirement for its component manager path.

## Risks and test signals

Risks include missing generic-parser support, forgetting the side-codec component selection for CS8409, and built-in HDA core plus modular codec autoload mismatches. Test signals are `olddefconfig` coverage, `modinfo` aliases for modular builds, boot probing on Cirrus hardware, and build matrix checks for built-in and module combinations.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/cirrus/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/cirrus/Makefile -->
# sources/distributed-fs/ceph-client/sound/hda/codecs/cirrus/Makefile

## Purpose

This Makefile maps the Cirrus Kconfig symbols to codec driver objects.

## Important APIs, types, and functions

`snd-hda-codec-cs420x-y`, `snd-hda-codec-cs421x-y`, and `snd-hda-codec-cs8409-y` define the object composition. CS8409 is built from both `cs8409.o` and `cs8409-tables.o`. `subdir-ccflags-y += -I$(src)/../../common` provides access to common HDA headers.

## Control flow

Kbuild appends `snd-hda-codec-cs420x.o`, `snd-hda-codec-cs421x.o`, or `snd-hda-codec-cs8409.o` to `obj-*` when the matching config symbol is enabled as built-in or module.

## State and persistence behavior

No runtime state exists. The persisted build result determines module names and linked objects. Splitting CS8409 tables into a second object means both files must remain in the same symbol namespace and module.

## Dependencies and integration points

The Makefile integrates with `Kconfig`, ALSA HDA codec infrastructure, and the common side-codec include path. CS8409 depends on symbols declared across `cs8409.h`, `cs8409.c`, and `cs8409-tables.c`.

## Risks and test signals

Risks include omitting table objects from CS8409, breaking include paths, or mismatching Kconfig symbol names. Test signals are `make M=sound/hda/codecs/cirrus`, full kernel builds for each symbol as `y` and `m`, and unresolved-symbol checks for `cs8409-tables.o` exports consumed by `cs8409.o`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/cirrus/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/cirrus/cs420x.c -->
# sources/distributed-fs/ceph-client/sound/hda/codecs/cirrus/cs420x.c

## Purpose

This driver supports Cirrus Logic CS4206, CS4207, and CS4208 HDA codecs. It layers Cirrus-specific coefficient programming, GPIO/EAPD handling, Apple platform fixups, CS4207 errata sequences, and CS4208-specific corrections on top of the generic HDA parser.

## Important APIs, types, and functions

`struct cs_spec` embeds `struct hda_gen_spec` and stores GPIO masks, EAPD GPIO bits, the vendor-processing NID, and an optional SPDIF switch hook. `cs_vendor_coef_get()` and `cs_vendor_coef_set()` are the central coefficient accessors. `cs_automute()` updates generic outputs and toggles headphone/speaker EAPD GPIOs. `cs_init()` writes errata/init verbs and initializes GPIO/coefficient state. `cs_parse_auto_config()` runs the generic pin parser and keeps dynamically switched ADCs powered. Probe paths split into `cs420x_probe()` and `cs4208_probe()`, selected by `cs_codec_probe()`. `cs_build_controls()` applies build-time fixups after generic controls are created.

## Control flow

Probe allocates the spec, installs the automute hook, selects fixups from model names and PCI/subsystem quirks, applies `HDA_FIXUP_ACT_PRE_PROBE`, parses BIOS pin defaults with the generic parser, then applies `HDA_FIXUP_ACT_PROBE`. Init runs CS420x or CS4208 coefficient verb sequences, calls `snd_hda_gen_init()`, sets GPIOs, and for CS420x enables DMIC/SPDIF coefficient state based on active pins. Build first creates generic controls, then lets fixups patch mixer behavior such as the CS4208 SPDIF switch.

## State and persistence behavior

Runtime state is in `codec->spec`, generic parser state, cached GPIO values, and the hooked SPDIF mixer callback. Hardware state persists in vendor coefficients, GPIO data, EAPD lines, pin overrides, and amp-cap overrides. CS4208 Mac fixups may remap fixup IDs using codec SSID and may set inverted jack-detection behavior.

## Dependencies and integration points

The driver depends on ALSA HDA core APIs, `hda_local.h`, `hda_auto_parser.h`, `hda_jack.h`, and `generic.h`. It integrates with the HDA fixup framework, generic auto parser, jack unsolicited events, Apple PCI/subsystem quirk tables, and module alias matching for codec IDs `0x10134206`, `0x10134207`, and `0x10134208`.

## Risks and test signals

Risks include wrong GPIO EAPD polarity causing muted speakers or headphones, stale SPDIF switch hook pointers, coefficient writes to the wrong vendor NID, Apple quirk overmatching, dynamic ADC power regressions, and CS4208 amp-cap/pin override mistakes. Test signals include boot probe logs, generic mixer creation, headphone automute, speaker EAPD behavior, DMIC presence, SPDIF switch and pin-control synchronization, suspend/resume, and model-specific Apple hardware smoke tests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/cirrus/cs420x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/cirrus/cs421x.c -->
# sources/distributed-fs/ceph-client/sound/hda/codecs/cirrus/cs421x.c

## Purpose

This driver supports Cirrus Logic CS4210 and CS4213 codecs. It handles CS4210 coefficient initialization and A1 errata, GPIO/SENSE_B/DMIC pinmuxing, SPDIF jack-driven automute, speaker boost control, suspend power sequencing, and generic HDA auto-configuration.

## Important APIs, types, and functions

`struct cs_spec` extends the generic spec with GPIO/EAPD fields, `spdif_detect`, `spdif_present`, `sense_b`, and `vendor_nid`. `cs_vendor_coef_get()` and `cs_vendor_coef_set()` access the vendor processing coefficients. `cs_automute()` mutes output when SPDIF SENSE_B is present and updates GPIO EAPD state. `cs4210_pinmux_init()` configures B1/B2 as GPIO or SENSE_B and disconnects DMIC when those functions are forced. `parse_cs421x_digital()` enables SPDIF unsolicited callbacks. `cs4210_spdif_automute()` updates SPDIF pin output and calls automute. `cs421x_boost_vol_*()` implement the custom speaker boost ALSA control backed by `CS421X_IDX_SPK_CTL`.

## Control flow

Probe allocates state, sets the automute hook, applies CS4210 fixups when applicable, updates pinmux before parsing, runs `cs421x_parse_auto_config()`, and applies probe fixups. The parser first normalizes DAC volume caps, then uses the generic HDA parser, registers SPDIF detection callbacks, and adds the speaker boost control for CS4210 speaker outputs. Init writes CS4210 coefficient and errata sequences, reapplies pinmux, runs generic init, programs GPIOs, and performs an initial SPDIF automute check. Suspend shuts up pins, powers DAC/ADC to D3, and sets PDREF for CS4210.

## State and persistence behavior

Persistent state lives in generic parser structures, `sense_b` and SPDIF detection flags, GPIO state, coefficient registers, and the current speaker boost coefficient. `spdif_present` is updated by jack callbacks and feeds `gen.master_mute`. Suspend resets some hardware power state but keeps software state in `codec->spec`.

## Dependencies and integration points

The driver uses ALSA HDA generic parser, jack callbacks, pin config helpers, amp-cap overrides, and module codec IDs `0x10134210` and `0x10134213`. It has board fixups for CDB4210 and Stumpy, including pin tables and SENSE_B setup.

## Risks and test signals

Risks include disabling DMIC incorrectly when GPIO/SENSE_B is selected, SPDIF detect callbacks toggling the wrong pin control, speaker boost coefficient drift, failing to keep the single ADC path powered, and PDREF/suspend sequencing regressions. Test signals include playback/capture on CS4210 and CS4213, speaker boost mixer get/put, SPDIF plug/unplug automute, DMIC availability on boards without forced SENSE_B, and suspend/resume without pop or lost capture.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/cirrus/cs421x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/cirrus/cs8409-tables.c -->
# sources/distributed-fs/ceph-client/sound/hda/codecs/cirrus/cs8409-tables.c

## Purpose

This file contains static data for the CS8409 HDA bridge driver: ALSA mixer templates, fixed-rate PCM descriptors, HDA init verb arrays, pin configuration tables, CS42L42 I2C initialization sequences, CS8409 coefficient programming sequences, sub-codec descriptors, Dell platform quirk tables, model names, and HDA fixup chains.

## Important APIs, types, and functions

Exported data includes `cs42l42_dac_volume_mixer`, `cs42l42_adc_volume_mixer`, `cs42l42_48k_pcm_analog_playback`, `cs42l42_48k_pcm_analog_capture`, `cs8409_cs42l42_init_verbs`, `cs8409_cs42l42_hw_cfg`, `cs8409_cs42l42_bullseye_atn`, `cs8409_cs42l42_codec`, `dolphin_init_verbs`, `dolphin_hw_cfg`, `dolphin_cs42l42_0`, `dolphin_cs42l42_1`, `cs8409_cdb35l56_four_init_verbs`, `cs8409_cdb35l56_four_hw_cfg`, `cs8409_fixup_tbl`, `cs8409_models`, and `cs8409_fixups`. The static pin and I2C arrays are consumed through exported descriptors and fixups.

## Control flow

The file is declarative. Runtime code in `cs8409.c` selects an entry from `cs8409_fixup_tbl` or `cs8409_models`, applies a pin-table fixup, then chains to a function fixup such as `cs8409_cs42l42_fixups()`, `dolphin_fixups()`, or `cs8409_cdb35l56_four_autodet_fixup()`. Hardware init functions iterate the `struct cs8409_cir_param` arrays until the zero terminator. CS42L42 resume/init code bulk-writes the `struct cs8409_i2c_param` sequences.

## State and persistence behavior

Most objects are immutable tables. The exported `struct sub_codec` objects are mutable templates: `cs8409.c` assigns their `codec` pointer and updates fields such as `hp_jack_in`, `mic_jack_in`, `suspended`, `last_page`, and volume caches at runtime. Because those objects are global, correct single-device assumptions and initialization ordering matter.

## Dependencies and integration points

The data depends on constants and structs from `cs8409.h`, CS42L42 register definitions, HDA generic parser APIs, and the HDA fixup framework. Quirk entries primarily target Dell subsystem IDs for Bullseye, Warlock, Cyborg, Dolphin, Odin, and related MLK variants, plus CDB35L56-four-HD model support.

## Risks and test signals

Risks include incorrect Dell subsystem-to-fixup mapping, stale CS42L42 register sequences, shared mutable `sub_codec` state across multiple codec instances, wrong pin defaults causing generic parser misclassification, and coefficient recipes that break ASP slot timing or DMIC routing. Test signals include fixup selection logs for known subsystem IDs, 48 kHz-only PCM constraints, jack detection for single and dual CS42L42 designs, speaker/DMIC routing on Bullseye/Warlock/Cyborg/Odin, and component binding for CDB35L56 systems.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/cirrus/cs8409-tables.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/cirrus/cs8409.c -->
# sources/distributed-fs/ceph-client/sound/hda/codecs/cirrus/cs8409.c

## Purpose

This is the runtime driver for the Cirrus Logic CS8409 HDA bridge. CS8409 is not a complete analog codec; it bridges HDA pins to companion codecs or amplifiers such as CS42L42 and CS35L56-class side components. The driver provides generic HDA parsing plus CS8409 coefficient setup, clock-gated I2C access to CS42L42, synthesized jack detection, volume proxy controls, PCM hooks, suspend/resume sequencing, and component-manager integration.

## Important APIs, types, and functions

Core CS8409 helpers include `cs8409_alloc_spec()`, `cs8409_vendor_coef_get()`, `cs8409_vendor_coef_set()`, `cs8409_parse_auto_config()`, `cs8409_init()`, `cs8409_build_controls()`, and `cs8409_remove()`. I2C helpers are `cs8409_enable_i2c_clock()`, `cs8409_disable_i2c_clock()`, `cs8409_i2c_wait_complete()`, `cs8409_set_i2c_dev_addr()`, `cs8409_i2c_set_page()`, `cs8409_i2c_read()`, `cs8409_i2c_write()`, `cs8409_i2c_bulk_read()`, and `cs8409_i2c_bulk_write()`. CS42L42 support includes `cs42l42_volume_info/get/put()`, `cs42l42_mute()`, playback/capture PCM hooks, jack detection helpers, `cs42l42_resume()`, and `cs42l42_suspend()`. Platform fixups include `cs8409_cs42l42_fixups()`, `dolphin_fixups()`, and `cs8409_cdb35l56_four_autodet_fixup()`.

## Control flow

Probe allocates `struct cs8409_spec`, picks a model or subsystem fixup, applies `PRE_PROBE`, parses generic auto config, then applies `PROBE`. Init calls generic init and then `HDA_FIXUP_ACT_INIT`; build controls calls generic control construction and then `HDA_FIXUP_ACT_BUILD`. CS42L42 fixups override `exec_verb` so HDA pin-sense reads return companion-codec jack state, register fixed 48 kHz PCM streams, add mixer controls, configure GPIO reset/interrupt lines, and run initial jack detection only after both init and build have completed. Dolphin uses two CS42L42 sub-codecs and its own jack and exec-verb dispatch. CDB35L56 fixups discover ACPI I2C/SPI devices, initialize the HDA component manager, and forward playback hooks to side-codec components.

## State and persistence behavior

`struct cs8409_spec` stores generic parser state, `scodecs[]`, GPIO state, speaker state, delayed I2C clock work, I2C address cache, playback/capture activity flags, init/build completion flags, original `exec_verb`, optional unsolicited-event override, and component manager state. Each `struct sub_codec` stores I2C address, reset/IRQ GPIOs, init sequence, suspended flag, page cache, jack status, headset-bias/full-scale settings, and volume cache. Hardware persistence spans CS8409 vendor coefficients, GPIO reset lines, CS42L42 register pages, side-codec power state, and jack-detection interrupt masks. The delayed clock worker keeps I2C clocks enabled briefly after transactions, then disables them under `i2c_mux`.

## Dependencies and integration points

The driver depends on Linux ACPI, I2C/SPI discovery helpers, mutexes, delayed work, `read_poll_timeout`, ALSA HDA generic parser, HDA jack reporting, CS42L42 register definitions, `hda_component` side-codec management, and exported data from `cs8409-tables.c`. Its module imports namespace `SND_HDA_SCODEC_COMPONENT` and matches HDA codec ID `0x10138409`.

## Risks and test signals

Risks include I2C clock race conditions, stale `dev_addr` or `last_page` caches, shared global `sub_codec` templates, errors swallowed during bulk init, jack event polarity confusion, synthesized pin-sense mismatch, volume writes while a sub-codec is suspended, component-manager cleanup leaks, and suspend/resume ordering that leaves CS42L42 in reset or with interrupts masked. Test signals include I2C timeout/error logs, jack insertion/removal for HP/mic/line-out on all variants, ALSA mixer volume persistence during PCM prepare/cleanup, 48 kHz stream negotiation, suspend/resume with wake GPIO events, component bind/unbind for CS35L56 systems, and `exec_verb` fallback correctness for non-intercepted verbs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/cirrus/cs8409.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/cirrus/cs8409.h -->
# sources/distributed-fs/ceph-client/sound/hda/codecs/cirrus/cs8409.h

## Purpose

This header defines the CS8409 bridge driver's shared constants, data structures, exported table declarations, and fixup entry points used by `cs8409.c` and `cs8409-tables.c`.

## Important APIs, types, and functions

`enum cs8409_pins` names the CS8409 HDA node layout, including ASP1/ASP2 transmitters/receivers, DMIC pins, beep generator, and vendor widget. `enum cs8409_coefficient_index_registers` names CS8409 coefficient indices for device config, ASP clocks, slot controls, I2C/SPI, PFE, status, loopback, and pad config. Platform/fixup enums name Bullseye, Warlock, Cyborg, Dolphin, Odin, and CDB35L56 paths. `struct cs8409_i2c_param`, `struct cs8409_cir_param`, `struct sub_codec`, and `struct cs8409_spec` are the central data types. The header declares CS42L42 mixer callbacks, PCM stream descriptors, fixup tables, init/hardware config arrays, global sub-codec templates, and the platform fixup functions.

## Control flow

The header itself has no executable flow. It shapes runtime dispatch by giving fixup IDs, codec indices, volume offsets, and exported function prototypes to both compilation units. `cs8409.c` uses these declarations to select table data and call platform-specific fixups; `cs8409-tables.c` uses the structs and constants to initialize the static data.

## State and persistence behavior

`struct cs8409_spec` is allocated per HDA codec and persists for the codec lifetime. It owns delayed work, mutex-protected I2C state, side-codec pointers, GPIO state, PCM/jack flags, callback overrides, and component manager state. `struct sub_codec` state persists companion-codec address, reset/IRQ metadata, jack status, suspend/page state, full-scale/no-type-detect flags, and volume caches.

## Dependencies and integration points

The header includes PCI, TLV, workqueue, CS42L42, HDA codec, local HDA helper, auto parser, jack, generic parser, and side-codec component headers. It is the ABI boundary between table data and runtime code inside the CS8409 module.

## Risks and test signals

Risks include enum values drifting away from hardware node/coefficient numbering, struct layout expectations between files, global sub-codec declarations being reused unsafely, and missing declarations when adding a platform. Test signals are compiler coverage for `cs8409.o` plus `cs8409-tables.o`, fixup selection for every enum path, runtime validation of pin NIDs against HDA widgets, and component-manager paths for CS35L56 ACPI devices.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/cirrus/cs8409.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/cm9825.c -->
# sources/distributed-fs/ceph-client/sound/hda/codecs/cm9825.c

## Purpose

This driver supports the C-Media CM9825 HDA codec. It combines generic HDA auto-configuration with vendor-specific verb sequences for power states, headphone plug transitions, GENE_TWL7 board routing, playback start/stop de-pop behavior, delayed jack reporting, and resume sequencing.

## Important APIs, types, and functions

`struct cmi_spec` embeds `struct hda_gen_spec` and stores selected D0/D3/headphone verb tables, delayed jack work items, jack-detect-capable pins, and the quirk ID. Vendor verb constants such as `CM9825_VERB_SET_PLL`, `CM9825_VERB_SET_DACL`, and `CM9825_VERB_SET_D2S` address vendor node `0x43`. Key functions are `cm9825_probe()`, `cm9825_init()`, `cm9825_suspend()`, `cm9825_resume()`, `cm9825_cm_std_resume()`, `cm9825_playback_pcm_hook()`, `cm9825_setup_unsol()`, `hp_callback()`, delayed work handlers for HP/lineout/inputs, and `cm9825_remove()`.

## Control flow

Probe allocates state, picks standard or GENE_TWL7 verb tables by subsystem ID, initializes delayed work, writes D0 verbs, parses pin defaults through the generic parser, and registers jack callbacks. Jack callbacks temporarily block reporting, schedule 200 ms delayed work, and then update jack state after vendor headphone-present/remove sequencing. Playback prepare/cleanup on GENE_TWL7 writes start/stop verb sequences. Suspend cancels delayed work and writes D3 verbs. Resume reinitializes the codec, writes D0 verbs, restores regmap state, and updates power status; the standard path also checks headphone presence and applies the remove sequence if needed.

## State and persistence behavior

Software state includes selected verb table pointers, delayed work pending state, cached jack NIDs, and generic parser configuration. Hardware state persists in vendor node registers, pin widget control for node `0x42`, EAPD on `0x34`, selected input routing, jack reporting state, and amp/power registers. Delayed jack work intentionally defers reporting to let detection and de-pop state settle.

## Dependencies and integration points

The driver depends on ALSA HDA core, generic parser, jack helpers, delayed work, and module matching for codec ID `0x13f69825`. It integrates with PCM hooks, generic build/init/PCM operations, HDA unsolicited jack events, and subsystem-ID-specific board behavior.

## Risks and test signals

Risks include unsupported subsystem IDs returning `-ENXIO`, incorrect vendor verb values causing no capture/playback or pop noise, delayed work racing with remove/suspend, jack report blocking not being cleared, and GENE_TWL7 fixed routing breaking other boards. Test signals include boot probe with known subsystem IDs, headphone plug/unplug after 200 ms delay, playback start/stop pop behavior, capture reliability on GENE_TWL7, suspend/resume jack state, and absence of delayed-work use-after-free warnings.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/cm9825.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/cmedia.c -->
# sources/distributed-fs/ceph-client/sound/hda/codecs/cmedia.c

## Purpose

This is the generic C-Media HDA codec driver for CMI8888 and CMI9880-family codecs. Most behavior is delegated to the ALSA HDA generic parser, with one CMI8888-specific headphone amplifier control.

## Important APIs, types, and functions

`cmedia_probe()` allocates `struct hda_gen_spec`, initializes generic parser state, parses BIOS pin defaults, runs generic auto-config, and optionally adds `Headphone Amp Playback Volume` for CMI8888 pin `0x10` when that pin is configured as headphone output. `cmedia_codec_ops` binds probe/remove/build/init/unsol/check-power/stream-PM operations to generic HDA helpers.

## Control flow

Probe detects CMI8888 by codec vendor ID, masks NID `0x10` out of generic output-volume selection so the boost amp is not folded into normal output volume, parses pin config, then adds the explicit amp control if the pin default indicates `AC_JACK_HP_OUT`. Errors call `snd_hda_gen_remove()` before returning.

## State and persistence behavior

State is the generic parser spec in `codec->spec`, plus `out_vol_mask` for CMI8888. Hardware persistence is limited to generic HDA control state and any mixer writes through the manually added headphone amp control.

## Dependencies and integration points

The driver uses ALSA HDA core, generic auto parser, HDA jack support, and module IDs `0x13f68888`, `0x13f69880`, and `0x434d4980`. It integrates almost entirely through generic build/init/PCM and jack-event handling.

## Risks and test signals

Risks include misdetecting the CMI8888 boost amp, duplicate or missing headphone volume controls, BIOS pin defaults that hide the intended HP amp, and generic-parser regressions affecting CMI9880. Test signals are mixer enumeration on CMI8888, headphone amp gain changes, generic playback/capture/jack behavior on CMI9880, and probe failure cleanup under injected allocation/control-add errors.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/cmedia.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/conexant.c -->
# sources/distributed-fs/ceph-client/sound/hda/codecs/conexant.c

## Purpose

This driver supports a broad set of Conexant HDA codecs using the generic HDA parser plus many platform fixups. It handles EAPD control, optional beep controls, mute and mic-mute LEDs, headset/headphone mic modes, OLPC XO DC-input behavior, amp-cap corrections, pin overrides, GPIO quirks, and stability workarounds for resume communication.

## Important APIs, types, and functions

`struct conexant_spec` embeds `struct hda_gen_spec` and stores EAPD pins, parse flags, OLPC DC-mode state, LED GPIO/EAPD fields, and a CX11880/SN6140 headset-recognition flag. Probe and lifecycle functions are `cx_probe()`, `cx_init()`, `cx_suspend()`, `cx_remove()`, and `cx_auto_shutdown()`. EAPD helpers are `cx_auto_parse_eapd()`, `cx_auto_turn_eapd()`, and `cx_auto_vmaster_hook()`. Beep support is conditionally compiled through `cx_auto_parse_beep()`. Major fixup helpers include `cxt_fixup_headphone_mic()`, `cxt_fixup_headset_mic()`, `cxt_fixup_olpc_xo()`, `cxt_fixup_mute_led_eapd()`, GPIO LED helpers, amp-cap fixups, HP gate-mic setup, and CX11880/SN6140 headset VREF handling.

## Control flow

Probe allocates state, enables a jack callback for CX11880/SN6140 headset VREF handling, scans EAPD-capable pins, selects a fixup table based on vendor ID, optionally installs a vmaster EAPD hook, applies `PRE_PROBE` fixups, parses pin defaults with accumulated parse flags, creates beep controls, runs generic auto-config, enables `sync_write` and bus reset if needed, and applies `PROBE` fixups. Init runs generic init, enables static EAPDs, initializes GPIO LEDs, applies `INIT` fixups, and re-applies CX11880/SN6140 headset recognition. Suspend/remove turn off EAPD to avoid speaker noise.

## State and persistence behavior

Software state includes generic parser data, EAPD pin lists, dynamic EAPD mode, LED masks and polarity, OLPC recording/DC bias state, current capture mux paths, and parse flags. Hardware state persists in pin widget controls, EAPD bits, GPIO data, amp-cap overrides, vendor registers for headset mode and recognition, and OLPC mic/DC routing. Some fixups install hooks into generic callbacks, so state transitions happen through mixer, automute, capture PCM, and LED classdev paths.

## Dependencies and integration points

The driver depends on ALSA HDA core, generic parser, beep support when configured, jack support, LED classdev integration through HDA helpers, and included helper fixups for ThinkPad and Ideapad ACPI hotkey LEDs. It matches many Conexant codec IDs from CX11880/SN6140 through CX20952 and uses PCI/subsystem and codec quirks to select platform behavior.

## Risks and test signals

Risks include quirk overmatching, EAPD shutdown muting valid outputs, LED polarity mistakes, OLPC DC mode disabling normal microphones incorrectly, headset mic parse flags changing jack semantics, CX11880/SN6140 vendor writes breaking headset detection, sync-write bus reset side effects, and amp-cap overrides creating unsafe gain ranges. Test signals include per-codec probe and fixup selection logs, EAPD speaker/headphone output after mute toggles and suspend, mute/micmute LED behavior, headset CTIA/OMTP/headphone detection, OLPC DC-mode mixers and capture LED behavior, beep mixer creation when configured, and S3 resume stability on affected laptops.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/hda/codecs/conexant.c -->
