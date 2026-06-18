<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/env/ocf_env_list.h -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/env/ocf_env_list.h

Purpose: Linux-kernel-style intrusive list helpers for OCF userspace environment.

APIs and control flow: Defines `list_head`, poison values, init, add, add_tail, empty, delete, move, entry, first_entry, and several iteration macros including safe variants.

State and persistence: List membership is embedded in caller-owned structs; no allocation.

Dependencies and integration: Used by OCF C code expecting kernel list APIs.

Risks and test signals: Iteration macros rely on nonstandard `typeof` and pointer arithmetic; C/C++ compiler compatibility matters. OCF build and list-heavy OCF tests validate behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/env/ocf_env_list.h -->
