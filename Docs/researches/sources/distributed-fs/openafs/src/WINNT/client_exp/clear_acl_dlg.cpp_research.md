# sources/distributed-fs/openafs/src/WINNT/client_exp/clear_acl_dlg.cpp

Purpose: implements a simple dialog for choosing whether to clear normal ACL entries, negative ACL entries, or both.

Important APIs/functions: constructor initializes localized template and booleans; `DoDataExchange` binds `IDC_NEGATIVE` and `IDC_NORMAL`; `GetSettings` returns selected flags.

Control flow: MFC dialog lifecycle handles checkbox state through DDX. Caller retrieves settings after modal completion.

State/persistence: only local booleans `m_bNormal` and `m_bNegative`; no direct ACL writes.

Dependencies/integration: used by ACL cleanup flows, depends on `TaLocale` through dialog resource lookup and MFC DDX.

Risks: no validation prevents OK with neither checkbox selected unless handled in the dialog resource or caller.

Test signals: checkbox default state, selected settings returned, cancel handling by caller, and localized dialog loading.
