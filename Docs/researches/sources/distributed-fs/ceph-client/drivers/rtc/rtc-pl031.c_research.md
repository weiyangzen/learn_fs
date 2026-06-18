# sources/distributed-fs/ceph-client/drivers/rtc/rtc-pl031.c

Purpose: implements ARM AMBA PL031 RTC support, including original ARM and STMicroelectronics variants. It provides counter timekeeping, alarms, wake IRQ support, ST clockwatch enablement, an ST weekday reset fix, and ST v2 calendar/year-register conversion.

Important APIs/types/functions: `struct pl031_vendor_data` selects variant ops and range; `struct pl031_local` stores vendor data, RTC, and MMIO base. Generic paths are `pl031_read_time()`, `pl031_set_time()`, `pl031_read_alarm()`, `pl031_set_alarm()`, and `pl031_alarm_irq_enable()`. ST v2 paths use `pl031_stv2_tm_to_time()`, `pl031_stv2_time_to_tm()`, `pl031_stv2_read_time()`, and `pl031_stv2_set_alarm()`. `pl031_interrupt()` clears AI and notifies RTC core.

Control flow: probe requests AMBA regions, duplicates the variant ops, maps registers, enables either normal counter or ST clockwatch mode, applies the ST reset weekday correction if needed, initializes wakeup, allocates and registers the RTC, and requests the IRQ with variant flags. Remove frees IRQ and releases AMBA regions.

State and persistence: original variants store seconds in DR/LR/MR. ST v2 stores packed calendar fields in DR/MR plus BCD century/year registers. Interrupt mask/status registers preserve alarm enable/pending state until cleared.

Dependencies and integration: uses AMBA device IDs to select ARM, ST v1, or ST v2 behavior; integrates with RTC core, wake IRQ helpers, MMIO, BCD helpers, and IRQ handling. ST v2 supports year range 0000-9999 while original variants are limited by a 32-bit seconds counter.

Risks: ST v2 weekday must be valid or calculated, and bad weekday handling can reject otherwise valid times. Probe uses `request_irq()` after devm RTC registration, so failure cleanup depends on manual release paths. `pl031_remove()` does not unmap devm mappings, which is fine, but uses manual AMBA release. Test signals include all AMBA IDs, ST reset weekday fix, ST v2 conversion round trips, alarm IRQ enable/clear, wake IRQ behavior, shared IRQ flags, and 32-bit range boundaries.
