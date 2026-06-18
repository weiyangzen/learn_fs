# sources/distributed-fs/openafs/src/WINNT/client_exp/down_servers_dlg.cpp

Purpose: implements a simple dialog listing AFS servers reported as down.

Important APIs/functions: constructor, `DoDataExchange`, `OnInitDialog`, and `SetServerNames`.

Control flow: caller supplies a `CStringArray` of server names. Initialization populates the listbox with each name.

State/persistence: stores server names in `m_ServerNames` and listbox UI state only; no external writes.

Dependencies/integration: MFC dialog/listbox, localized dialog template, and callers that detect down servers.

Risks: no refresh after initialization if `SetServerNames` is called while visible. It displays raw strings with no status metadata or retry path.

Test signals: empty list, multiple servers, string copying semantics, and dialog localization.
