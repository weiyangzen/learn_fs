## sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/armada_plane.h

Purpose: declares Armada plane-private atomic state and the helper functions shared by primary and overlay plane code.

Important type is `struct armada_plane_state`, which embeds `drm_plane_state` and caches `src_hw`, `dst_yx`, `dst_hw`, `addrs[2][3]`, `pitches[3]`, and `interlace`. Accessor macros expose those cached values to register-programming code. Declared functions include plane calculation/check/reset/duplicate helpers and primary plane initialization.

Control flow is structural: atomic check fills this state once, then primary and overlay update paths consume it without recalculating addresses. State is transient atomic commit state, not persistent storage, but it represents values later persisted into display registers. Dependencies are DRM plane state types and Armada source files that provide implementations.

Risks include declarations for cleanup/destroy helpers that are not implemented in this file set, tight coupling between cache layout and update macros, and invalid cached values if callers bypass the shared atomic check. Test signals are build/link coverage, successful state duplication/reset, and correct primary/overlay updates after atomic commits.
