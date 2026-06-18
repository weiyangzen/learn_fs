<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sun3_scsi_vme.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/sun3_scsi_vme.c

## Purpose
`sun3_scsi_vme.c` is a tiny wrapper that builds the Sun3 NCR5380 front-end in VME mode. It defines `SUN3_SCSI_VME` and includes `sun3_scsi.c`, causing that implementation to compile with VME-specific register programming, probing, naming, and DVMA helpers.

## Important APIs, Types, And Functions
The file declares no standalone functions or data structures. Its only API effect is the `SUN3_SCSI_VME` preprocessor symbol, which changes `sun3_scsi.c` behavior: the driver name becomes `sun3_scsi_vme`, the SCSI host name becomes "Sun3 NCR5380 VME SCSI", VME resources are probed, VME DVMA mapping is used, and VME-specific DMA address/count/fifo/interrupt-vector registers are programmed.

## Control Flow
There is no runtime control flow in this file itself. Compilation flows into `sun3_scsi.c` with the VME branch enabled. The resulting platform driver is registered through `module_platform_driver_probe()` from the included file and probes VME MMIO/IRQ resource pairs.

## State And Persistence Behavior
No independent state is stored here. All runtime state is the file-static Sun3 NCR5380 state from `sun3_scsi.c`, including the single-controller DMA globals and NCR5380 host data. The wrapper creates no persistent state.

## Dependencies And Integration Points
This file depends entirely on `sun3_scsi.c`. It integrates through Kbuild/compilation rather than a C-call boundary, so source-level changes to `sun3_scsi.c` directly affect the VME variant.

## Risks
The primary risk is that the wrapper hides a second compiled personality of `sun3_scsi.c`; changes tested only in the on-board build may break the VME build. VME-specific risks inherited from the included file include resource scanning, board detection through CSR behavior, VME interrupt-vector setup, and packed FIFO residual handling.

## Test Signals
Test signals are compile coverage for the VME object, platform alias/name matching for `sun3_scsi_vme`, VME resource probing, IRQ vector programming, VME DVMA map/unmap, and the full Sun3 NCR5380 DMA/interrupt test set under `SUN3_SCSI_VME`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sun3_scsi_vme.c -->
