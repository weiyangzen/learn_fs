## sources/distributed-fs/openafs/src/WINNT/client_exp/results_dlg.h

Purpose: Declares `CResultsDlg`, the reusable results list dialog.

Important APIs/types: Constructor takes a help context ID; `SetContents` provides title, column title, file rows, and result rows. Dialog data binds label and list controls.

Control flow/state: Private arrays retain display content between construction and `OnInitDialog`.

Dependencies/integration: MFC and resource IDs; used by `gui2fs.cpp`.

Risks/tests: Header lacks include guards. Test constructor/help ID propagation and ownership independence from caller arrays.
