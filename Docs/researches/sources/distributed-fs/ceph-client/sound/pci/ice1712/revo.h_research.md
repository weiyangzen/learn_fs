# sources/distributed-fs/ceph-client/sound/pci/ice1712/revo.h

## Purpose
`revo.h` declares the public board-support interface and GPIO layout for the M-Audio Revolution/Audiophile 192 Envy24HT driver.

## Important APIs, Types, and Functions
- `REVO_DEVICE_DESC` contributes user-visible card descriptions to the ICE1724 card table.
- `VT1724_SUBDEVICE_REVOLUTION71`, `VT1724_SUBDEVICE_REVOLUTION51`, and `VT1724_SUBDEVICE_AUDIOPHILE192` identify the supported PCI subsystem IDs.
- `extern struct snd_ice1712_card_info snd_vt1724_revo_cards[]` exports the board table implemented in `revo.c`.
- `VT1724_REVO_CCLK`, `CDIN`, `CDOUT`, `CS0..CS3`, `I2C_DATA`, `I2C_CLOCK`, and `MUTE` define board-specific GPIO bit assignments.

## Control Flow
This header has no executable flow. It is included by the generic ICE1724 card registry and by `revo.c`; constants steer subdevice matching and GPIO operations.

## State and Persistence
No state is stored. The constants describe hardware wiring and must remain synchronized with `revo.c` serial/I2C transactions.

## Dependencies and Integration Points
The declarations depend on `struct snd_ice1712_card_info` from the ICE1712 core. GPIO aliases intentionally overlap for different board models, so call sites must choose the correct interpretation by subvendor.

## Risks and Test Signals
Risks are mainly wrong bit definitions or subdevice IDs, which would cause missing detection, wrong chip-selects, or stuck mute. Test signals are successful matching of all three board models and verified GPIO traffic during codec initialization.
