# sources/distributed-fs/ceph-client/drivers/usb/dwc3/ulpi.c

Purpose: registers a ULPI bus interface backed by DWC3 `GUSB2PHYACC` accesses so external USB2 PHY registers can be read and written through the controller.

Important APIs/functions: `dwc3_ulpi_init` and `dwc3_ulpi_exit` are exported to core code. Internal helpers are `dwc3_ulpi_busyloop`, `dwc3_ulpi_read`, `dwc3_ulpi_write`, and `dwc3_ulpi_detect_config`. `dwc3_ulpi_ops` supplies ULPI read/write callbacks.

Control flow: init registers a ULPI interface with DWC3-backed ops, stores it in `dwc->ulpi`, then detects specific PHY IDs. Reads and writes compose `GUSB2PHYACC` requests, support extended ULPI addresses, wait for `DONE` with nanosecond-scale delays, and return data or timeout. Exit unregisters the interface and clears the pointer.

State and persistence: persistent state is `dwc->ulpi` and feature flags such as `enable_usb2_transceiver_delay` set for Microchip USB3340. Register operations affect external PHY state through the DWC3 access window.

Dependencies and integration: uses Linux ULPI interface APIs, ULPI register constants, delays, time constants, and DWC3 IO/core helpers. It integrates with PHY management and DWC3 core initialization.

Risks: timeouts can occur if the PHY is absent, clocked incorrectly, or suspended. The busy loop briefly sleeps if SUSPHY is set, but callers still rely on hardware readiness. Extended address timing differs from normal reads/writes. Vendor-specific detection currently handles only Microchip USB3340.

Test signals: successful ULPI registration, readable PHY ID values, correct Microchip delay flag setting, and no timeout logs during probe/resume. Hardware tests should include PHY register reads, writes through ULPI drivers, and suspend/resume with SUSPHY transitions.
