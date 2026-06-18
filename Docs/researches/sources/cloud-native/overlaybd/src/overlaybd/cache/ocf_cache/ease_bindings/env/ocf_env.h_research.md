<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/env/ocf_env.h -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/env/ocf_env.h

Purpose: Header compatibility layer that maps OCF environment requirements to userspace C/C++ and Photon-backed functions.

APIs and types: Defines Linux-like integer types, memory flags, debug/assert macros, container/list helpers, string/memory wrappers, secure memory stubs, allocator prototypes, mutex/rmutex/rwlock/rwsem/completion/atomic/spinlock APIs, bit ops, tick/time conversion, sort, sleep, crc32, and execution context APIs.

State and persistence: No persistent state; declarations back runtime state in `ocf_env.cpp`.

Dependencies and integration: Included by vendored OCF and ease bindings.

Risks and test signals: Many macros simplify kernel semantics, including interrupt context and secure memory. OCF unit and cache reload tests should exercise expected semantics.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/env/ocf_env.h -->
