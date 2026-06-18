# sources/cloud-native/overlayfs-tools/common.h

Purpose: shared declarations and macros for overlayfs-tools diagnostics, gettext integration, min/max helpers, and allocation wrappers.

Important APIs/types/functions: `_()` gettext macro, GNU-style `min`/`max`, printf-checked declarations for `print_err`, `print_info`, `print_debug`, memory helpers, and `version`.

Control flow: compile-time feature selection only; `USE_GETTEXT` toggles translation.

State and persistence: no state.

Dependencies/integration: included by most C files and provides a consistent utility layer across `overlay` and `fsck.overlay`.

Risks: `min`/`max` use GNU statement expressions and `typeof`, matching `gnu11` build mode but not strict ISO C. The fallback `__attribute__` guard may hide compiler checking on non-GNU compilers.

Test signals: build with Meson `c_std=gnu11` verifies macro compatibility.
