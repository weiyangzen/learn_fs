## sources/distributed-fs/ceph-client/drivers/acpi/processor_idle.c

### Purpose
`processor_idle.c` implements the ACPI-backed cpuidle driver. It discovers legacy C-states from `_CST` or FADT/P_BLK, discovers low-power idle states from `_LPI`, validates platform constraints, and registers per-CPU cpuidle devices.

### Important APIs, Types, And Functions
Public integration functions include `acpi_processor_register_idle_driver()`, `acpi_processor_unregister_idle_driver()`, `acpi_processor_power_init()`, `acpi_processor_power_exit()`, `acpi_processor_hotplug()`, `acpi_processor_power_state_has_changed()`, and `acpi_idle_rescan_dead_smt_siblings()`. Important internals include C-state discovery and verification helpers, `acpi_idle_enter()`, `acpi_idle_enter_bm()`, `acpi_idle_enter_s2idle()`, `_LPI` parsing via `acpi_processor_evaluate_lpi()`, and LPI flattening via `flatten_lpi_states()`.

### Control Flow
Driver registration clamps `max_cstate`, claims CST control, finds one processor with valid idle data, builds global cpuidle state descriptors, and registers `acpi_idle_driver`. Per-CPU power initialization rediscoveries power data, allocates a `cpuidle_device`, fills per-CPU state pointers, and registers the device. Legacy C-state discovery prefers `_CST`, falls back to FADT, adds mandatory C1, verifies C2/C3 address and latency, applies DMI quirks, sets APIC timer broadcast and TSC stability flags, and handles bus-mastering rules for C3. LPI discovery validates architecture FFH support and `_OSC` LPI support, evaluates `_LPI` at the CPU and processor-container parents, flattens hierarchical local/parent states, and registers FFH enter callbacks.

### State, Persistence, And Dependencies
State includes module parameters `max_cstate`, `nocst`, `bm_check_disable`, and `latency_factor`, per-CPU `acpi_cpuidle_device`, per-CPU C-state pointers, `acpi_idle_driver`, static bus-mastering flags, and per-processor power flags. Dependencies span cpuidle, CPU hotplug, DMI, tick broadcast, context tracking, perf low-power callbacks, ACPI `_CST`/`_LPI`, FADT, architecture FFH hooks, and x86 APIC/TSC behavior.

### Integration Points
`processor_driver.c` calls the registration and per-CPU init/exit hooks. Architecture files may override weak LPI probe and enter hooks. Thermal, hotplug, and ACPI power notifications trigger reinitialization or device enablement.

### Risks
Idle entry runs in low-level CPU contexts, so interrupt, RCU, context-tracking, and bus-mastering sequencing are sensitive. Firmware latency ordering bugs are worked around by sorting only latencies, not whole state entries. `_LPI` hierarchy flattening limits to `ACPI_PROCESSOR_MAX_POWER`. Reinitialization unregisters all cpuidle devices when CPU0 receives a power notification, which depends on CPU hotplug locking.

### Test Signals
Exercise `_CST`, FADT-only, `_LPI`, disabled `nocst`, boot idle override, C3 with and without BM control, APIC timer-stop systems, suspend-to-idle entry, CPU hotplug, ACPI C-state notification, malformed `_LPI` packages, and platforms with too many LPI combinations.
