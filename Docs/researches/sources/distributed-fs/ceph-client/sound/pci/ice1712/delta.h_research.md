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
