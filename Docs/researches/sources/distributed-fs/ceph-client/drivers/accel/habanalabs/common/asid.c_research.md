# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/asid.c

Purpose: manages HabanaLabs ASID allocation with a bitmap, reserving ASID 0 for kernel/device CPU use.

Important APIs/functions: `hl_asid_init()` allocates `hdev->asid_bitmap`, initializes the mutex, and sets bit 0. `hl_asid_alloc()` locks the bitmap, finds the first zero bit below `max_asid`, sets it, and returns it; if full it returns 0. `hl_asid_free()` rejects kernel ASID or out-of-range ASIDs with a critical log and otherwise clears the bit. `hl_asid_fini()` destroys the mutex and frees the bitmap.

Control flow: device initialization calls init; context creation allocates ASIDs; context/device teardown frees them; final cleanup calls fini.

State and persistence: `hdev->asid_bitmap` and `asid_mutex` are runtime device state. ASID assignments persist while contexts live.

Dependencies: HabanaLabs device structures, Linux bitmap/slab/mutex helpers.

Risks: returning 0 for allocation failure overlaps the reserved kernel ASID value, so callers must treat 0 as failure for user contexts. `hl_asid_free()` lacks locking around `clear_bit()`, which relies on caller-side serialization or atomic bitops being sufficient for the driver contract.

Test signals: bitmap allocation failure, exhaustion at `max_asid`, reserved ASID rejection, double-free behavior, concurrent allocate/free, and device fini after active contexts are gone.
