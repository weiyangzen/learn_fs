# sources/distributed-fs/openafs/src/WINNT/client_exp/PropBase.h

Purpose: declares the common base class for OpenAFS Explorer property pages.

Important types/APIs: `PropertyPage` stores `m_hwnd`, `m_hInst`, selected `filenames`, and booleans describing symlink, mountpoint, and directory state. It provides virtual `SetHwnd` and `PropPageProc`.

Control flow: property page subclasses override `PropPageProc` for message handling.

State/persistence: holds per-property-page runtime state only.

Dependencies/integration: includes resource IDs and relies on MFC/Win32 types. Used by `CPropFile`, `CPropACL`, and `CPropVolume`.

Risks: no constructor initialization for several public fields. Public mutable fields make lifecycle contracts implicit and easy to violate.

Test signals: object initialization by shell extension factory, flag propagation for mountpoint/symlink/directory pages, and callback dispatch.
