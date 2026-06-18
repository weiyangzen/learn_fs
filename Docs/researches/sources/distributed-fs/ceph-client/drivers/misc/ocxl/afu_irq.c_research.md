# sources/distributed-fs/ceph-client/drivers/misc/ocxl/afu_irq.c

## Purpose
This file allocates, maps, handles, and frees AFU interrupt trigger pages for OCXL contexts. It bridges OpenCAPI link hardware IRQ allocation to Linux virtual IRQs and optional per-IRQ callbacks such as eventfd notification.

## Important APIs, types, and functions
The private `afu_irq` stores ID, hardware IRQ, virq, name, callback, cleanup callback, and private data. Public functions are `ocxl_irq_offset_to_id()`, `ocxl_irq_id_to_offset()`, `ocxl_irq_set_handler()`, `ocxl_afu_irq_alloc()`, `ocxl_afu_irq_free()`, `ocxl_afu_irq_free_all()`, and `ocxl_afu_irq_get_addr()`. Internal helpers are `setup_afu_irq()`, `release_afu_irq()`, `afu_irq_handler()`, and `afu_irq_free()`.

## Control flow and state
Allocation reserves an ID in the context IRQ IDR, allocates a hardware IRQ from the OCXL link, creates a Linux IRQ mapping, requests the IRQ, traces it, and returns an mmap offset. The interrupt handler dispatches the registered callback if present, otherwise drops the interrupt. Free removes the IDR entry, unmaps any userspace trigger-page mapping, frees the virq, calls private cleanup, returns the hardware IRQ to the link, and frees memory.

## State and persistence behavior
State is per-context and held in `ctx->irq_idr` under `ctx->irq_lock`. Trigger-page mappings can be invalidated through `unmap_mapping_range()` when an IRQ is freed. No persistent state exists beyond context lifetime.

## Dependencies and integration points
It depends on Linux IRQ domains, XIVE trigger-page data, PowerNV OCXL link IRQ APIs, context/AFU internal structures, and tracing. `file.c` uses it for `OCXL_IOCTL_IRQ_ALLOC`, `IRQ_FREE`, `IRQ_SET_FD`, and mmap of trigger pages.

## Risks and test signals
Risks include IDR iteration while freeing all without IDR removal, callback lifetime, trigger page address lookup, mapping invalidation, link IRQ pool exhaustion, and virq cleanup on setup failure. Test signals include IRQ allocate/free loops, eventfd handler delivery, mmap trigger pages, freeing mapped IRQs, link IRQ exhaustion, and context release cleanup.
