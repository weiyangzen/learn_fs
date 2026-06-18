## sources/distributed-fs/ceph-client/arch/powerpc/platforms/ps3/htab.c

### Purpose
`htab.c` implements PS3 hash page table operations through LV1 hypervisor calls.

### Important APIs, Types, And Functions
Important functions are `ps3_hpte_insert()`, `ps3_hpte_updatepp()`, `ps3_hpte_invalidate()`, `ps3_hpte_clear()`, and `ps3_hpte_init()`. `ps3_hpte_remove()` and bolted PP update are not implemented. A spinlock serializes HTAB operations.

### Control Flow
Insert encodes HPTE V/R fields, translates physical to LPAR addresses, asks LV1 to insert into primary/secondary groups, reads back entries to determine secondary placement, and returns the Linux slot encoding. Updatepp reads the group, compares AVPN/valid bit, invalidates matching entries, and returns `-1` so the caller reinserts. Invalidate writes zero to an LV1 HTAB slot. Clear iterates every HPTE, zeros it, then shuts down PS3 memory state for kexec.

### State, Persistence, And Dependencies
State is the hypervisor HTAB and global `ppc64_pft_size`. Dependencies include hash MMU encoding helpers, LV1 HTAB calls, PS3 physical-to-LPAR translation, and PS3 memory teardown.

### Integration Points
`ps3_hpte_init()` installs the operations into `mmu_hash_ops`.

### Risks
Unimplemented remove/update-bolted paths can panic or log if used unexpectedly. Insert BUGs if all victim entries are bolted. LV1 readback is required because inserted secondary status is not otherwise known.

### Test Signals
Hash MMU boot, memory pressure, permission changes, kexec clear path, and fault tests that trigger secondary HPTE insertion validate behavior.
