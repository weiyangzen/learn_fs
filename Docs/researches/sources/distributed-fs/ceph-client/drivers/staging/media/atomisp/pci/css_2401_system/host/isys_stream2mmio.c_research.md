# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/host/isys_stream2mmio.c

Purpose: defines the number of stream IDs supported by each CSS 2401 Stream2MMIO controller.

Important APIs/types/functions: `N_STREAM2MMIO_SID_PROCS` maps controller 0 to all SIDs and controllers 1/2 to four SIDs.

Control flow: static initialization only. Consumers loop up to the count for a controller.

State and persistence: read-only global constant.

Dependencies and integration: includes `isys_stream2mmio.h`; used by private state capture/dump code and input-buffer controller integration.

Risks and test signals: count mismatch causes invalid or missing SID register access. Tests should cover all Stream2MMIO controllers and SID loop bounds.
