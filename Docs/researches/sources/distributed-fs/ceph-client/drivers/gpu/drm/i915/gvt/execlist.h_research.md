# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/execlist.h

## Purpose
`execlist.h` declares the packed register/descriptor views and per-engine state structures used by GVT execlist emulation. It provides bitfield mappings for context descriptors, execlist status registers, context status pointers, and CSB entries.

## Important Types
`struct execlist_ctx_descriptor_format` overlays the low descriptor dword with valid, restore, addressing, coherency, fault, privilege, and LRCA fields, and treats the upper dword as `context_id`. `struct execlist_status_format` maps active/valid bits, queue-full state, write/current pointers, and current context id. `struct execlist_context_status_pointer_format` maps CSB read/write pointers and mask bits. `struct execlist_context_status_format` maps idle-to-active, preempted, element-switch, active-to-idle, context-complete, wait reasons, and lite-restore status. `struct execlist_ring_context` models the first 52 dwords of logical ring context image with MMIO address/value pairs. `struct intel_vgpu_execlist` stores two slots plus running/pending pointers and cached ELSP dwords.

## Control Flow And State
The header has no executable control flow beyond declarations, but it defines the state that `execlist.c` mutates during submit, schedule-in, schedule-out, reset, and cleanup. Two descriptors form one ELSP submission bundle; two virtual slots represent running and pending hardware execlists.

## Dependencies And Integration Points
It includes Linux types and forward references `struct intel_vgpu`/`struct intel_engine_cs` indirectly through users. The public API `intel_vgpu_submit_execlist()` is called by submission/MMIO code after ELSP writes are collected.

## Risks And Test Signals
Bitfield layout must match the guest-visible hardware ABI. Any compiler/layout or hardware-generation mismatch would corrupt descriptor interpretation and status reporting. Tests should cover descriptor decoding, CSB bit layout, and ABI compatibility with the i915 guest driver used by the supported platform generation.
