# sources/distributed-fs/ceph-client/sound/pci/ice1712/se.c

## Purpose
`se.c` provides Envy24HT board support for ONKYO WAVIO SE-90PCI and SE-200PCI cards. SE-90PCI is mostly static hardware setup, while SE-200PCI initializes WM8740, WM8766, and WM8776 devices and creates custom ALSA mixer controls for playback, capture, input selection, AGC, and AFL bypass.

## Important APIs, Types, and Functions
- `struct se_spec` caches per-control stereo values in `vol[8]`.
- `se200pci_WM8766_write()` bit-bangs a 16-bit control word over GPIO16/17/18 and wraps GPIO save/restore.
- `se200pci_WM8776_write()` sends WM8776 register/data words over the Envy24HT I2C helper to address `0x34`.
- `se200pci_set_pro_rate()` dispatches rate changes to the attached codecs; only WM8766 changes MCLK ratio.
- `struct se200pci_control` and `se200pci_cont[]` describe custom ALSA controls and their target hardware.
- `se200pci_cont_*_{info,get,put}` implement ALSA mixer callbacks and update hardware on changed values.
- `se_init()` and `se_add_controls()` are the exported board callbacks through `snd_vt1724_se_cards[]`.

## Control Flow
Probe calls `se_init()`, which allocates `se_spec`, distinguishes SE-90PCI from SE-200PCI, sets DAC/ADC counts, and initializes codecs. For SE-200PCI, WM8766 is reset and configured for I2S 24-bit, WM8776 receives a manual default-register load and initial selector/AGC/volume state, and `ice->gpio.set_pro_rate` is assigned. Control registration loops over `se200pci_cont[]`, creates `snd_kcontrol` descriptors, and wires each put callback to `se200pci_cont_update()`.

## State and Persistence
Mixer values are cached only in `ice->spec->vol`; hardware register state is programmed immediately on mixer updates. EEPROM images in `se200pci_eeprom` and `se90pci_eeprom` are static fallback configuration data used by the core. There is no nonvolatile persistence or resume cache in this file.

## Dependencies and Integration Points
The file depends on ICE1712/Envy24HT GPIO and I2C helpers, ALSA control/TLV APIs, and board IDs from `se.h`. It integrates by providing `snd_vt1724_se_cards[]` and by setting `ice->gpio.set_pro_rate` for the core rate-change path.

## Risks and Test Signals
Risks include hand-coded WM8766/WM8776 register values diverging from hardware expectations, missing rollback on partial initialization errors, and `change` reporting in some multi-channel puts reflecting only the last lane. Test signals include ALSA mixer control enumeration, valid TLV scales, correct default mute/volume behavior, audible output on all SE-200PCI channel groups, capture selector switching, and MCLK changes above 96 kHz.
