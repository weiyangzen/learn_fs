# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/include/mmu/sh_mmu_mrfld.h

## Purpose
This header exposes the Merrifield-specific Silicon Hive/ISP MMU client descriptor for AtomISP. It lets generic ISP MMU/HMM code bind to Merrifield hardware-specific PTE and TLB behavior.

## Important APIs, Types, And Data
- `extern struct isp_mmu_client sh_mmu_mrfld;` declares the hardware client consumed by `isp_mmu_init()`.

## Control Flow
There is no executable logic in this header. Platform or AtomISP initialization code selects `sh_mmu_mrfld` and passes it to the generic MMU layer, which then calls its callbacks for page-directory base setup, PTE conversion, and TLB flushing.

## State And Persistence
The declaration points to implementation-defined static/global state elsewhere. Runtime MMU state is held in `struct isp_mmu`, not in this header.

## Dependencies And Integration Points
The header depends conceptually on `struct isp_mmu_client` from `isp_mmu.h`, though it does not include that file itself. It integrates Merrifield-specific MMU code with the generic AtomISP HMM/ISP MMU layer.

## Risks
- Because the header does not include `isp_mmu.h`, includers must have seen `struct isp_mmu_client` first or compilation fails.
- The external symbol must be provided exactly once by the Merrifield MMU implementation.
- Wrong client selection would corrupt page-table interpretation or TLB maintenance.

## Test Signals
Build tests should verify include ordering and symbol resolution. Runtime validation should initialize the generic MMU with `sh_mmu_mrfld`, map/unmap HMM buffers, verify PTE physical translations, and confirm Merrifield TLB flush callbacks run on mapping changes.
