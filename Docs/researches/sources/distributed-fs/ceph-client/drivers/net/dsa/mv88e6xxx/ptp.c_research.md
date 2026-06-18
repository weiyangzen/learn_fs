# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/ptp.c

## Purpose
Provides PTP hardware clock support for 88E6xxx devices, including cyclecounter/timecounter setup, frequency/time adjustment, external timestamp capture on supported GPIO pins, overflow maintenance, and per-family PTP ops descriptors.

## Important APIs, Types, and Functions
Key structures include `mv88e6xxx_cc_coeffs` and exported ops `mv88e6165_ptp_ops`, `mv88e6352_ptp_ops`, and `mv88e6390_ptp_ops`. Important functions are `mv88e6xxx_ptp_setup`, `mv88e6xxx_ptp_free`, `mv88e6xxx_ptp_adjfine`, `mv88e6xxx_ptp_adjtime`, `mv88e6xxx_ptp_gettime`, `mv88e6xxx_ptp_settime`, `mv88e6352_ptp_enable_extts`, and family-specific clock reads.

## Control Flow and State
Setup reads the TAI clock period, selects 4/8/10 ns coefficients, initializes `chip->tstamp_cc` and `chip->tstamp_tc`, configures `ptp_clock_info`, optionally programs the PTP CPU destination port, registers the PHC, and schedules overflow work. Time changes are protected by `mv88e6xxx_reg_lock`. External timestamp enable configures GPIO function, starts delayed polling, reads TAI event status, clears valid events, converts raw cycles to nanoseconds, and emits `ptp_clock_event`.

## Dependencies and Integration Points
Depends on AVB TAI read/write ops, GPIO ops, hwtstamp support, global1/global2 helpers, kernel PTP, workqueues, DSA upstream-port lookup, and the driver register lock. It integrates with ethtool/SIOCSHWTSTAMP paths through `hwtstamp.c` and with PHC consumers through `ptp_clock_register`.

## Risks and Test Signals
Risks include wrong clock-period coefficients, missed 32-bit counter overflow, deadlocks if free is called with the register lock held, event polling races, unsupported GPIO/pin functions, and firmware/hardware reporting unexpected periods. Test signals include `phc2sys`/`ptp4l` stability, adjfine bounds, external timestamp edge tests, suspend/remove cleanup, and forced error paths for TAI reads/writes.
