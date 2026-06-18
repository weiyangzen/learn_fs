# sources/distributed-fs/ceph-client/drivers/scsi/elx/include/efc_common.h

## Purpose
`efc_common.h` provides the smallest shared definitions used across the Emulex FC discovery library and transport driver: a DMA buffer descriptor and device-scoped logging macros.

## Important APIs, Types, And Functions
`struct efc_dma` records CPU-visible DMA memory (`virt`), allocation base (`alloc`), bus address (`phys`), allocation size, active length, and the PCI device used for DMA ownership. The logging macros `efc_log_crit`, `efc_log_err`, `efc_log_warn`, `efc_log_info`, and `efc_log_debug` route libefc messages through `dev_*(&efc->pci->dev, ...)`.

## Control Flow And State
There is no executable control flow. The important state behavior is contractual: files that allocate DMA memory fill `virt`, `phys`, and `size`, update `len` when a payload length is meaningful, and clear the structure after freeing. Logging assumes every object passed as `efc` has a valid `pci` pointer.

## Dependencies And Integration Points
The header includes `<linux/pci.h>` and is pulled into `efclib.h`, `efc.h`, command code, ELS construction, and transport code. It is a common ABI between mailbox-command helpers, ELS request buffers, node service-parameter buffers, and hardware receive buffers.

## Risks And Test Signals
Risks are mostly misuse risks: freeing DMA with the wrong `pci_dev`, stale `len` after buffer reuse, or logging with a partially initialized `struct efc`. Test signals include fault-injected DMA allocation/free paths, driver init failure cleanup, and log paths invoked during early attach errors before all higher-level objects exist.
