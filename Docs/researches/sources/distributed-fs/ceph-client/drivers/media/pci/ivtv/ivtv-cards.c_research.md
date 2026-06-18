# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-cards.c

## Purpose
`ivtv-cards.c` is the board database for the ivtv driver. It describes supported Hauppauge, AVerMedia, Yuan, Adaptec, I/O Data, GotView, ASUS, Buffalo, Sony, and related CX23415/CX23416 cards, including PCI IDs, V4L2 capabilities, physical inputs and outputs, tuner choices, I2C probe addresses, GPIO masks, and board-specific comments.

## Important APIs, Types, and Functions
The file instantiates many `struct ivtv_card` descriptors and matching `struct ivtv_card_pci_info` tables, plus common tuner I2C probe sets such as `ivtv_i2c_std`, `ivtv_i2c_radio`, and `ivtv_i2c_tda8290`. Exported helpers are `ivtv_get_card()`, `ivtv_get_input()`, `ivtv_get_output()`, `ivtv_get_audio_input()`, and `ivtv_get_audio_output()`.

## Control Flow
There is little procedural control flow. Probe code in `ivtv-driver.c` indexes `ivtv_card_list` directly or scans each card's `pci_list` to select a descriptor. Once selected, input and output query helpers translate descriptor entries into V4L2-facing names, types, audio sets, and standards. Variant descriptors for PVR-350 V1 and CX23416GYC no-GR/no-YCS sit after standard cards so runtime detection can switch to them without altering normal card numbering.

## State and Persistence
State is static, read-mostly kernel data. It is not persisted and has no runtime locking. The selected `itv->card`, `itv->card_name`, `itv->card_i2c`, and derived input counts in `struct ivtv` are runtime pointers into this table.

## Dependencies and Integration Points
The descriptors encode dependencies on V4L2 standards/capabilities, tuner IDs, GPIO subdev behavior, and media subdevice-specific routing constants for `cx25840`, `saa711x`, `saa717x`, `msp3400`, `wm8775`, `cs53l32a`, `m52790`, and `upd64031a`. Driver probe, routing, I2C registration, GPIO control, tuner setup, and ioctl enumeration all consume this file.

## Risks and Edge Cases
Incorrect bit flags or input mux constants can silently register the wrong subdevice, route audio/video from the wrong physical jack, or omit radio and IR support. Hauppauge cards rely on EEPROM more than PCI IDs, while some non-Hauppauge IDs collide and are refined by probed subdevices. Unsupported cards such as AVerMedia M104 intentionally expose zero V4L2 capabilities to abort probe after identification.

## Test Signals
Useful signals are correct autodetection logs, expected `/dev/video*` and radio nodes, valid `VIDIOC_ENUMINPUT`/`VIDIOC_ENUMOUTPUT` names and standards, tuner selection for PAL/NTSC/SECAM, GPIO-controlled mux switching, IR subdevice registration, and board-specific capture from every advertised physical input.
