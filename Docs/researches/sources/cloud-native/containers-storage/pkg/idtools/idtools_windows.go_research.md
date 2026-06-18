## sources/cloud-native/containers-storage/pkg/idtools/idtools_windows.go

Purpose: Windows implementations for ownership-related helpers where UID/GID semantics are unsupported.

Important APIs/types/functions: `mkdirAs` and `CanAccess`.

Control flow: `mkdirAs` ignores ownership arguments and calls `os.MkdirAll`; `CanAccess` always returns true.

State and persistence: may create directories; no ownership changes.

Dependencies and integration points: enables public idtools APIs to compile on Windows.

Risks: behavior is intentionally semantic mismatch with Unix; callers relying on ownership/access enforcement must gate platform behavior.

Test signals: no selected Windows-specific tests.
