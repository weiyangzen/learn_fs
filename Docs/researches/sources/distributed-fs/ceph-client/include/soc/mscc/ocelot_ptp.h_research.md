# sources/distributed-fs/ceph-client/include/soc/mscc/ocelot_ptp.h

Purpose: declares the Ocelot PTP hardware clock interface and exposes PTP pin/action and clock-adjustment register bits used by the MSCC switch driver.

Important APIs/types/functions: exports `ocelot_ptp_gettime64`, `ocelot_ptp_settime64`, `ocelot_ptp_adjtime`, `ocelot_ptp_adjfine`, `ocelot_ptp_verify`, `ocelot_ptp_enable`, `ocelot_init_timestamp`, and `ocelot_deinit_timestamp`. It also defines `OCELOT_MAX_PTP_ID`, `OCELOT_PTP_FIFO_SIZE`, pin register strides, `PTP_PIN_ACTION_*`, `PTP_CFG_MISC_PTP_EN`, and clock adjustment bits.

Control flow: implementations in `ocelot_ptp.c` bind these callbacks into `struct ptp_clock_info`, read/set TOD registers, adjust time or frequency, configure external timestamp/perout pins, and install VCAP traps for PTP packets. The header is the common contract used by platform-specific Ocelot and Felix drivers.

State and persistence: state lives in hardware TOD, adjustment registers, timestamp FIFOs, pin configuration, and VCAP trap rules. Initialization registers a PHC and deinitialization tears it down.

Dependencies and integration: depends on `linux/ptp_clock_kernel.h` and `soc/mscc/ocelot.h`. It integrates with Linux PTP, DSA tagging transmit rewrite operations, RX/TX timestamp handling, IRQ handlers, and VCAP filters for L2/IPv4/IPv6 PTP trapping.

Risks: timestamp FIFO overflow, wrong pin action encoding, or incorrect one-step/two-step rewrite handling can corrupt time sync. Test signals include PHC get/set/adj tests, `ptp4l` traffic, external timestamp/perout validation, TX/RX timestamp paths, and FIFO overflow handling.
