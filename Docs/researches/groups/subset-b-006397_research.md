# subset-b-006397 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/delta.c -->
# sources/distributed-fs/ceph-client/sound/pci/ice1712/delta.c

## Purpose
Implements board-specific low-level support for M-Audio Delta-family ICE1712 cards, Digigram VX442, Lionstracs Mediastation, and Edirol DA2496. It plugs these boards into the generic ICE1712 core by declaring `snd_ice1712_delta_cards[]`, setting channel counts, programming GPIO-driven S/PDIF and codec buses, initializing AKM converter descriptions, and adding card-specific ALSA controls.

## Important APIs, Types, and Functions
The public entry point is the `snd_ice1712_delta_cards[]` table. `snd_ice1712_delta_init()` is the main `chip_init` callback and `snd_ice1712_delta_add_controls()` is the mixer/control callback. The file implements an emulated I2C/SPI path for CS8427 through `ap_cs8427_sendbytes()`, `ap_cs8427_readbytes()`, and `ap_cs8427_i2c_ops`; legacy CS8403 S/PDIF status writes through `snd_ice1712_delta_cs8403_spdif_write()`; AKM chip-select callbacks for Delta44/66, Delta1010LT, Delta66E, and VX442; and rate callbacks `delta_1010_set_rate_val()`, `delta_ak4524_set_rate_val()`, and `vx442_ak4524_set_rate_val()`. Optional PM hooks reset/mute and restore AKM/CS8427 state.

## Control Flow
Initialization first normalizes some EEPROM IDs to newer Delta1010E/Delta66E variants based on GPIO direction, sets total DAC/ADC counts by subvendor, installs PM callbacks, and raises the SPI clock line. Boards with CS8427 create an ALSA I2C bus using the GPIO-backed ops and call `snd_ice1712_init_cs8427()`. Older Delta1010/MediaStation or DiO/Delta66 variants use GPIO rate switching and/or CS8403 S/PDIF ops. Boards without analog AKM management return early; others allocate `ice->akm`, select the matching AKM template/private GPIO masks, and call `snd_ice1712_akm4xxx_init()`. Control creation adds word-clock, optical input, S/PDIF, and AKM mixer controls according to subvendor.

## State and Persistence Behavior
Runtime state lives in `struct snd_ice1712`: `num_total_dacs`, `num_total_adcs`, `i2c`, `cs8427`, `akm`, `akm_codecs`, `spdif.cs8403_bits`, and GPIO register shadowing. The CS8403 default and stream status bytes are stored in `ice->spdif` and written immediately when not blocked by an active professional playback stream. AKM register images/volumes are preserved across suspend/resume by copying them before reinitialization. Hardware state is volatile and reconstructed from EEPROM, board subtype, ALSA controls, and AKM/CS8427 caches.

## Dependencies and Integration Points
The file depends on the ICE1712 core helpers from `ice1712.h`, GPIO bit definitions from `delta.h`, ALSA I2C, CS8427, CS8403 helpers, AK4xxx codec support, and ALSA control APIs. It is consumed by `ice1712.c` through `card_tables[]`; the generic probe calls the selected card-info callbacks after base chip setup.

## Risks
GPIO bit sharing is the main risk: CS8427, AKM codecs, word clock, and S/PDIF status all reuse small board-specific pin maps and must hold `gpio_mutex` or save/restore GPIO direction/mask correctly. Rate changes above 48 kHz toggle DFS bits and sometimes reset converters, so regressions can cause clicks, silent audio, or wrong high-rate operation. Subvendor remapping based on `gpiodir` is heuristic. CS8403 status writes are bit-banged with long delays and can conflict with active stream status if locking or stream checks change.

## Test Signals
Probe each listed model or forced `model=` alias, verify expected channel counts and mixer controls, check CS8427 initialization on Audiophile/Delta410/1010LT/66E/VX442, validate S/PDIF default and PCM stream control updates, test word-clock status/select controls on Delta1010 and 1010LT, run playback/capture at <=48 kHz and >48 kHz to confirm DFS behavior, and suspend/resume with AKM mixer volumes and CS8427 state restored.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/delta.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/delta.h -->
# sources/distributed-fs/ceph-client/sound/pci/ice1712/delta.h

## Purpose
Defines the device IDs, module description fragment, exported card table, and GPIO bit assignments used by `delta.c` for M-Audio Delta-family cards and Digigram VX442.

## Important APIs, Types, and Functions
`DELTA_DEVICE_DESC` contributes user-visible supported-device text. `ICE1712_SUBDEVICE_*` constants identify Delta1010, Delta1010E, DiO2496, Delta66/66E, Delta44, Audiophile, Delta410, Delta1010LT, VX442, Mediastation, and Edirol DA2496 boards. The header declares `extern struct snd_ice1712_card_info snd_ice1712_delta_cards[]`. GPIO macros name shared DFS/S/PDIF lines and per-board chip-select, word-clock, serial-data, serial-clock, and input-select bits.

## Control Flow
The header has no executable flow. It controls board dispatch indirectly: `ice1712.c` scans `snd_ice1712_delta_cards[]`, while `delta.c` switches on the subvendor constants and uses the GPIO macros to select CS8427, CS8403, AK4524/4528/4529, word-clock, and S/PDIF input hardware.

## State and Persistence Behavior
The definitions describe volatile hardware pin state rather than persisted software state. `delta.c` stores current state in `ice->gpio`, `ice->spdif`, and AKM/CS8427 structures. The bit meanings are part of the board contract: changing them changes how the driver drives physical pins.

## Dependencies and Integration Points
Included by `delta.c` and by the core driver through low-level board includes. The constants integrate with ALSA card-info matching, EEPROM subvendor detection, and the shared `ICE1712_GPIO()` control helper.

## Risks
Several boards share bit positions with different meanings. A mistaken macro or polarity change can select the wrong codec, leave chip selects asserted, invert word-clock source selection, or misreport S/PDIF status. Dummy IDs for newer revisions and comments with uncertain polarity, such as Delta1010LT word-clock, require hardware validation.

## Test Signals
Compile users of all macros, verify each `model=` alias maps to a card-info entry, read `/proc/asound/.../ice1712` GPIO fields for expected EEPROM defaults, and exercise every GPIO-backed mixer control while observing hardware behavior or register changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/delta.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/envy24ht.h -->
# sources/distributed-fs/ceph-client/sound/pci/ice1712/envy24ht.h

## Purpose
Provides VT1724/Envy24HT register, EEPROM, GPIO, DMA, S/PDIF, AC97, and I2C definitions plus I2C helper prototypes. Although this work item focuses on the ICE1712 driver directory, this header is the shared map for the related VT1724 path.

## Important APIs, Types, and Functions
The header defines EEPROM byte indices `ICE_EEP2_*`, direct-register helpers `ICEREG1724()` and `ICEMT1724()`, register offsets such as `VT1724_REG_CONTROL`, `VT1724_REG_GPIO_DATA`, `VT1724_MT_DMA_CONTROL`, and DMA channel register blocks for PDMA/RDMA streams. It names bit masks for IRQs, system config, I2S features, S/PDIF configuration, MPU401 FIFO state, AC97 commands, GPIO direction/mask/data, DMA start/pause/FIFO errors, and I2S format. It declares `snd_vt1724_read_i2c()` and `snd_vt1724_write_i2c()`.

## Control Flow
There is no executable control flow in the header. Including VT1724 code uses these offsets to reset the chip, read EEPROM configuration, configure GPIO width and direction, program multichannel DMA engines, service IRQs, set I2S/S/PDIF formats, and access external codec/control devices over I2C.

## State and Persistence Behavior
The constants describe hardware register state. EEPROM indices represent persistent board configuration bytes read from the device; runtime register state is volatile and must be restored during probe/resume by the VT1724 implementation. GPIO fields extend beyond the 8-bit ICE1712 model to wider VT1724 pins.

## Dependencies and Integration Points
It includes ALSA control, AC97, rawmidi, I2C, PCM, and local `ice1712.h` declarations. The shared `struct snd_ice1712` carries VT1724-specific flags and callbacks, so this header bridges the older ICE1712 base structure and the newer Envy24HT register layout.

## Risks
Register definitions are low-level and many comments encode hardware errata or ambiguous widths, especially GPIO direction and GPIO 16:22 handling. Wrong bit masks can start or pause the wrong DMA engine, mis-handle S/PDIF as PDMA4/RDMA1, or break MPU interrupts. Because the header shares naming with ICE1712 but maps different offsets, accidental use of ICE1712 macros on VT1724 paths is a maintenance risk.

## Test Signals
Build VT1724 users, probe Envy24HT cards, verify EEPROM fields decode to expected channel/S/PDIF/GPIO setup, run all PDMA/RDMA streams including S/PDIF paths, check MIDI FIFO interrupts, validate GPIO read/write for pins above 15, and suspend/resume through rate, route, and DMA state restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/envy24ht.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/ews.c -->
# sources/distributed-fs/ceph-client/sound/pci/ice1712/ews.c

## Purpose
Implements low-level support for TerraTec EWX24/96, EWS88MT, EWS88D, DMX 6Fire, Phase88, and terrasoniq TS88 ICE1712 cards. It provides GPIO-bitbanged I2C, CS8427 or CS8404 S/PDIF setup, PCF8574/PCF8575/PCF9554 expander access, AK4524 codec selection, and board-specific ALSA controls.

## Important APIs, Types, and Functions
The exported table is `snd_ice1712_ews_cards[]`. `struct ews_spec` stores up to three I2C expander/transmitter devices. `snd_ice1712_ews_init()` performs board initialization, and `snd_ice1712_ews_add_controls()` registers controls. The I2C bit ops are `ewx_i2c_start()`, `ewx_i2c_stop()`, `ewx_i2c_direction()`, `ewx_i2c_setlines()`, `ewx_i2c_getclock()`, and `ewx_i2c_getdata()`. AKM callbacks include `ews88mt_ak4524_lock()/unlock()`, `ewx2496_ak4524_lock()`, and `dmx6fire_ak4524_lock()`. S/PDIF callbacks encode/decode CS8404 state, while 6Fire helpers read/write PCF9554 registers and expose mux/switch controls.

## Control Flow
Initialization sets ADC/DAC counts by subvendor, allocates `ews_spec`, creates the GPIO-backed I2C bus, then creates board-specific I2C devices: PCF9554 for DMX6Fire, CS8404 plus PCF8574 expanders for EWS88MT-like boards, or PCF8575 for EWS88D. EWX2496 and DMX6Fire initialize CS8427 and set receiver error masks; EWS88MT/D use CS8404 S/PDIF ops and write default status bits. EWS88D returns before analog setup; the remaining boards allocate AKM codec state and initialize the matching AK4524 template. Control registration adds common S/PDIF controls when CS8427 did not provide them, AKM controls for analog boards, and card-specific sensitivity, ADAT, optical, phono, LED, and input-select controls.

## State and Persistence Behavior
`ice->spec` owns the I2C device pointers. PCF expander outputs hold sensitivity, ADAT, input-select, and chip-select state in external hardware. ALSA controls read-modify-write these expanders on demand. GPIO direction/mask is saved and restored around I2C and AKM operations. CS8404 status bytes live in `ice->spdif.cs8403_bits` and `cs8403_stream_bits`; CS8427 state is delegated to the ALSA CS8427 helper.

## Dependencies and Integration Points
The file depends on `ice1712.h`, `ews.h`, ALSA I2C bit-bang support, CS8427/CS8404 helpers, AK4xxx codec support, and ALSA controls. It is selected from the core `card_tables[]` and relies on core PCM/mixer/rate code to call S/PDIF and AKM callbacks.

## Risks
I2C and AKM serial access share GPIO pins and require strict save/restore sequencing. Front-module absence on EWS88MT is detected through PCF access and can fail probe. PCF expander bit polarity differs by control. A notable risk is `snd_ice1712_ews88d_control_put()`: it computes `ndata` but sends `data`, so changed EWS88D controls may report success without updating hardware. Error handling often returns `-EIO` only after bus operations fail, so hardware regressions are easiest to catch with real devices.

## Test Signals
Probe all supported subvendors, confirm I2C device creation and EWS88MT front-module detection, verify CS8427 controls on EWX2496/DMX6Fire and CS8404 controls on EWS88MT/D, exercise AKM mixer controls, test all sensitivity switches and 6Fire muxes, check EWS88D ADAT/optical controls actually change PCF8575 output, and validate suspend/reprobe behavior by checking GPIO and expander state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/ews.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/ews.h -->
# sources/distributed-fs/ceph-client/sound/pci/ice1712/ews.h

## Purpose
Defines supported TerraTec/terrasoniq device IDs and GPIO/I2C bit assignments consumed by `ews.c`.

## Important APIs, Types, and Functions
`EWS_DEVICE_DESC` describes supported boards. `ICE1712_SUBDEVICE_EWX2496`, `EWS88MT`, `EWS88MT_NEW`, `EWS88D`, `DMX6FIRE`, `PHASE88`, and `TS88` are subvendor IDs used for dispatch. The header declares `snd_ice1712_ews_cards[]`. It defines GPIO bits for EWX24/96 and EWS88 serial data/clock/RW, sensitivity selects, MIDI pins, EWS88 CS8414 rate pins, I2C addresses for CS8404/PCF8574/PCF8575, and DMX6Fire AK4524 chip selects plus PCF9554/CS8427 addresses.

## Control Flow
The header has no executable flow. `ews.c` uses these constants in probe-time subvendor switches, I2C device creation, GPIO bit-bang callbacks, AKM chip select, and ALSA control get/put operations.

## State and Persistence Behavior
The macros describe hardware pin and I2C address contracts. Runtime state is stored externally in `ice->gpio` and `struct ews_spec`; expander outputs persist only as long as the powered device keeps them.

## Dependencies and Integration Points
It integrates with `ice1712.c` model detection and with `snd_ice1712_ews_cards[]` in `ews.c`. The constants are also tied to the generic `ICE1712_GPIO()` helper and ALSA I2C device APIs.

## Risks
Polarity and address mistakes are high impact because they can select the wrong expander, invert sensitivity controls, or break shared serial access to both I2C and AK4524 devices. The same GPIO bit positions are reused across EWX, EWS88, and DMX6Fire layouts with different semantics.

## Test Signals
Compile `ews.c`, force each supported `model=` alias, confirm I2C addresses on a bus analyzer or debug logs, exercise GPIO-backed controls and AKM access, and validate that mixer labels match board hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/ews.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/hoontech.c -->
# sources/distributed-fs/ceph-client/sound/pci/ice1712/hoontech.c

## Purpose
Implements low-level support for Hoontech/STAudio/Event ICE1712 boards: SoundTrack Audio DSP24, DSP24 Value, DSP24 Media 7.1, STAudio ADCIII, and Event EZ8. It primarily sequences GPIO-controlled external boxes and optional AK4524 codec support.

## Important APIs, Types, and Functions
The exported table is `snd_ice1712_hoontech_cards[]`. `struct hoontech_spec` stores four GPIO box bytes, a global config mask, and per-box channel/MIDI config. `hoontech_init()` is the shared initializer for DSP24-like and STAudio variants; wrappers are `snd_ice1712_hoontech_init()` and `snd_ice1712_staudio_init()`. GPIO sequencers include `snd_ice1712_stdsp24_gpio_write()`, `snd_ice1712_stdsp24_darear()`, `snd_ice1712_stdsp24_mute()`, `snd_ice1712_stdsp24_insel()`, `snd_ice1712_stdsp24_box_channel()`, `snd_ice1712_stdsp24_box_midi()`, and `snd_ice1712_stdsp24_midi2()`. `snd_ice1712_value_init()` configures modified DSP24 Value hardware with an AK4524 template, and `snd_ice1712_ez8_init()` simply applies EEPROM GPIO defaults.

## Control Flow
DSP24/STAudio initialization sets 8 DACs and 8 ADCs, allocates `hoontech_spec`, initializes the four addressable GPIO bytes with address, clock, channel, MIDI, mute, input-select, and rear-DAC defaults, then applies either normal or STAudio box defaults. It writes global DAREAR/mute/input-select state and loops over four boxes to enable MIDI2, channel routing, and MIDI1 as configured. DSP24 Value instead sets 2 DACs/ADCs, allocates AKM state, initializes AK4524 access through GPIO masks, and immediately builds AKM mixer controls. EZ8 copies EEPROM GPIO mask, direction, and state into hardware.

## State and Persistence Behavior
The driver keeps intended box state in `hoontech_spec->boxbits`, `config`, and `boxconfig`; hardware receives the state through clocked GPIO writes. There are no custom ALSA controls for changing the box config after initialization. AKM state for DSP24 Value is held in `ice->akm` and managed by common AK4xxx helpers. EZ8 state is sourced from EEPROM and not otherwise shadowed beyond `ice->gpio`.

## Dependencies and Integration Points
The file depends on `ice1712.h`, `hoontech.h`, ALSA core allocation/control support, AK4xxx helpers through declarations in `ice1712.h`, and the core card table scan. Core probe uses the card-info entries, then generic ICE1712 PCM, mixer, MIDI, and control setup run around these board hooks.

## Risks
GPIO sequencing has fixed microsecond/millisecond delays and no readback, so timing changes can silently break external box programming. Historical comments warn that box configuration flags and MIDI routing behave unexpectedly on ADAC2000-like boxes. The default config is conservative and mostly first-box oriented for non-STAudio. DSP24 Value builds AKM controls inside `chip_init`, unlike most board files, which can interact with later generic control creation ordering.

## Test Signals
Probe all listed Hoontech/Event/STAudio model paths, verify 8-channel or 2-channel counts as appropriate, observe GPIO writes during box setup, test MIDI routing on first and additional boxes, validate mute/input/rear-DAC defaults, run AKM mixer controls on DSP24 Value, and confirm EZ8 preserves EEPROM GPIO direction/mask/state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/hoontech.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/hoontech.h -->
# sources/distributed-fs/ceph-client/sound/pci/ice1712/hoontech.h

## Purpose
Defines Hoontech/STAudio/Event device IDs, the exported card table, and GPIO bit-manipulation macros for DSP24 external box control and DSP24 Value AK4524 access.

## Important APIs, Types, and Functions
`HOONTECH_DEVICE_DESC` contributes supported-device text. `ICE1712_SUBDEVICE_STDSP24`, `STDSP24_VALUE`, `STDSP24_MEDIA7_1`, `EVENT_EZ8`, and `STAUDIO_ADCIII` identify real and dummy model-selected boards. The header declares `snd_ice1712_hoontech_cards[]`. Macros such as `ICE1712_STDSP24_0_BOX()`, `ICE1712_STDSP24_1_CHN1()`, `ICE1712_STDSP24_2_MIDIIN()`, `ICE1712_STDSP24_3_MUTE()`, `ICE1712_STDSP24_SET_ADDR()`, and `ICE1712_STDSP24_CLOCK()` mutate the four-byte box image used by `hoontech.c`. Config flags describe global and per-box channel/MIDI enables.

## Control Flow
No code executes in the header. The macros are invoked by `hoontech.c` during initialization and GPIO sequencing to build byte values before clocking them into external hardware.

## State and Persistence Behavior
The macros mutate an in-memory byte array, usually `hoontech_spec.boxbits`. Persistence is limited to runtime memory and external latch state. Dummy subdevice IDs depend on explicit model selection because some hardware shares subsystem IDs.

## Dependencies and Integration Points
Included by `hoontech.c` and indirectly by `ice1712.c` board-table aggregation. The AK4524 GPIO masks integrate with the shared AK4xxx initialization helper.

## Risks
The macros directly assign expressions into array slots and evaluate the array argument multiple times, so callers must pass a stable lvalue array. Bit packing is hardware-specific and opaque; off-by-one address or channel bits can route the wrong external box channel or MIDI path. Dummy IDs require careful model matching to avoid misidentification.

## Test Signals
Compile macro users, force each Hoontech model path, inspect `boxbits` during initialization, verify external box channel/MIDI routing, and confirm DSP24 Value AK4524 serial masks select the intended GPIO pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/hoontech.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/ice1712.c -->
# sources/distributed-fs/ceph-client/sound/pci/ice1712/ice1712.c

## Purpose
Implements the main ALSA PCI driver for ICEnsemble ICE1712/Envy24 cards. It handles module parameters, PCI probe, EEPROM/model detection, base chip reset/configuration, interrupts, consumer and professional PCM engines, AC97 and I2C helpers, S/PDIF control scaffolding, multitrack mixer/routing controls, procfs diagnostics, PM, and dispatch into board-specific low-level tables.

## Important APIs, Types, and Functions
Driver registration is through `ice1712_driver` and `module_pci_driver()`. Probe path functions are `snd_ice1712_probe()`, `snd_ice1712_create()`, `snd_ice1712_read_eeprom()`, and `snd_ice1712_chip_init()`. Runtime IRQ handling is in `snd_ice1712_interrupt()`. PCM setup is split across `snd_ice1712_pcm()`, `snd_ice1712_pcm_ds()`, and `snd_ice1712_pcm_profi()` with corresponding open/close/prepare/trigger/pointer callbacks. Mixer/control functions cover multitrack volumes, routes, peaks, internal clock, rate lock/reset, EEPROM readback, GPIO controls, and S/PDIF control creation. Board integration uses `card_tables[]` containing Hoontech, Delta, and EWS card arrays.

## Control Flow
Probe allocates an ALSA card, initializes locks and GPIO callbacks, disables legacy emulation, requests PCI regions/IRQ, reads EEPROM or forced `model=`, resets/configures chip registers, then finds a matching board table entry. The board `chip_init` sets channel counts and external hardware. The core then creates professional PCM, optional consumer PCM, AC97 mixer, generic controls, board controls, optional DS PCM, MPU401 ports, clock source, long name, and registers the card. Interrupts loop until `IRQSTAT` clears, dispatching MIDI, professional playback/capture, DS channels, and consumer playback/capture period notifications. Professional hw_params set the rate, which propagates to GPIO, AKM codecs, and S/PDIF callbacks when not locked or active.

## State and Persistence Behavior
Per-card state is `struct snd_ice1712` in `card->private_data`. It stores IO bases, substreams, DMA sizes/addresses, EEPROM, selected card info, GPIO shadows, rate flags, AKM/CS8427 state, S/PDIF bytes, AC97 pointer, MIDI devices, and PM snapshots. Static globals `PRO_RATE_LOCKED`, `PRO_RATE_RESET`, and `PRO_RATE_DEFAULT` are module-wide rather than per-card, so multiple cards share rate policy controls. EEPROM content can come from hardware or card-info-provided data and is exposed read-only as an ALSA card control and procfs diagnostics.

## Dependencies and Integration Points
The driver depends on Linux PCI/DMA/IRQ/module APIs, ALSA core/PCM/control/AC97/rawmidi/proc/TLV helpers, CS8427, and the board-specific Delta/EWS/Hoontech files. It exports helper functions used by board files: GPIO get/put, S/PDIF control builder, AKM initialization/free/control building, and CS8427 initialization.

## Risks
Hardware access is register-level and timing-sensitive. Consumer PCM is explicitly warned as not working well. The professional rate controls use global static state, which is risky for systems with multiple ICE1712 cards. EEPROM fallback and forced model selection can configure the wrong GPIO layout. Route and volume controls manipulate packed hardware fields where incorrect shifts affect other channels. Suspend/resume only restores selected route, clock, AC97, AKM, and board state; untracked external expander state may need board hooks.

## Test Signals
Build and load the module, probe real and forced-model cards, inspect `/proc/asound/.../ice1712`, run professional 10-channel playback and 12-channel capture at every supported rate, test sync-start playback/capture groups, exercise consumer and DS streams if AC97 is present, verify multitrack route/volume/peak controls, test S/PDIF master/internal clock switching, run MIDI on one- and two-port boards, and suspend/resume while checking clock, route, S/PDIF, AC97, and AKM state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/ice1712.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/ice1712.h -->
# sources/distributed-fs/ceph-client/sound/pci/ice1712/ice1712.h

## Purpose
Defines the shared register map, EEPROM layout, core state structures, GPIO helpers, and board-info contract for the ICE1712 driver family. Board files include this header to access common hardware operations and to register initialization/control callbacks.

## Important APIs, Types, and Functions
The header defines direct, indirect, DS, and multitrack register offsets through `ICEREG()`, `ICEDS()`, and `ICEMT()`, plus bit masks for reset, IRQs, AC97, DMA, I2S, S/PDIF, routes, monitor controls, and EEPROM indices. Key structures are `struct snd_ice1712_eeprom`, `struct snd_ak4xxx_private`, `struct snd_ice1712_spdif`, the central `struct snd_ice1712`, and `struct snd_ice1712_card_info`. Inline helpers wrap GPIO operations, save/restore GPIO direction and mask, write/read GPIO bit groups, and indirect-register byte IO. Declared helper APIs include GPIO ALSA control get/put, S/PDIF control building, AKM init/free/control building, and CS8427 init.

## Control Flow
The header itself is declarative, but it shapes driver control flow. The core fills `struct snd_ice1712`, initializes function pointers in `ice->gpio`, and invokes `snd_ice1712_card_info` callbacks found in board tables. Board files install S/PDIF callbacks, AKM private masks, rate callbacks, and PM hooks into fields defined here. ALSA controls call the declared GPIO/S/PDIF helpers, while PCM and interrupt code use the register macros.

## State and Persistence Behavior
`struct snd_ice1712` is the lifetime state container for one card. It tracks PCI resources, substreams, DMA addresses, EEPROM data, card-info selection, control volumes, feature flags, rate state, open reservations, AKM/CS8427/I2C handles, GPIO shadows, board-private `spec`, and VT172x/PM fields. GPIO save/restore stores only direction and write-mask snapshots and relies on callers to pair calls correctly. No state is serialized outside ALSA/kernel runtime except hardware EEPROM data read into memory.

## Dependencies and Integration Points
It includes Linux IO and ALSA control, AC97, rawmidi, I2C, AK4xxx, AK4114, PT2258, PCM, and MPU401 headers. It is the integration point between `ice1712.c` and board-specific files such as `delta.c`, `ews.c`, and `hoontech.c`, and it also carries fields used by the related VT1724 driver path.

## Risks
This is a broad internal ABI. Changing structure fields, callback semantics, GPIO save/restore behavior, or register macros can break multiple board files. `snd_ice1712_save_gpio_status()` locks `gpio_mutex` and requires a matching restore; missed restores deadlock later GPIO users. Register macros assume IO bases are valid and mapped to the correct BAR. Packed bitfields in card flags and shared VT172x additions require careful initialization.

## Test Signals
Compile all ICE1712 and VT172x users, run sparse/build warnings on structure and inline helper use, probe representative Delta/EWS/Hoontech boards, exercise GPIO save/restore under AKM and I2C paths, validate card-info callbacks and MPU naming, and run suspend/resume to ensure PM fields remain coherent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ice1712/ice1712.h -->
