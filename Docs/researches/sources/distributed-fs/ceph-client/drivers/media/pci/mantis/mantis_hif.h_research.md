# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_hif.h

- Purpose: Defines symbolic operation IDs for Mantis HIF memory and I/O transactions.
- Important APIs/types/functions: `MANTIS_HIF_MEMRD`, `MANTIS_HIF_MEMWR`, `MANTIS_HIF_IOMRD`, `MANTIS_HIF_IOMWR`.
- Control flow: These constants classify host-interface operations, while callable prototypes are exported through `mantis_link.h`.
- State and persistence: No state or persistence.
- Dependencies and integration points: Used by HIF/CAM code to describe GPIF operation types.
- Risks: Constants are not strongly typed; mismatches would only surface at call sites or logs.
- Test signals: Compile coverage and CAM HIF transaction tests.
