# sources/distributed-fs/ceph-client/drivers/ptp/ptp_sysfs.c

Purpose: implements the generic sysfs interface for PTP class devices. It exposes clock capability metadata, controls EXTS/PEROUT/PPS features, manages virtual clock creation limits, drains the external timestamp FIFO, and creates per-pin configuration attributes.

Important APIs/types/functions: `ptp_groups[]` exports the main attribute group. Static attributes include `clock_name`, max/count capability files, `max_phase_adjustment`, `extts_enable`, `fifo`, `period`, `pps_enable`, `n_vclocks`, and `max_vclocks`. `ptp_is_attribute_visible()` hides unsupported controls based on `ptp_clock_info`. `ptp_populate_pin_groups()` and `ptp_cleanup_pin_groups()` dynamically create and free the `pins/` group. `ptp_pin_store()` calls `ptp_set_pinfunc()` under `pincfg_mux`.

Control flow: stores parse simple text commands and call the driver `enable()` callback with a `struct ptp_clock_request`. `extts_enable` expects an index and enable flag. `period` expects index, start seconds/nanoseconds, and period seconds/nanoseconds, enabling when period is nonzero. `pps_enable` requires `CAP_SYS_TIME`. `fifo` reads and removes one event from the first timestamp queue. `n_vclocks_store()` creates or removes child virtual clocks to reach the requested count, updates the parent `vclock_index[]`, and logs free-running behavior for parents without cycle support. `max_vclocks_store()` resizes the index array when it will not truncate existing virtual clocks.

State and persistence: sysfs writes mutate live PTP device state only. Virtual clock count and max count persist for the lifetime of the parent `struct ptp_clock`; they are not stored across unregister/reboot. FIFO reads consume queued external timestamp events.

Dependencies and integration: depends on PTP private structures, capability checks, sysfs attribute groups, dynamic allocation helpers, child device iteration, and `ptp_vclock_register/unregister()`.

Risks and test signals: the sysfs FIFO intentionally drains only the first queue. `max_vclocks_store()` declares an `unsigned int *` for storage allocated and used as `int *`, which is type-inconsistent though same-sized on normal platforms. Vclock deletion uses `device_for_each_child_reverse()` and a non-error `-EINVAL` break convention. Test visibility for clocks with/without EXTS/PEROUT/PPS/phase support, permission checks for PPS, malformed store input, FIFO wraparound, growing/shrinking vclocks under concurrency, pin name lookup, and cleanup after partial pin group allocation.
