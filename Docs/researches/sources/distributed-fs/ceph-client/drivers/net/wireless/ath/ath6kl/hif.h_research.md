# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/hif.h

## Purpose
`hif.h` defines the host interface contract and shared structures for ath6kl bus implementations. It includes mailbox address layout, request flag bits, scatter-gather limits, interrupt register layouts, `struct ath6kl_device`, and `struct ath6kl_hif_ops`.

## Important APIs, types, and functions
Important constants include mailbox block sizes, DMA buffer size, mailbox base/width/end addresses, extended mailbox and GMBOX ranges, SDIO async IRQ mode, scatter request limits, communication timeout, and combined HIF request flag macros such as `HIF_WR_ASYNC_BLOCK_INC`, `HIF_RD_SYNC_BLOCK_FIX`, and `HIF_WR_SYNC_BYTE_INC`. `struct bus_request` tracks a bus transaction or scatter request. `struct hif_scatter_req` describes multi-entry transfers with completion, status, optional virtual DMA bounce buffer, and inline `scat_list`. `struct ath6kl_irq_proc_registers` and `struct ath6kl_irq_enable_reg` mirror target interrupt register tables. `struct ath6kl_hif_ops` is the bus implementation vtable.

## Control flow and integration
HTC mailbox code uses HIF request flags to submit mailbox reads/writes, HIF common code reads/writes interrupt registers, BMI uses HIF read/write paths during firmware boot, and HTC pipe code uses pipe-specific operations. Interrupt bottom halves receive `struct ath6kl_device`, whose `htc_cnxt` points back to HTC and whose `ar` points to the root driver object.

## State and persistence behavior
The header defines persistent per-device HIF state but does not allocate it. Bus implementations persist queues of `bus_request`, scatter pools, interrupt enable shadows, and private `ar->hif_priv`. Request flags encode direction, sync/async mode, byte/block basis, and fixed/incremental address behavior, and those flags must remain consistent with HIF implementation semantics.

## Dependencies and integration points
`hif.h` includes `common.h`, `core.h`, and Linux scatterlist definitions. The include of `core.h` makes this header tightly coupled to the driver root state. It exports setup/mask/unmask/poll/RX-control/interrupt/scatter functions implemented in `hif.c`.

## Risks and test signals
Risks include duplicate scatter limit constants, bus implementations misinterpreting request flags, inline flexible array sizing for scatter items, packed interrupt register layout mismatch with firmware, and cyclic header dependencies. Test signals include compiling every HIF implementation, SDIO CMD53 fixed/incremental transfer tests, scatter limits, mailbox address range use, interrupt register table reads, and suspend/resume with active bus queues.
