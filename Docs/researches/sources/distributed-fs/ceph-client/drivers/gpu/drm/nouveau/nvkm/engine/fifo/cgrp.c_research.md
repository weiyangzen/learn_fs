<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/cgrp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/cgrp.c

## Purpose

`cgrp.c` implements FIFO channel-group state: group lifetime, CGID allocation, shared engine contexts, VMM-specific subcontexts, reference management, and recovery state initialization.

## Important APIs, Types, And Functions

`nvkm_cgrp_ectx_get()/put()` manage per-engine group contexts. `nvkm_cgrp_vctx_get()/put()` manage per-engine plus VMM subcontexts, including VMM engine reference counts, instance object allocation, and engine-specific constructor/bind hooks. `nvkm_cgrp_new()` allocates a group, references the VMM, optionally allocates a CGID, and initializes lists/locks. `nvkm_cgrp_ref()`, `nvkm_cgrp_unref()`, and `nvkm_cgrp_put()` manage krefs and IRQ-lock release.

## Control Flow

Channel creation either joins an existing group or creates a private group. When a channel needs an engine context, it asks the group for a vctx; the group reuses an existing engine/VMM context or creates ectx then vctx, invoking engine callbacks to allocate hardware context. Destruction unwinds vctx, ectx, VMM refs, instance objects, and CGID allocation.

## State And Persistence Behavior

Persistent group state includes name, runlist, VMM reference, hardware-group flag, id, channel list/count, ectx/vctx lists, mutex, IRQ lookup lock, recovery atomic state, and kref. Vctx objects persist VMM refs, GPU object instance/VMA, ectx references, and VMM engine reference increments.

## Dependencies And Integration Points

It depends on runlist CHID/CGID allocators, channel code, engine context constructors, MMU/VMM reference tracking, GPU object binding, and channel-group user objects.

## Risks And Edge Cases

Reference balance is subtle across cctx/vctx/ectx layers. Failure after list insertion must call the matching put path. CGID allocation can fail with `-ENOSPC`. VMM engine reference counts must be decremented exactly once to keep TLB invalidation logic correct.

## Test Signals

Signals include successful channel-group creation, shared context reuse across channels in a group, VMM-specific context separation, CGID exhaustion handling, and no leaked VMM engrefs or GPU objects after channel/group destroy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/cgrp.c -->
