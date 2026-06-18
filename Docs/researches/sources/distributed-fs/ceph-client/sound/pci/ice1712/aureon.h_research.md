# sources/distributed-fs/ceph-client/sound/pci/ice1712/aureon.h

## Purpose

This header declares device descriptor strings, VT1724 subdevice IDs, the Aureon/Prodigy card-info table, and board-specific GPIO bit assignments used by `aureon.c`.

## Important APIs, Types, and Functions

`AUREON_DEVICE_DESC` lists Terratec Aureon and Audiotrak Prodigy model descriptors for the parent driver. `VT1724_SUBDEVICE_*` constants identify Aureon 5.1 Sky, Aureon 7.1 Space, Aureon 7.1 Universe, Prodigy 7.1, Prodigy 7.1 LT, and Prodigy 7.1 XT. The header declares `snd_vt1724_aureon_cards[]`. `AUREON_*` GPIO masks define shared SPI, WM reset/chip-select, CS8415 chip-select, AC97 bridge, digital select, and headphone amplifier lines. `PRODIGY_*` masks define alternate WM SPI and headphone pins for Prodigy LT/XT variants.

## Control Flow, State, Dependencies, Risks, and Tests

There is no runtime control flow or state. Constants drive board matching, GPIO direction/mask programming, SPI transactions, AC97 bridge writes, and control behavior in `aureon.c`. The declaration assumes `struct snd_ice1712_card_info` is visible through parent headers. Risks center on using the wrong GPIO mask family for a board variant and descriptor macro syntax affecting parent module descriptions. Test by building ICE1724, verifying all descriptors/subdevice IDs are included, and exercising GPIO-dependent controls on standard and LT/XT layouts.
