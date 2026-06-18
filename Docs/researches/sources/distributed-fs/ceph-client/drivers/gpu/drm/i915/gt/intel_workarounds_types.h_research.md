# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_workarounds_types.h

Purpose: defines the compact data structures used by the i915 workaround framework to describe register programming and grouped workaround lists.

Important APIs/types: `struct i915_wa` stores either an `i915_reg_t` or `i915_mcr_reg_t`, clear/set/read masks, and bitfields identifying masked-register and MCR semantics. `struct i915_wa_list` stores the owning `intel_gt`, list label, engine label, dynamically allocated array, entry count, and logical workaround count.

Control flow: the header contains no executable flow. Its data shape drives `_wa_add()` merge/sort behavior, MMIO apply/verify loops, context LRI emission, and whitelist slot programming.

State and persistence behavior: `i915_wa_list` persists generated workaround state in GT and engine objects across initialization and later apply/verify calls. `wa_count` can exceed `count` because multiple logical workarounds may merge into one register entry. `read` identifies bits safe/required to validate and can be zero for write-only or deliberately unverifiable entries.

Dependencies and integration points: includes Linux integer types and `i915_reg_defs.h` for typed MMIO register wrappers. Forward-declares `struct intel_gt` for ownership without importing full GT definitions.

Risks: the union means code must respect `is_mcr` before choosing singleton or MCR access paths. Incorrect `read` masks can create false CI failures or hide lost settings. Bitfield packing should remain simple because these structures are allocated in arrays and copied by value.

Test signals: validated indirectly by all workaround construction/apply/verify paths; compile failures catch register type changes.
