# sources/distributed-fs/ceph-client/drivers/media/usb/au0828/au0828-cards.c

## Purpose
Defines AU0828 board profiles, USB IDs, GPIO bring-up, EEPROM handling, tuner reset callbacks, and analog frontend/tuner subdevice setup.

## Important APIs, types, and functions
`au0828_boards[]` maps board numbers to names, tuner types/addresses, I2C speed, IR/analog flags, and input routing. `hvr950q_cs5340_audio()` controls a shared I2S audio reset GPIO. `au0828_tuner_callback()` resets tuners for supported boards. `hauppauge_eeprom()` parses Hauppauge EEPROM and updates tuner type. `au0828_card_setup()` reads EEPROM and calls `au0828_card_analog_fe_setup()`. `au0828_card_analog_fe_setup()` creates `au8522` analog decoder and tuner subdevices when V4L2 analog is enabled. `au0828_gpio_setup()` powers/reset devices per board. `au0828_usb_id_table[]` binds many Hauppauge/DViCO/Elgato IDs to board profiles.

## Control flow and state
Core probe copies a board profile from `au0828_boards`, powers the bridge, calls GPIO setup, registers I2C, and invokes card setup. Card setup may overwrite tuner type from EEPROM, then attaches analog subdevices. GPIO setup writes bridge registers and sleeps to satisfy reset/power timing.

## Dependencies and integration points
Depends on AU0828 register access, AU8522 demod/decoder, tuner framework, TV EEPROM, and V4L2 subdevice registration. The USB ID table is consumed by `au0828-core.c` probe.

## Risks and test signals
Risks are board-profile mistakes, GPIO timing regressions, mismatch with ALSA USB quirks for V4L2 boards, and EEPROM model drift. Test signals include correct board name on probe, expected tuner type after EEPROM parse, successful analog subdevice creation, tuner reset callback behavior, and working inputs for TV/composite/S-video.
