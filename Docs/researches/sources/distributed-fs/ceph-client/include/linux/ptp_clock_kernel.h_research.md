# sources/distributed-fs/ceph-client/include/linux/ptp_clock_kernel.h

Purpose: declares the in-kernel PTP Hardware Clock provider/consumer interface, including clock registration, driver operation callbacks, event notification, auxiliary work, timestamp cross-sampling helpers, virtual clock conversion, and scaled-ppm arithmetic.

Important APIs and types: `struct ptp_clock_request` describes EXTS, PEROUT, and PPS requests. `struct ptp_system_timestamp` carries pre/post system timestamps and clock ID. `struct ptp_clock_info` is the driver callback table for frequency/phase/time adjustment, time/cycle reads, cross timestamps, feature enable, pin verification, auxiliary work, and perout loopback. `struct ptp_clock_event` reports alarm, external timestamp, offset, PPS, and user PPS events. Helpers include `scaled_ppm_to_ppb()`, `diff_by_scaled_ppm()`, and `adjust_by_scaled_ppm()`. Public APIs include `ptp_clock_register()`, `ptp_clock_unregister()`, `ptp_clock_event()`, `ptp_clock_index()`, index lookup by OF node or parent device, `ptp_find_pin*()`, worker scheduling/cancel, built-in-only virtual clock index lookup/conversion, and pre/post system timestamp readers.

Control flow: a PHC driver fills `ptp_clock_info`, registers it, responds to core ioctl/sysfs requests through callbacks, reports timestamp/PPS events with `ptp_clock_event()`, and unregisters on removal. Consumers may resolve a PHC index by device, find pin mappings under core locking, schedule auxiliary driver work, or convert timestamps to virtual PHC time when PTP is built in.

State and persistence: runtime state is owned by the PTP core and driver: registered clocks, pin configuration, event queues, auxiliary work, and hardware time. PHC time is hardware state and may persist depending on device power.

Dependencies and integration points: depends on device model, PPS, PTP UAPI, timecounter/timekeeping, skbuff timestamping, OF nodes, kthread work, and network timestamp consumers. It is the core bridge between NIC/PHC drivers and userspace `/dev/ptp*`.

Risks and test signals: risks include callback sleeping/atomic-context mismatch, bad `max_adj`, deprecated `gettime64` use, inconsistent cross timestamp windows, pin mux races, unsupported flag handling, arithmetic overflow in frequency adjustment, and module vs built-in virtual clock restrictions. Test PHC registration/removal, ioctl adjustment/set/get, external timestamp and PPS events, pin assignment validation, aux worker lifecycle, virtual clock conversion, and `CONFIG_PTP_1588_CLOCK` disabled stubs.
