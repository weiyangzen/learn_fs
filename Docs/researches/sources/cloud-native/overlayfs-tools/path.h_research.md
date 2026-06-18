# sources/cloud-native/overlayfs-tools/path.h

Purpose: declares lightweight path helpers.

Important APIs/types/functions: `joinname(const char*, const char*)` and `basename2(const char*, const char*)`.

Control flow: callers use `joinname` for allocated path construction and `basename2` for relative path views.

State and persistence: no header state; ownership is implementation-defined.

Dependencies/integration: consumed by fsck scanner and redirect lookup logic.

Risks: no NULL-safety or ownership annotations in the header.

Test signals: compile and path unit tests.
