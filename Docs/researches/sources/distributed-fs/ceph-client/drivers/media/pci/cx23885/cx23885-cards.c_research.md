# sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23885-cards.c

Main cx23885 board database and board-specific setup layer. It maps PCI subsystem IDs to supported boards, declares per-board ports, inputs, tuners, CI type, GPIO defaults, and analog/DVB capabilities, and performs hardware setup during probe.

Important data/functions are `cx23885_boards`, `cx23885_subids`, `cx23885_card_list`, `hauppauge_eeprom`, `viewcast_eeprom`, `tbs_card_init`, `cx23885_tuner_callback`, `cx23885_gpio_setup`, `cx23885_ir_init`, `cx23885_ir_fini`, `cx23885_ir_pci_int_enable`, `netup_jtag_io`, and `cx23885_card_setup`. Setup reads EEPROM, configures TS port defaults, resets demods/tuners/CAM chips through GP0/MC417 GPIOs, loads cx25840 and cs3308 subdevices, initializes NetUP hardware, loads Altera firmware through JTAG, and selects IR implementation.

State mutated includes board/port settings, `sd_cx25840`, `sd_ir`, GPIO and MC417 registers, interrupt masks, EEPROM-derived logs, and FPGA firmware state. Risks are board-specific GPIO mistakes, stale ID tables, interrupt storms from unsafe IR enablement, firmware absence, and hardcoded module parameters. Test signals are per-board probe, EEPROM parsing, DVB frontend attach, analog routing, CI operation, IR receive/transmit, GPIO sequencing, and unknown-board fallback output.
