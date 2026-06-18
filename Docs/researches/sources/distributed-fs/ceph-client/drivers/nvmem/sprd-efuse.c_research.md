# sources/distributed-fs/ceph-client/drivers/nvmem/sprd-efuse.c

Purpose: Spreadtrum AP eFuse NVMEM provider with read and permanent program support for the normal eFuse region.

Important APIs/types/functions: `struct sprd_efuse_variant_data` defines normal block count, block offset, and double-data mode. `sprd_efuse_lock()` serializes with mutex and hardware spinlock. `sprd_efuse_raw_read()` controls read power and optional double mode. `sprd_efuse_raw_prog()` writes magic, powers/programs, optionally auto-checks/locks, handles error flags, and clears magic. `sprd_efuse_read()`/`sprd_efuse_write()` are NVMEM callbacks.

Control flow: probe maps MMIO, obtains hwspinlock and enable clock, initializes mutex/variant data, and registers byte-granular read/write NVMEM sized to normal blocks. Reads lock, enable clock, compute physical block as logical offset plus variant offset, read one block, shift/copy requested bytes, disable clock, unlock. Writes lock, enable clock, choose permanent block lock only for full-block writes, program, disable clock, unlock.

State/persistence: eFuse programming is permanent. Runtime state includes clock, lock, MMIO base, and variant geometry.

Dependencies/integration: OF compatible `sprd,ums312-efuse`; depends on hwspinlock, clock, MMIO, and legacy fixed cells.

Risks: write callback passes raw `offset` to `sprd_efuse_raw_prog()` rather than the block index plus normal-block offset used by reads, which is a high-value item to verify against hardware expectations. Full-block writes lock the block against future programming. Power sequencing/magic register handling must unwind on all errors.

Test signals: hwspinlock timeout, clock failure, read error flag clearing, write error flag clearing, partial versus full-block write lock behavior, and verification that logical write offsets map to intended physical blocks.
