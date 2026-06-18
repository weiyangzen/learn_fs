# sources/distributed-fs/ceph-client/drivers/pps/clients/pps_parport.c

Purpose: PPS client for parallel-port ACK interrupt pulses, with optional polling to capture the clear edge.

Important APIs/types/functions: `struct pps_client_pp`, module parameter `clear_wait`, `parport_irq()`, `parport_attach()`, `parport_detach()`, `signal_is_set()`, and `pps_parport_driver`.

Control flow: parport attach validates `clear_wait`, allocates state and an IDA index, registers an exclusive parport device with an IRQ callback, claims the port, registers a PPS source with both-edge support, stores the clear-wait count, enables port IRQs, and logs attachment. IRQ handler timestamps assert immediately; if clear capture is enabled it disables local IRQs, verifies signal is still high, polls status up to `cw` reads for signal clear, timestamps clear if observed, and emits assert plus optional clear. Repeated clear timeouts disable clear capture. Detach identifies its current parport device, disables IRQ, unregisters PPS, releases/unregisters parport device, frees IDA index and memory.

State/dependencies: per-port `pps_client_pp` holds parport device, PPS device, timeout counters, and index. Depends on parport ops and PPS core.

Risks: detach relies on `port->cad` and a comment calls this ugly; local IRQ disabling while polling must remain bounded; clear edge can be lost; repeated timeouts silently degrade to assert-only capture; attach rollback has several resource stages.

Test signals: attach/detach on parport hardware, IRQ assert capture, clear capture with different `clear_wait` values, timeout degradation after five failures, IDA reuse, and exclusive claim conflicts.
