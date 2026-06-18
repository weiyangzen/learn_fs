# sources/distributed-fs/ceph-client/drivers/rpmsg/qcom_glink_smem.c

Purpose: Qualcomm GLINK transport over SMEM shared memory. It allocates/acquires SMEM descriptors and FIFOs for a remote PID, exposes RX/TX `qcom_glink_pipe` callbacks, and registers a child device representing the GLINK edge.

Important APIs, types, and functions: `struct qcom_glink_smem` owns the synthetic device, IRQ, mailbox, remote PID, and GLINK native handle. `struct glink_smem_pipe` wraps FIFO pointers and little-endian head/tail fields. `qcom_glink_smem_register()` and `qcom_glink_smem_unregister()` are exported integration APIs. Pipe callbacks include `glink_smem_rx_avail()`, `glink_smem_rx_peek()`, `glink_smem_rx_advance()`, `glink_smem_tx_avail()`, `glink_smem_tx_write()`, and `glink_smem_tx_kick()`.

Control flow: registration allocates a standalone child `struct device`, reads `qcom,remote-pid`, allocates or reuses SMEM descriptor item 478, allocates/reuses TX FIFO item 479, lazily maps RX FIFO item 480 on first RX availability check, requests the edge IRQ with `IRQF_NO_AUTOEN`, acquires mailbox channel 0, installs pipe callbacks, clears local RX tail and TX head, and starts `qcom_glink_native_probe()` with `GLINK_FEATURE_INTENT_REUSE`. The IRQ handler simply calls `qcom_glink_native_rx()`. Unregister disables IRQ, removes GLINK native, frees the mailbox, and unregisters the child device.

State and persistence: shared state is the SMEM descriptor array (`tx.tail`, `tx.head`, `rx.tail`, `rx.head`) and FIFO memory. The driver maintains cached FIFO virtual addresses and the GLINK native pointer. TX reserves `FIFO_FULL_RESERVE + TX_BLOCKED_CMD_RESERVE` bytes to avoid full/empty ambiguity and leave room for read notifications. `wmb()` orders FIFO writes before publishing the head pointer.

Dependencies and integration points: depends on Qualcomm SMEM (`qcom_smem_alloc/get`), mailbox, OF IRQ and `qcom,remote-pid`, and GLINK native. It is not a platform driver itself; another Qualcomm subsystem driver calls the exported register/unregister functions for each edge.

Risks: RX FIFO acquisition is lazy, so early interrupts before item 480 exists produce zero available bytes and logs. Descriptor size must be exactly 32 bytes. Shared head/tail values are remote-controlled little-endian fields, so corruption can break ring accounting. TX alignment rounds head to 8 bytes without explicit padding writes, relying on GLINK framing and reserved FIFO space.

Test signals: exercise SMEM allocation reuse (`-EEXIST`), remote PID parsing, deferred/missing SMEM, RX FIFO lazy acquisition, wrapped RX/TX copies, mailbox failures, intent reuse behavior, and unregister while interrupts are pending. Runtime traces should show GLINK channels appearing over the SMEM edge.
