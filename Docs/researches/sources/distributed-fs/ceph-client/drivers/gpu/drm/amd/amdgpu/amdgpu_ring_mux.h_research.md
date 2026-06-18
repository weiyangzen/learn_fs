## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ring_mux.h

Purpose: declares the software-ring multiplexer data structures and public helpers used by GFX rings to share a real hardware ring.

Important APIs and types: `struct amdgpu_mux_entry` tracks one software ring and the last copied range in both hardware and software pointer spaces. `enum amdgpu_ring_mux_offset_type` identifies control, DE, and CE patch offsets. `enum ib_complete_status` names default, preempted, and completed IB states, although this header's implementation does not use it directly. `struct amdgpu_ring_mux` stores the real ring, entry array, spinlock, resubmit state, timer, and trailing-fence flag. `struct amdgpu_mux_chunk` records one IB's software-ring start/end, fence seqno, and patch offsets.

Control flow: the declared functions initialize/finalize mux state, add software rings, route pointer operations, start/end IB chunk tracking, mark patch offsets, handle trailing fence IRQs, and provide GFX-specific software ring callbacks.

State and persistence: all state is volatile runtime scheduling/preemption metadata; no persistent storage. The structures point to `struct amdgpu_ring` objects owned elsewhere.

Dependencies and integration points: includes Linux timer/spinlock and `amdgpu_ring.h`. Used by GFX ring setup and generic ring IB hooks.

Risks: consumers must maintain `entry_index` consistency and call begin/end/mark in valid order. Chunk offsets use `buf_mask + 1` as a sentinel, which assumes valid ring offsets are always `<= buf_mask`. The header exposes enough mutable structure that misuse outside the mux implementation could break synchronization.

Test signals: compile coverage with GFX software rings enabled, pointer callback tests, and preemption/resubmission validation.
