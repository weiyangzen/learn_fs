# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/commonring.h

Purpose: Declares the shared common ring structure and API for brcmfmac msgbuf-style ring users.

Important APIs/types/functions: `struct brcmf_commonring` contains read/write/final pointers, depth, item length, buffer address, five pointer/doorbell callbacks, callback context, spinlock, saved IRQ flags, init/full flags, and `outstanding_tx`. Declares all commonring operations and item-count/length macros.

Control flow: Callers allocate the ring and backing memory, register callbacks, configure dimensions, then use reserve/complete/read APIs under appropriate lock discipline.

State and persistence behavior: Runtime-only in-memory state. `outstanding_tx` is declared for users but not manipulated by `commonring.c`.

Dependencies and integration points: Consumed by msgbuf and bus code that manages shared host/device queues.

Risks: Partially initialized callback sets fail only at runtime. `buf_addr` is typeless and relies on kernel/GNU C pointer arithmetic. Lock use is caller-coordinated.

Test signals: Compile with sparse lock annotations; validate pointer reset after config, attach/detach, and ring wrap under load.
