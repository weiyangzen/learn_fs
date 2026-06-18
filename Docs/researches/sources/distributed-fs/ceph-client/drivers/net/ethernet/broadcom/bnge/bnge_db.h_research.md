# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_db.h

Purpose: Defines 64-bit doorbell record encoding used by `bnge` queue/ring notification paths.

Important APIs/types: Doorbell bit constants define epoch, toggle, XID, L2 path, valid bit, and SQ/SRQ/CQ/NQ type encodings. `struct bnge_db_info` stores the MMIO doorbell pointer, fixed key bits, ring mask, epoch mask, and epoch shift. `DB_EPOCH()` and `DB_RING_IDX()` compose the dynamic index bits used by `bnge_db_write()` in `bnge.h`.

Control flow: TX/RX and completion paths construct per-ring `bnge_db_info`, then doorbell hardware with `db_key64 | DB_RING_IDX(db, idx)`. Epoch bits allow hardware to distinguish wrapped ring indices.

State/persistence: Doorbell geometry persists per ring and is derived from hardware/resource setup. No standalone runtime state exists outside the struct embedded elsewhere.

Dependencies/integration: Included by `bnge.h`; consumed by TX/RX and queue resource files. It assumes 64-bit MMIO writes through `bnge_writeq()`.

Risks/test signals: Incorrect masks or shifts cause missed or misdirected hardware notifications. Test ring wrap, queue start/stop, SQ/CQ/NQ arm paths, 32-bit atomic write behavior through caller, and hardware generation compatibility.
