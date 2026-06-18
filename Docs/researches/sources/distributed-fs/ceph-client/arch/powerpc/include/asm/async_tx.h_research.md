# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/async_tx.h

Purpose: selects PowerPC DMA offload capability flags for the async_tx subsystem.

Important APIs/types/functions: defines `async_tx_issue_pending_all()` as an empty inline hook and `async_tx_find_channel(dep, type)` as a macro passing `async_tx_cap_mask_all` to `__async_tx_find_channel()`.

Control flow: callers use the generic async_tx channel lookup path. This header does not perform runtime work beyond the macro call.

State and persistence: no state is stored. DMA channel ownership and descriptors are managed by async_tx and DMA engine code.

Dependencies and integration points: includes `<linux/async_tx.h>`. It integrates architecture policy with async XOR/memcpy/PQ users.

Risks: the empty issue-pending hook means PowerPC relies on lower layers to submit work; if an architecture-specific pending flush were needed it would be absent. The all-capability mask assumes generic filtering is sufficient.

Test signals: build async_tx users, run DMA engine self-tests or RAID acceleration paths, and verify channel selection/fallback works when no DMA engine is present.
