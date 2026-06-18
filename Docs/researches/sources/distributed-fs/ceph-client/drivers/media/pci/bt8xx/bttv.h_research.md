# sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/bttv.h

## Purpose
`bttv.h` is the public-ish bttv interface header used by other in-kernel drivers and bttv companion files. It defines card IDs, board configuration structures, exported legacy GPIO APIs, the newer subdevice bus interface, GPIO helpers, I2C helper declarations, and IR entry points.

## Important APIs, Types, And Functions
Major types are `struct bttv_core`, `struct tvcard`, `struct bttv_sub_device`, and `struct bttv_sub_driver`. The header declares card setup hooks `bttv_idcard()`, `bttv_init_card1()`, `bttv_init_card2()`, `bttv_init_tuner()`, chipset hooks, legacy GPIO functions, subdriver registration, GPIO accessors, I2C helpers, and input helper functions. It defines many `BTTV_BOARD_*` constants and the compile-time `MUXSEL()` macro family used by board tables.

## Control Flow
The header does not execute code, but its types shape the runtime flow. `struct bttv_core` is embedded at the start of private `struct bttv` and shared with subdrivers. `struct tvcard` entries drive muxing, GPIO audio routing, tuner configuration, video input counts, DVB/remote/radio capability, and card-specific hooks. `bttv_call_all()` and `bttv_call_all_err()` wrap V4L2 subdevice broadcasts.

## State And Persistence
The header defines state containers rather than storing state itself. `struct tvcard` is static board metadata. `struct bttv_core` carries per-device V4L2, PCI, I2C, subdevice list, number, and card type. GPIO and subdevice structures point back to this core.

## Dependencies And Integration Points
It depends on V4L2, I2C, tuner definitions, and media device APIs. It is included by bttv implementation files, bt8xx DVB modules, and legacy external users of the bttv GPIO interface. Board table definitions in `bttv-cards.c` rely heavily on the board IDs and `struct tvcard`.

## Risks
The large board-ID namespace is ABI-like inside the driver family; reordering or changing IDs breaks board tables and module parameters. `MUXSEL()` uses preprocessor packing with octal literal tricks, so callers must pass plain 0-3 digits. The header exposes obsolete legacy GPIO functions that can keep unsafe usage patterns alive.

## Test Signals
Compile coverage is the main signal. Runtime signals include correct card identification by board ID, mux selection matching board tables, successful subdriver registration, and external modules resolving the declared symbols.
