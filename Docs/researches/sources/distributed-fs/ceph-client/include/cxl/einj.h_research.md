# sources/distributed-fs/ceph-client/include/cxl/einj.h

Purpose: declares the optional ACPI APEI EINJ CXL protocol error-injection interface.

Important APIs, types, and flow: when `CONFIG_ACPI_APEI_EINJ_CXL` is enabled, APIs expose available CXL error types through seq_file, inject errors for a downstream-port PCI device, inject RCH errors by RCRB base, and report initialization state. Disabled stubs return `-ENXIO` or `false`.

State and persistence: state is owned by the EINJ implementation; this header only exposes availability and injection entry points. No persistence exists.

Dependencies and integration: depends on ACPI APEI EINJ, PCI devices, seq_file, and CXL error handling paths.

Risks and test signals: error injection is inherently disruptive and must be gated by capability and initialization checks. Signals include disabled-Kconfig stub behavior, debugfs/sysfs available-type output, valid/invalid port injection, RCH path tests, and CXL RAS/CPER event observation after injection.
