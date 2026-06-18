# sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/loongson_module.h

Purpose: shares module-level Loongson symbols between module entry and core driver.

Important APIs/types/functions: declares `extern int loongson_vblank` and `extern struct pci_driver lsdc_pci_driver`.

Control flow: no executable flow.

State and persistence: `loongson_vblank` is runtime module parameter state used by PCI probe.

Dependencies and integration points: included by `loongson_module.c` and `lsdc_drv.c`.

Risks and test signals: declarations must match definitions. Test compile/link and vblank parameter behavior.
