# sources/distributed-fs/ceph-client/include/linux/fsl/ptp_qoriq.h

Purpose: declares register layouts, bit definitions, state, endian accessors, and public operations for the QorIQ/eTSEC PTP hardware clock driver.

Important APIs and types: register structs map control, alarm, fixed-period interval, and external timestamp groups. `struct ptp_qoriq_registers` stores mapped register group pointers. Offset and bit macros define timer control, event/mask/status, alarm, FIPER, external trigger, Tx/Rx timestamp, clock selection, prescaler, and default periods. `struct ptp_qoriq` stores base, register pointers, spinlock, PTP clock/caps, resource/device, feature flags, IRQ, PHC index, timing parameters, and endian-specific read/write callbacks. Public operations include `ptp_qoriq_isr()`, `ptp_qoriq_init()`, `ptp_qoriq_free()`, `ptp_qoriq_adjfine()`, `ptp_qoriq_adjtime()`, `ptp_qoriq_gettime()`, `ptp_qoriq_settime()`, `ptp_qoriq_enable()`, and `extts_clean_up()`.

Control flow: platform driver maps registers, picks eTSEC or standard offsets and endian accessors, initializes the PHC, handles timer IRQs for alarms/FIPER/external timestamps, and implements PTP clock callbacks for time adjustment, set/get, and feature enable.

State and persistence: state is runtime PHC register programming, PTP clock registration, feature flags, IRQ state, and frequency/timer compensation fields. Hardware time persists while powered but is not filesystem storage.

Dependencies and integration points: depends on I/O accessors, interrupts, PTP clock kernel API, resources, and network drivers that consume hardware timestamping.

Risks and test signals: risks include endian mismatch, incorrect clock period/addend calculations, missing spinlock protection around multi-register time reads/writes, IRQ event cleanup races, and feature bit differences between eTSEC and QorIQ variants. Tests should cover PHC register/unregister, get/set/adjfine/adjtime accuracy, external timestamp events, periodic outputs, IRQ storms, suspend/resume, and big/little-endian platforms.
