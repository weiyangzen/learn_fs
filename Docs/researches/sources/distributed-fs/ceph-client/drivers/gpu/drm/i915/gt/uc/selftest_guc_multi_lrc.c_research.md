# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/selftest_guc_multi_lrc.c

Purpose: live GuC selftest for multi-LRC parallel context submission on engine classes with multiple sibling engines.

Important APIs/types/functions: `logical_sort()` orders sibling engines by logical mask. `multi_lrc_create_parent()` creates a parallel parent context with siblings of a class. `multi_lrc_context_unpin()` and `multi_lrc_context_put()` clean parent/child contexts. `multi_lrc_nop_request()` submits a parent request and child requests, marking the last child with `I915_FENCE_FLAG_SUBMIT_PARALLEL`. `intel_guc_multi_lrc_basic()` registers the class loop.

Control flow: the test iterates engine classes, skipping compute and render because breadcrumb handshake is unsupported there. For each class with at least two engines, it creates a parallel context, submits parent and child no-op requests, waits for the parent request, then waits for GT idle before releasing the context tree.

State and persistence: all state is transient: sibling arrays, parent/child context references, request references, and GT idle state. Cleanup explicitly unpins all children and the parent, then drops the parent creation reference.

Dependencies and risks: depends on GuC submission, parallel engine context creation, logical engine masks, request submission ordering, and selftest wait helpers. Risks include sibling ordering mistakes, leaked child context pins on request creation failures, class skip assumptions, and timeout sensitivity. Test signals are skipped operation on wedged/non-GuC systems, clean no-op completion on supported classes, and GT idle within five seconds.
