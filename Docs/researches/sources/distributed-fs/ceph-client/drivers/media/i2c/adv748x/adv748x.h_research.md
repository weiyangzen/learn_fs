<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/adv748x/adv748x.h -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/adv748x/adv748x.h

## Purpose
`adv748x.h` is the shared private header for the ADV748x driver stack. It defines page IDs, OF port numbers, pad layouts, child/parent state structures, helper macros, register offsets/masks, and cross-file function prototypes.

## Important APIs, Types, and Functions
- Enums define register pages, OF ports, CSI-2 pads, HDMI pads, and AFE pads.
- `struct adv748x_csi2`, `struct adv748x_hdmi`, `struct adv748x_afe`, and `struct adv748x_state` are the core private data contracts across source files.
- Macros identify enabled endpoints and TX identity (`is_tx_enabled`, `is_txa`, `is_txb`, `is_afe_enabled`, `is_hdmi_enabled`).
- Register macros cover IO, HDMI timing, repeater/EDID, SDP, CP, and CSI TX maps.
- Helper macros wrap page-specific access (`io_read`, `hdmi_read16`, `sdp_clrset`, `cp_clrset`, `tx_write`).
- Prototypes expose core register access, subdev init, TX power, AFE/CSI2/HDMI init/cleanup, and pixel-rate/virtual-channel helpers.

## Control Flow
The header has no runtime control flow, but it defines inline helpers such as `adv748x_get_remote_sd()` that traverse media pads to remote subdevices.

## State and Persistence
It defines the in-memory state layout for all ADV748x modules. Persistent hardware state is represented by page register offsets and masks, but the header itself stores nothing.

## Dependencies and Integration Points
It depends on Linux I2C declarations and on media/V4L2 types included by each C file before use. It is the coupling layer for `adv748x-core.c`, `adv748x-afe.c`, `adv748x-csi2.c`, and `adv748x-hdmi.c`.

## Risks
- Container macros are powerful and unsafe if used with the wrong subdevice type.
- Register masks and page IDs form an implicit ABI among split source files; mistakes compile but misprogram hardware.
- The endpoint-enabled macros treat endpoint presence as feature enablement, so device-tree correctness is central.

## Test Signals
Compile all ADV748x objects together, exercise media graph creation for every port enum, validate register constants against hardware dumps, and test helper macros through HDMI/AFE/TX format and stream paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/adv748x/adv748x.h -->
