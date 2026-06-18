# sources/distributed-fs/ceph-client/drivers/perf/fsl_imx8_ddr_perf.c

Purpose: Implements the Freescale/NXP i.MX8 DDR and DB perf PMU. It exposes DDR controller transaction, command, queue, credit, and AXI-ID filtered events through perf, handling multiple SoC quirks and two PMU types (`imx8_ddr*` and `imx8_db*`).

Important APIs, types, and functions: `struct ddr_pmu` stores PMU state, MMIO base, IRQ, CPU, active events, counter ownership, IDA instance, and devtype data. `struct fsl_ddr_devtype_data` captures quirks, identifier, and PMU type. Event/filter sysfs is built from `ddr_perf_events_attrs`, format attributes for `event`, `axi_id`, `axi_mask`, `axi_port`, and `axi_channel`, capability attributes under `caps`, and optional `identifier`. Runtime paths are `ddr_perf_event_init()`, `ddr_perf_event_add()`, `ddr_perf_event_start()`, `ddr_perf_event_stop()`, `ddr_perf_event_update()`, and `ddr_perf_irq_handler()`.

Control flow: OF probe maps MMIO, enables all clocks, selects devtype data, allocates a PMU ID, chooses name prefix by DDR vs DB type, sets up a dynamic CPU hotplug state, requests the IRQ, pins it to the chosen CPU, and registers the PMU. Event init rejects sampling and task-bound events, enforces PMU group compatibility, and enforces compatible AXI filters for filtered events. Add programs filter registers for legacy/enhanced/super filter variants, allocates counter 0 only for cycles and counters 1-3 for other events, stores the event, and optionally starts it. IRQ is driven by cycle-counter overflow; it drains all active events and restarts the cycle counter.

State and persistence: Counter ownership is in `events[NUM_COUNTERS]`; `active_counter` keeps the cycle counter running while any event is active. Hardware counters are cleared after every read. Filter programming is global or per-counter depending on quirk flags, so grouped filtered events must share compatible filters.

Dependencies and integration: Uses platform/OF matching, clock bulk enable, MMIO, IRQ affinity, Linux perf PMU callbacks, IDA allocation, CPU hotplug, and NXP device-tree compatible strings for i.MX8 variants.

Risks and test signals: Risks include filter incompatibility across grouped events, AXI mask/channel bit inversion errors, cycle-counter bias handling on enhanced-filter SoCs, and event loss when non-cycle counters overflow before the cycle IRQ drains them. Test with `perf stat` on each advertised event, DB-type visibility restrictions, invalid filter group rejection, IRQ affinity migration, and overflow warning paths.
