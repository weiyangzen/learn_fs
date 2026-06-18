# sources/distributed-fs/ceph-client/drivers/parport/parport_sunbpp.c

Purpose: SBUS/OpenFirmware platform driver for Sun bidirectional parallel-port hardware (`SUNW,bpp`). It adapts Sun BPP register semantics to the generic parport operations interface.

Important APIs/types/functions: `parport_sunbpp_ops` supplies data, control, status, IRQ, direction, and state callbacks. `status_sunbpp_to_pc()` and `control_sunbpp_to_pc()` translate Sun register polarity into PC parport bit definitions. `bpp_probe()` maps OF resources, duplicates ops, registers a parport, requests a shared IRQ with `parport_irq_handler`, enables device interrupts, initializes forward direction, stores drvdata, and announces the port. `bpp_remove()` performs the reverse.

Control flow/state: state is almost entirely hardware register state in `struct bpp_regs`; save/restore persists the parport control bits in `parport_state.u.pc.ctr`. Probe stores the mapped base address in `p->base`, size in `p->size`, and parent device in `p->dev`. Remove disables IRQs before freeing the IRQ, unmaps the OF resource, drops the port reference, and frees duplicated ops.

Dependencies/integration: integrates platform OF matching, SBUS I/O accessors, SPARC OpenPROM/DMA headers, and parport IEEE1284 generic helpers. Risks include register polarity mistakes, assuming `op->archdata.irqs[0]` exists, using `parport_put_port()` rather than `parport_del_port()` after `parport_remove_port()`, and limited non-SPARC coverage. Test signals include OF match/probe on Sun BPP hardware, status/control bit readback, shared IRQ activity, clean unbind, and IEEE1284 fallback transfers.
