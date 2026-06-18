# sources/distributed-fs/openafs/src/WINNT/client_exp/down_servers_dlg.h

Purpose: declares the down-servers display dialog.

Important APIs/types: `CDownServersDlg : public CDialog`, `SetServerNames(const CStringArray&)`, resource ID `IDD_DOWN_SERVERS`, and `CListBox m_ServerList`.

Control flow: callers populate names before modal display; initialization fills the listbox.

State/persistence: in-memory copy of server names only.

Dependencies/integration: uses MFC and resource IDs.

Risks: no include guard and no metadata beyond display strings.

Test signals: server list passed by callers appears in the dialog in order.
