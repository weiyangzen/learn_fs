# sources/distributed-fs/ceph-client/drivers/bus/mhi/ep/mmio.c

Purpose: endpoint MMIO helper layer for reading/writing MHI endpoint registers, managing interrupt masks/status, discovering host context base addresses, reading doorbells, publishing execution environment, and resetting endpoint-visible MHI state.

Important APIs: basic accessors `mhi_ep_mmio_read/write/masked_read/masked_write`; interrupt helpers for control, command DB, channel DB, event DB masking/status; base readers `mhi_ep_mmio_get_chc_base()`, `mhi_ep_mmio_get_erc_base()`, `mhi_ep_mmio_get_crc_base()`; `mhi_ep_mmio_get_db()`; state helpers `mhi_ep_mmio_get_mhi_state()`, `mhi_ep_mmio_set_env()`, `mhi_ep_mmio_clear_reset()`, `mhi_ep_mmio_reset()`, `mhi_ep_mmio_init()`, and `mhi_ep_mmio_update_ner()`.

Control flow: initialization reads CHDB/ERDB offsets and event-ring counts, then clears MHI control/status and all interrupt status. Channel DB enable/disable updates both hardware mask registers and a local mask cache used by IRQ processing. Doorbell reads combine high/low 32-bit registers into host ring write pointers.

State and persistence: maintains cached `chdb[].mask/status`, event ring counts, hardware event ring count, and host physical base addresses in `mhi_ep_cntrl`. Hardware interrupt masks and MHI status persist while endpoint BAR state is powered.

Dependencies and integration: depends on endpoint register offsets from `internal.h`, common masks, `readl/writel`, and `mhi_ep_cntrl->mmio`. It is called by endpoint main, ring, and state-machine code.

Risks: interrupt mask naming is nonstandard: writing 1 enables. Incorrect local mask synchronization drops or processes disabled channel doorbells. MMIO reset clears status and all interrupt bits, so ordering around host reset matters. Test signals include register init, all channel/event mask rows, doorbell high/low composition, host base address reads, MHI reset clear, READY/SYSERR status writes via state code, and IRQ ack/clear behavior.
