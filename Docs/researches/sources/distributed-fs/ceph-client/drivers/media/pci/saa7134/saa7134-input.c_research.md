# sources/distributed-fs/ceph-client/drivers/media/pci/saa7134/saa7134-input.c

Purpose: provides infrared remote-control support for SAA7134 cards through the Linux rc/input subsystem. It supports GPIO scancode remotes, GPIO raw-edge decoders, and I2C IR receiver clients with board-specific key readers.

Important APIs, types, and functions: module parameters `disable_ir`, `ir_debug`, and `pinnacle_remote` control probing and remote variant selection. `build_key()` extracts GPIO scancodes using board masks and reports keydown/keyup events. I2C key readers handle FlyDVB Trio, MSI TV@nywhere Plus, Kworld PC150U, PurpleTV, Behold M6xx NECX, and Pinnacle grey/color packet formats. `saa7134_input_irq()`, `saa7134_input_timer()`, `saa7134_ir_open()`, and `saa7134_ir_close()` manage IRQ/polling/raw operation. `saa7134_input_init1()`, `saa7134_input_fini()`, and `saa7134_probe_i2c_ir()` are called from core and I2C setup.

Control flow: early core init calls `saa7134_input_init1()` for GPIO remotes. It switches on `dev->board`, selects an rc keymap, GPIO masks, polling interval, and raw-decode mode, then allocates `struct saa7134_card_ir` plus `struct rc_dev`, fills PCI identity and rc properties, and registers the rc device. Opening the rc device applies board-specific GPIO output setup, marks the remote running, and starts a timer for polling remotes. IRQs from core call `saa7134_input_irq()`, which either builds a scancode or stores a raw IR edge. I2C adapter registration calls `saa7134_probe_i2c_ir()`, which creates `ir_video` clients with optional platform data and custom `get_key` callbacks for supported boards.

State and persistence: runtime state lives in `dev->remote`, `struct saa7134_card_ir` masks, polling timer, last GPIO value, raw decode flag, `rc_dev`, and `dev->init_data` for I2C clients. Keymap names reference kernel rc maps. There is no persistent state.

Dependencies and integration points: integrates with core IRQ GPIO16/GPIO18 dispatch, SAA7134 GPIO registers and rescan bit, I2C adapter/client creation, `ir-kbd-i2c`, rc-core keymaps/protocol decoders, and board definitions. Raw mode relies on rc-core IR decoders via `RC_DRIVER_IR_RAW`.

Risks: the board switch is large and mask values are easy to regress. Some remotes require GPIO setup in open rather than init so resume works. Polling timers must be deleted before freeing the rc device. I2C get-key callbacks sometimes modify client address or depend on GPIO lines before I2C reads. Raw edge polarity uses `mask_keydown`; wrong masks break protocol decoding.

Test signals: rc device registration for each supported board, keydown/keyup events from GPIO remotes, timer polling cadence, GPIO IRQ handling on GPIO16/GPIO18, raw IR decoding through rc-core, I2C client instantiation and key reads, suspend/resume with rc device open, `disable_ir=1`, and Pinnacle grey/color remote selection.
