# sources/distributed-fs/ceph-client/drivers/net/ethernet/sunplus/spl2sw_desc.h

Purpose: Declares the descriptor lifecycle API used by the Sunplus platform driver, MAC reset path, and NAPI cleanup logic.

Important APIs: Exports RX flush, TX/RX clean, combined clean/free, TX/RX init, descriptor allocation, and full descriptor initialization helpers. The separation lets probe allocate and initialize once, reset reflush RX descriptors without reallocating, and remove free all DMA resources.

State and dependencies: The header assumes `struct spl2sw_common` and descriptor constants from `spl2sw_define.h`. Callers own locking and device quiescing before invoking cleanup or reinitialization.

Risks and test signals: The API is low-level and not self-serializing. Tests should exercise all call sites: probe failure after allocation, normal remove, TX timeout reset, and cleanup with partially initialized RX queues.
