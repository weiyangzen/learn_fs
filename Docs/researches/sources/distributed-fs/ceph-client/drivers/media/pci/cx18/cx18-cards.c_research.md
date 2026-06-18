# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-cards.c

## Purpose
This file is the board database for cx18-supported CX23418 capture cards. It defines card-specific PCI IDs, video/audio input routing, tuner choices, GPIO reset and mux settings, I2C probing addresses, DDR timing, and user-visible card names/comments.

## Important APIs, Types, and Functions
Static `struct cx18_card` instances describe Hauppauge HVR-1600 variants, Compro H900, Yuan MPC718, Conexant Raptor PAL, Toshiba Qosmio DVB-T/Analog, Leadtek PVR2100 and DVR3100H, and GoTView PCI DVD3 Hybrid. Public helpers are `cx18_get_card()`, `cx18_get_input()`, and `cx18_get_audio_input()`. The file also defines standard tuner I2C address sets `cx18_i2c_std` and `cx18_i2c_nxp`.

## Control Flow
Probe code asks `cx18_get_card()` by user-selected index or autodetected PCI/EEPROM result. Once selected, `cx18_init_struct2()` counts valid video/audio inputs from the table. Ioctl enumeration calls `cx18_get_input()` and `cx18_get_audio_input()` to fill V4L2 descriptors from the active table.

## State and Persistence
The card table is static read-only state. At runtime, `struct cx18` holds a pointer to the selected card, derived names, I2C address table, input counts, active input, audio input, tuner standard, and GPIO values initialized from the selected entry.

## Dependencies and Integration Points
The file depends on V4L2 standards, tuner IDs, `cx18-av-core.h` input enums, `cx18-cards.h` structures, and CS5345 mux constants. It drives probe decisions in `cx18-driver.c`, GPIO behavior in `cx18-gpio.c`, tuner and subdevice registration in `cx18-i2c.c`, firmware DDR setup in `cx18-firmware.c`, and DVB frontend selection in `cx18-dvb.c`.

## Risks and Edge Cases
Many boards have comments saying experimenters are needed or settings are guesses. Wrong DDR timing can prevent firmware or DMA from working. Wrong GPIO reset masks can hold tuners, demods, or IR chips in reset. Hauppauge cards are refined by EEPROM rather than subsystem IDs, so defaulting to the wrong HVR-1600 variant can select the wrong digital frontend or DDR timing.

## Test Signals
Validate every card entry with PCI autodetection or forced `cardtype=`, input and audio enumeration, tuner setup, GPIO reset behavior, DDR initialization, analog capture, and DVB registration on hybrid boards.
