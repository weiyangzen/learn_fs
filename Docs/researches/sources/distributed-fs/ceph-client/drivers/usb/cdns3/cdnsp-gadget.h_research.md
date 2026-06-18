# sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdnsp-gadget.h

Purpose: central CDNSP gadget-controller contract. The complete 1616-line file was read. It defines register layouts, bitfields, TRBs, contexts, rings, endpoint/request/device objects, state flags, helper macros, and cross-file prototypes.

Important APIs/types/functions: register structs `cdnsp_cap_regs`, `cdnsp_op_regs`, `cdnsp_port_regs`, `cdnsp_intr_reg`, `cdnsp_run_regs`; hardware context structs `cdnsp_container_ctx`, `cdnsp_slot_ctx`, `cdnsp_ep_ctx`; transfer structs `cdnsp_command`, `cdnsp_stream_info`, `cdnsp_ep`, `cdnsp_transfer_event`, `union cdnsp_trb`, `cdnsp_segment`, `cdnsp_td`, `cdnsp_ring`, `cdnsp_erst`, `cdnsp_request`, and `cdnsp_device`; plus prototypes for memory, controller glue, ring/command queueing, context lookup, and gadget callbacks.

Control flow: no major runtime flow except `cdnsp_read_64()`, `cdnsp_write_64()`, and `next_request()`. Its macros drive flow in other files by encoding command doorbells, port changes, TRB types, completion codes, cycle ownership, stream IDs, setup metadata, and endpoint indexes.

State and persistence: defines all persistent in-memory state shapes. `cdnsp_device` owns controller lifetime state; `cdnsp_ep` endpoint state; `cdnsp_ring`/`cdnsp_td` queued-transfer state; context structs mirror DMA memory consumed by hardware.

Dependencies/integration: Linux USB gadget/IRQ/MMIO helpers. Included by gadget, memory, ring, EP0, trace, and debug code. Layouts must match Cadence CDNSP/xHCI-like hardware ABI and Linux gadget expectations.

Risks: bitfield and layout drift can break hardware ABI; endpoint index conversions must remain consistent; stream constants cap supported streams; context size and TRB ownership rules are fragile.

Test signals: full CDNSP build, trace-decoded context programming, ring wrap and cycle-bit behavior, endpoint mapping checks, speed decoding, and successful control/bulk/interrupt/isoc/stream endpoint operation.
