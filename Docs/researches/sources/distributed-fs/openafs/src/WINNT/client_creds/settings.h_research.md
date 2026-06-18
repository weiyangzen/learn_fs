# sources/distributed-fs/openafs/src/WINNT/client_creds/settings.h

Purpose: declares registry settings helpers and versioning macros.

Important APIs/macros: root aliases `HKCR`, `HKCU`, `HKLM`; byte/version helpers `HIBYTE`, `LOBYTE`, `MAKEVERSION`; exported functions for erasing, restoring, storing, sizing, reading, writing binary registry values, and recursively deleting keys.

Control flow: no implementation. The header documents the version compatibility rules used by `RestoreSettings`.

State/persistence: all declared functions operate on registry state supplied by callers.

Dependencies/integration: uses Win32 `HKEY`, `LPCTSTR`, `PVOID`, `WORD`, and `BOOL`. `EXPORTED` can be overridden by consumers, suggesting reuse outside this executable.

Risks: macros redefine common names if not already present. Documentation says newer minor versions can be read by older programs when compatible, so structure fields must only be appended for minor version changes.

Test signals: compile with existing Windows macros, version macro values, and consumers preserving append-only minor-version semantics.
