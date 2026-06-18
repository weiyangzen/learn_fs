# sources/distributed-fs/ceph-client/drivers/usb/cdns3/host-export.h

Purpose: exposes the Cadence host-role initializer to core code when host support is enabled and provides an inline `-ENXIO` fallback otherwise.

Important APIs/types/functions: declares `cdns_host_init(struct cdns *)` under `CONFIG_USB_CDNS_HOST`; otherwise defines an inline `cdns_host_init` returning `-ENXIO` and an empty `cdns_host_exit` stub.

Control flow: no runtime control beyond the fallback return path. It lets `core.c` compile and report unsupported host role when Kconfig excludes host support.

State and persistence: no owned state. The real host initializer fills `cdns->roles[USB_ROLE_HOST]`.

Dependencies and integration: included by `core.c` and `host.c` to bridge the role framework to xHCI platform-device creation.

Risks: the guard macro uses `CONFIG_USB_CDNS_HOST`, while core mode checks distinguish CDNS3/CDNSP host configs; Kconfig consistency is required to avoid unexpected `-ENXIO`.

Test signals: build host-disabled and host-enabled variants and verify OTG/host-only probes reject unsupported host mode gracefully.
