# sources/distributed-fs/ceph-client/drivers/misc/ocxl/context.c

## Purpose
This file manages OCXL per-process AFU contexts: PASID allocation, process-element attach/detach, fault-event recording, per-process MMIO and IRQ trigger-page mmap, and context cleanup.

## Important APIs, types, and functions
Public functions are `ocxl_context_alloc()`, `ocxl_context_attach()`, `ocxl_context_mmap()`, `ocxl_context_detach()`, `ocxl_context_detach_all()`, and `ocxl_context_free()`. Internal helpers include `xsl_fault_error()`, `map_pp_mmio()`, `map_afu_irq()`, `ocxl_mmap_fault()`, `check_mmap_mmio()`, and `check_mmap_afu_irq()`.

## Control flow and state
Allocation reserves a PASID from the AFU context IDR, initializes locks/wait queues/IRQ IDR, marks status `OPENED`, and takes an AFU reference. Attach transitions `OPENED` to `ATTACHED` by adding a process element on the link using current MM context, AMR, PIDR, TIDR, and fault callback. mmap validates whether the offset targets per-process MMIO or an IRQ page, sets PFNMAP/IO/noncached VMA ops, and faults insert the appropriate PFN. Detach marks the context closed, terminates the AFU PASID, removes the process element unless timeout makes it unsafe, and force-detach invalidates mappings.

## State and persistence behavior
State lives for the context fd: PASID, status, mapping pointer, xsl error record, IRQ IDR, and link process element. A detach timeout can intentionally leave the context unfreed and PASID allocated to avoid hardware checkstop risk.

## Dependencies and integration points
It depends on PowerPC MM context IDs, OCXL link APIs, config PASID termination, IRQ mapping helpers, file mapping invalidation, and internal AFU structures. `file.c` invokes it for open, attach, mmap, release, read/poll events, and ioctl operations.

## Risks and test signals
Risks include PASID leaks on detach timeout, status transitions under concurrent ioctl/release, mmap offset validation, stale mapping invalidation, fault callback races, and `ocxl_afu_irq_free_all()` cleanup. Test signals include context open/attach/release, mmap before/after attach, IRQ page mmap permission checks, xsl fault event wake/read, force detach during device removal, and PASID termination timeout handling.
