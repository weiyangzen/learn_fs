# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_workarounds.h

Purpose: declares the public i915 workaround lifecycle API and provides the inline cleanup helper for workaround lists.

Important APIs/functions: `intel_wa_list_free()` releases a list allocation with `kfree()` and zeroes the whole `i915_wa_list`. The header declares context APIs `intel_engine_init_ctx_wa()` and `intel_engine_emit_ctx_wa()`, GT APIs `intel_gt_init_workarounds()`, `intel_gt_apply_workarounds()`, `intel_gt_verify_workarounds()`, whitelist APIs `intel_engine_init_whitelist()` and `intel_engine_apply_whitelist()`, and engine APIs `intel_engine_init_workarounds()`, `intel_engine_apply_workarounds()`, `intel_engine_verify_workarounds()`.

Control flow: this header does not implement runtime control flow beyond freeing list storage. It forms the call boundary used by GT and engine initialization code, reset/resume paths, request emission for context state, and verification/selftest code.

State and persistence behavior: the only state mutation in the header is destructive cleanup of `wal->list` and reset of metadata fields. The declared functions initialize and apply state held in `struct intel_gt` and `struct intel_engine_cs`, but those structures are defined elsewhere.

Dependencies and integration points: includes `<linux/slab.h>` for memory free helpers and `intel_workarounds_types.h` for `struct i915_wa_list`. It forward-declares i915 request, engine, GT, and device-private structures to avoid pulling implementation headers into users.

Risks: callers must not use a workaround list after `intel_wa_list_free()` without reinitializing it, because the helper zeroes both metadata and pointer fields. The API split makes it easy to confuse context, GT, whitelist, and engine workaround domains; call sites should use the matching init/apply/verify hook.

Test signals: compile coverage confirms function prototypes match `intel_workarounds.c`. Runtime signal is indirect through selftests and reset/resume paths that call these APIs.
