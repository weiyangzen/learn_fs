<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/dart.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/dart.h

Purpose: register and table bit definitions for Apple/IBM U3/U4 DART IOMMU support.

Important APIs/types/functions: DART register offsets `DART_CNTL`, `DART_EXCP_*`, `DART_TAGS_*`, U4 base/size offsets, control bits for enable/flush/one-entry invalidate/idle/parity, table entry bits `DARTMAP_VALID` and `DARTMAP_RPNMASK`, and page constants `DART_PAGE_SHIFT/SIZE`.

Control flow: no executable logic; macros are consumed by `dart_iommu.c` to program the hardware.

State and persistence: no state. The macros describe persistent hardware register fields and DART table entry format.

Dependencies and integration points: tightly coupled to `dart_iommu.c` and U3/U4 chipset manuals. `DART_REG`, `DART_IN`, and `DART_OUT` assume a file-scope `dart` MMIO pointer.

Risks: register offsets and masks are hardware ABI. Incorrect values can corrupt DMA translations or hang TLB invalidation.

Test signals: DART initialization, DMA mapping/unmapping on U3/U4 systems, and successful suspend restore validate the definitions indirectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/dart.h -->
