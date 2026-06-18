# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_labpc_isadma.h

## Purpose
`ni_labpc_isadma.h` is the conditional interface for optional Lab-PC ISA DMA support. It lets common and ISA front-end code call DMA hooks regardless of whether `CONFIG_COMEDI_NI_LABPC_ISADMA` is enabled.

## Important APIs, Types, And Functions
When the Kconfig option is enabled, the header declares `labpc_init_dma_chan()`, `labpc_free_dma_chan()`, `labpc_setup_dma()`, `labpc_drain_dma()`, and `labpc_handle_dma_status()`. When disabled, it defines static inline no-op versions of the same functions.

## Control Flow
Callers do not branch on Kconfig. `ni_labpc.c` can always call init/free, and `ni_labpc_common.c` can always call setup/drain/status helpers. In disabled builds, no state is allocated and DMA paths are effectively unavailable because `devpriv->dma` remains null.

## State And Persistence
The header itself has no state. Its no-op stubs preserve build compatibility while leaving all runtime DMA state absent.

## Dependencies And Integration Points
The header is included by `ni_labpc.c`, `ni_labpc_common.c`, and `ni_labpc_isadma.c`. It depends on forward-visible Comedi device/subdevice declarations from including source files.

## Risks
The no-op fallback can make user-provided DMA configuration appear accepted while no DMA is actually used. Common code's transfer selection checks `devpriv->dma`, so this should degrade to FIFO transfers, but tests should ensure no call assumes DMA side effects after a no-op setup. Signature drift between declarations and implementations would break one Kconfig variant.

## Test Signals
Test enabled and disabled Kconfig builds, no-op behavior with DMA options, common transfer selection when `devpriv->dma == NULL`, symbol export availability when enabled, and header include order in all Lab-PC compilation units.
