<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-core.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-core.c

Purpose: PCI core and lifecycle manager for Softlogic/Bluecherry SOLO6010/SOLO6110 capture cards. It initializes hardware clocks, DMA, interrupts, subdevices, sysfs diagnostics, and module registration.

Important APIs, types, and functions: `solo_pci_probe()` allocates `solo_dev`, registers V4L2, enables PCI, maps BAR0, detects channel count, configures clocks/timers/DMA/watchdog, requests IRQ, and initializes I2C, P2M, display, GPIO, TW28, V4L2, encoder, encoder V4L2, audio, and sysfs. `solo_isr()` dispatches PCI error, P2M, I2C, video-in, encoder, and G.723 interrupts. `free_solo_dev()` tears subcomponents down. Sysfs handlers expose EEPROM, P2M timeout stats, SDRAM size/contents, input map, intervals, and SDRAM layout.

Control flow: probe configures global hardware before subcomponents. Interrupts are acknowledged immediately and then dispatched to submodule ISRs. Remove retrieves `solo_dev` from `v4l2_dev` drvdata and calls common free logic.

State and persistence: `solo_dev` is the main runtime state. EEPROM sysfs can write persistent device EEPROM, limited to top 64 bytes unless `full_eeprom=1`. SDRAM sysfs reads volatile card memory via P2M DMA.

Dependencies and integration points: PCI, V4L2, sysfs, IRQs, P2M DMA, I2C, TW28 decoder, GPIO, V4L2 display/encoder, ALSA G.723, EEPROM helper, and register definitions.

Risks: sysfs EEPROM writes are explicitly dangerous when full access is enabled. Failure unwind depends on `free_solo_dev()` tolerating partially initialized submodules. ISR dispatch relies on submodule handlers being ready after IRQ registration. `solo_reg_write()` reads PCI status after every write, which may hide posting assumptions but adds overhead.

Test signals: probe for 4/8/16 channel boards, interrupt delivery, V4L2/ALSA node creation, sysfs attribute reads, EEPROM guarded writes, SDRAM dump reads, active capture/encode/audio, and clean remove after partial probe failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-core.c -->
