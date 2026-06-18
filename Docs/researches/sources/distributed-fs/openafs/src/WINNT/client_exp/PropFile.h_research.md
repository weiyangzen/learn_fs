# sources/distributed-fs/openafs/src/WINNT/client_exp/PropFile.h

Purpose: declares the file property page class for the Explorer extension.

Important APIs/types: `CPropFile` derives from `PropertyPage`, overrides `PropPageProc`, and provides helpers for enabling, displaying, and constructing Unix permission strings. It stores `m_cellName` and `m_volName`.

Control flow: implementation handles property sheet initialization, command handling, and apply notifications.

State/persistence: class members cache cell/volume context; UI state stores pending mode changes until apply.

Dependencies/integration: depends on `PropBase.h`, resource IDs, and MFC `CString`.

Risks: `m_volName` is not initialized in this header or its constructor, so creators or future code must set it before mountpoint editing depends on it.

Test signals: construction with filename arrays, flag-driven UI, and mode string round-trips.
