<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soundwire/sdw_registers.h -->
# sources/distributed-fs/ceph-client/include/linux/soundwire/sdw_registers.h

Purpose: This header enumerates SoundWire 1.2 register addresses, bitfields, banked port register offsets, interrupt masks, PHY controls, and SDCA address construction/extraction helpers.

Important APIs/types/functions: Macros define address masks and paging flags, DP0/DPN interrupt and control registers, SCP interrupt/status/control/system registers, device ID registers, SDCA interrupt masks, banked frame/clock/port registers, PHY control masks, cascaded interrupt layout constants, and `SDW_SDCA_CTL()` plus field extraction/validation macros.

Control flow: No functions execute here; drivers use the constants to build register addresses for `sdw_read()`, `sdw_write()`, and update sequences. Banked macros direct programming into current or next bank before SoundWire bank switches.

State and persistence: Hardware registers hold all state. This header maps software names to persistent slave/control-port/data-port state, including interrupts, clock stop, device numbering, frame shape, lane control, and SDCA control selectors.

Dependencies/integration: Depends on `bitfield.h` and `bits.h`. Integrated by SoundWire core and codec/master drivers that parse interrupts, program ports, and access SDCA controls.

Risks and test signals: Risks include wrong bank offset, clearing write-clear interrupt bits accidentally, invalid SDCA address construction, and mismatch with spec revisions. Test with register read/write traces, interrupt cascade decoding, SDCA address round trips, bank switch validation, and compile checks for bitfield masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soundwire/sdw_registers.h -->
