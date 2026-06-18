# sources/distributed-fs/ceph-client/drivers/usb/cdns3/gadget-export.h

Purpose: provides conditional gadget initialization declarations for CDNSP and CDNS3 gadget roles, returning `-ENXIO` stubs when the relevant gadget support is not built.

Important APIs/types/functions: declares or stubs `cdnsp_gadget_init(struct cdns *)` under `CONFIG_USB_CDNSP_GADGET` and `cdns3_gadget_init(struct cdns *)` under `CONFIG_USB_CDNS3_GADGET`.

Control flow: no runtime flow beyond inline fallback stubs. Callers can unconditionally reference these helpers and receive a normal error if a role is disabled.

State and persistence: no owned state. Successful real implementations populate `struct cdns` gadget role fields outside this header.

Dependencies and integration: included by Cadence platform/core files that select the correct gadget initializer based on controller generation and Kconfig.

Risks: build-symbol naming must match Kconfig; a disabled gadget role appears as `-ENXIO`, so probe/mode negotiation must treat that as unsupported rather than hardware failure.

Test signals: host-only, gadget-only, and OTG build matrices verify the inline stubs and declarations line up with compiled implementations.
