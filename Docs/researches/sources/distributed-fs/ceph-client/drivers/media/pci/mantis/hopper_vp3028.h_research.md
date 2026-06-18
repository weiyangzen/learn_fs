# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/hopper_vp3028.h

## Purpose
This header declares the VP-3028 board ID and hardware configuration used by the Hopper PCI driver.

## Important APIs, Types, and Functions
It defines `MANTIS_VP_3028_DVB_T` as the board/device ID and declares `extern struct mantis_hwconfig vp3028_config`.

## Control Flow
There is no executable flow. The PCI ID table references the exported config to bind VP-3028 hardware to the frontend initialization data.

## State and Persistence Behavior
The header stores no runtime state. The implementation's static config is shared through this declaration.

## Dependencies and Integration Points
It includes `mantis_common.h` for `struct mantis_hwconfig` and is included by `hopper_cards.c` and `hopper_vp3028.c`.

## Risks
The ID constant and external declaration must match the implementation and PCI table. Wrong IDs prevent board matching or attach the wrong frontend config.

## Test Signals
Build/link coverage and PCI probe of VP-3028 devices validate the header.
