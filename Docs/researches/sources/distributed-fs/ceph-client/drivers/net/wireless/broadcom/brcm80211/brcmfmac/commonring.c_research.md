# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/commonring.c

Purpose: Implements generic circular ring pointer management for msgbuf-style host/device rings, abstracting producer/consumer arithmetic and hardware pointer synchronization callbacks.

Important APIs/types/functions: Provides callback registration, ring config, lock/unlock, write availability, single/multiple write reservation, write complete/cancel, read pointer retrieval, and read complete. It manages `r_ptr`, `w_ptr`, `f_ptr`, `depth`, `item_len`, `buf_addr`, `was_full`, and callback context.

Control flow: Bus/protocol configures a ring, writers reserve item memory, fill descriptors, then publish with `write_complete()` which writes `w_ptr` and rings the doorbell. Readers refresh `w_ptr`, consume a contiguous span from `r_ptr`, then publish the new read pointer.

State and persistence behavior: Runtime state is contained in `struct brcmf_commonring`. Device-visible pointer state is persisted only through callbacks.

Dependencies and integration points: Used by PCIe/msgbuf ring code. Depends on core types and Broadcom utility headers.

Risks: Uses one empty slot to distinguish full from empty. Multi-reserve only returns contiguous space up to ring end. `write_cancel()` assumes valid reserved count. Missing pointer callbacks make completion return `-EIO`.

Test signals: Exercise wraparound, full/low-water retry behavior, multi-reserve at end of ring, callback ordering, and IRQ-safe locking.
