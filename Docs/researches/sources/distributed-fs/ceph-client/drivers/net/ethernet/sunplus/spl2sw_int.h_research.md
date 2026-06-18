# sources/distributed-fs/ceph-client/drivers/net/ethernet/sunplus/spl2sw_int.h

Purpose: Declares the Sunplus interrupt and NAPI poll entry points.

Important APIs: `spl2sw_rx_poll()` and `spl2sw_tx_poll()` are passed to NAPI registration; `spl2sw_ethernet_interrupt()` is passed to `devm_request_irq()`.

State and dependencies: The prototypes assume `struct spl2sw_common` can be recovered from the NAPI container or IRQ `dev_id`. Implementation depends on the shared descriptor rings and interrupt mask lock in `spl2sw_common`.

Risks and test signals: Because these functions are invoked by core networking/IRQ contexts, signature changes or missing headers break probe-time registration. Build-test with NAPI and IRQ paths enabled; runtime-test interrupt masking/unmasking around poll completion.
