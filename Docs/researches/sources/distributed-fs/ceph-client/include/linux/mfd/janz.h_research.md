# sources/distributed-fs/ceph-client/include/linux/mfd/janz.h

Purpose: This header defines common data structures for Janz MODULbus devices, especially the CMOD-IO onboard PLX bridge register layout and platform module number.

Important APIs, types, and constants: `struct janz_platform_data` carries the MODULbus module number. `struct janz_cmodio_onboard_regs` maps byte-wide onboard registers with padding bytes, including interrupt disable/status, interrupt enable/module-number, reset assert/deassert, serial EEPROM data, and EEPROM chip select.

Control flow, state, and persistence: There is no code. Drivers memory-map the PLX bridge and read/write these byte registers to enable/disable interrupts, assert/deassert reset, identify the module switch value, and access EEPROM. Persistent state may exist in the EEPROM and physical module number switch; interrupt/reset registers are live hardware state.

Dependencies and integration points: It integrates with PCI or platform code for Janz MODULbus carriers and child device registration for modules.

Risks and test signals: Risks include struct layout/padding assumptions against MMIO hardware, read/write semantics changing by access direction, reset sequencing mistakes, and EEPROM chip-select misuse. Test signals include compile-time layout review, interrupt enable/disable tests, reset toggling, module-number readback, and EEPROM read/write validation.
