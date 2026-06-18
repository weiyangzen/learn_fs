# sources/distributed-fs/ceph-client/drivers/powercap/intel_rapl_tpmi.c

Purpose: RAPL backend for Intel TPMI auxiliary devices. It maps TPMI MMIO domain records into common RAPL packages and exposes powercap and perf PMU support without CPU-hotplug package discovery.

Important APIs/types/functions: `struct tpmi_rapl_package`, `trp_alloc()`, `trp_release()`, `parse_one_domain()`, `tpmi_rapl_read_raw()`, `tpmi_rapl_write_raw()`, `rapl_check_unit_tpmi()`, `intel_rapl_tpmi_probe()`, and `intel_rapl_tpmi_remove()`. `rpi_tpmi[]` defines TPMI primitive masks for PL1, PL2, PL4, locks, enables, energy, perf, and power info.

Control flow: auxiliary probe obtains TPMI platform data and a single resource, allocates a TPMI package wrapper, ioremaps the resource, and walks 128-byte domain records. `parse_one_domain()` validates version, domain size, mandatory unit/energy registers, domain type, root-system-domain status, duplicate domains, and register flags. It fills the backend register table with MMIO addresses and limit bitmaps. Probe then initializes `rapl_if_priv`, rejects duplicate package ids, calls `rapl_add_package()` with package id rather than CPU id, and adds a common RAPL PMU.

State and persistence: `tpmi_rapl_packages` and `tpmi_control_type` are protected by `tpmi_rapl_lock`; the shared `intel-rapl` powercap control type is registered for the first TPMI package and unregistered after the last is released. Per-package MMIO state is owned by devm ioremap plus the `tpmi_rapl_package` allocation; removal removes PMU, powercap package, and wrapper.

Dependencies/integration: depends on auxiliary bus, Intel VSEC/TPMI helpers, MMIO `readq()/writeq()`, common RAPL namespace, and powercap. Domain root filtering prevents non-root system domains from creating platform RAPL zones.

Risks: firmware-reported domain flags are trusted after validation; unsupported minor versions are only logged and still parsed; a parsing error aborts the whole package; write operations are unlocked MMIO read-modify-write through the common layer; multiple resources are rejected; `trp_alloc()` has careful first-package cleanup requirements.

Test signals: probe with valid/invalid TPMI resources, duplicate domains, non-root system domains, PL1/PL2/PL4 availability, package removal, powercap control type lifetime across multiple devices, perf PMU event visibility, and sysfs reads/writes against TPMI registers.
