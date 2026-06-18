# sources/distributed-fs/ceph-client/drivers/media/pci/cx88/cx88-cards.c

## Purpose
Provides cx88 board identification, static board configuration, PCI subsystem matching, EEPROM decoding, board-specific GPIO/reset/tuner setup, tuner callback routing, PCI quirks, MMIO resource acquisition, and allocation of the shared `cx88_core`. It is the hardware knowledge base that maps generic cx2388x chips to concrete analog, radio, DVB, and Blackbird board layouts.

## Important APIs, Types, And Data
Static module parameters `card[]`, `tuner[]`, `radio[]`, `latency`, and `disable_ir` allow override of autodetection, tuner type, radio tuner type, PCI latency, and IR support. `cx88_boards[]` is a large `struct cx88_board` table describing board names, tuner/radio types and addresses, TDA9887 config, audio chip, I2S input, analog/radio input muxes, GPIO values, MPEG capabilities, and multi-frontend counts. `cx88_subids[]` maps PCI subsystem vendor/device IDs to board IDs.

Exported or cross-file functions include `cx88_tuner_callback()`, `cx88_setup_xc3028()`, `cx88_get_resources()`, and `cx88_core_create()`. Internal helpers include `leadtek_eeprom()`, `hauppauge_eeprom()`, `gdi_eeprom()`, board-specific tuner reset callbacks for XC2028/XC4000/XC5000, `dvico_fusionhdtv_hybrid_init()`, `cx88_card_setup_pre_i2c()`, `cx88_card_setup()`, and `cx88_pci_quirks()`.

## Control Flow
`cx88_core_create()` allocates and initializes the shared core, registers a `v4l2_device`, initializes video and audio control handlers, reserves and maps PCI MMIO, resolves board number from module override or PCI subsystem ID, copies the board descriptor, fills default frontend count for DVB boards, applies tuner/radio overrides, resets hardware, runs pre-I2C board GPIO setup, initializes I2C, optionally instantiates tuner subdevices, performs board-specific setup, initializes IR unless disabled, and returns the core to callers.

Board setup is layered. Pre-I2C setup brings hidden demods/tuners out of reset or selects GPIO states needed for I2C visibility. Post-I2C setup reads EEPROMs for Hauppauge, GDI, and Leadtek boards; toggles board-specific reset pins; sends special I2C init sequences for DViCO hybrid hardware; configures radio and TV tuners through `call_all(core, tuner, s_type_addr, ...)`; applies TDA9887 config; configures XC2028/3028 firmware parameters through `cx88_setup_xc3028()`; and finally places tuners in standby. Tuner callbacks route reset/power commands from tuner and DVB frontend drivers back to board-specific GPIO sequences.

## State And Persistence
The file initializes long-lived shared state in `struct cx88_core`: board number and board descriptor, model, tuner formats, PCI bus/slot, IRQ mask, MMIO pointers, V4L2 control handlers, I2C adapter/client, optional gate control and IR state, and current defaults for width/height/field. Persistent external state is limited to hardware registers, GPIO latch values, I2C-attached tuner/demod state, and PCI configuration bytes such as latency/device-control quirks while the device is active.

## Dependencies And Integration Points
It depends on cx88 register/core declarations, tuner headers (`tea5767.h`, `xc4000.h`), V4L2 I2C subdevice helpers, tveeprom parsing, kernel PCI quirk flags, and board IDs defined in the shared cx88 header. It feeds all other cx88 modules: analog video uses input mux/GPIO/tuner data, ALSA uses shared core/audio chip state, DVB uses `board.mpeg`, `num_frontends`, tuner callbacks, and gate control, and Blackbird uses `CX88_MPEG_BLACKBIRD` capability plus shared hardware arbitration.

## Risks And Test Signals
Risks are dominated by board-table accuracy: wrong GPIOs can hide I2C devices, reset the wrong demod, mute audio, or route the wrong RF/input path. EEPROM parsing and module overrides can silently change tuner selection. Multi-function boards such as HVR1300/HVR3000/HVR4000 have fragile GPIO interactions between DVB and Blackbird or between DVB-S and DVB-T. Test signals are correct autodetection logs, successful I2C probe without touching excluded RTC/IR addresses, expected tuner/demod attachments, working analog inputs/radio/audio routes, board-specific DVB frontend registration, IR operation unless disabled, and clean core refcount teardown across multiple PCI functions.
