# sources/distributed-fs/openafs/src/WINNT/client_creds/afswiz.cpp

Purpose: implements the startup wizard shown when the AFS client service is configured but not running. It guides service start, optional credential acquisition, optional drive mapping, and completion.

Important APIs/functions: `ShowStartupWizard`; state dialog procedures `WizStart_DlgProc`, `WizStarting_DlgProc`, `WizCreds_DlgProc`, `WizMount_DlgProc`, `WizMounting_DlgProc`, `WizFinish_DlgProc`; helpers for enabling credential/map forms, service polling, and threaded mapping activation.

Control flow: `ShowStartupWizard` creates a `WIZARD`, sets state descriptors, shows it modally, refreshes tabs, and frees drive map state. The wizard starts the service, polls until running, optionally calls `ObtainNewCredentials`, optionally writes a drive mapping, and launches a background thread that activates inactive mappings before finishing.

State/persistence: file-static `l` holds a `DRIVEMAPLIST`, current wizard dialog, help ID, and requested submount. Persistent effects include service start, token creation, drive mapping writes, and submount creation through drive-map helpers.

Dependencies/integration: depends on OpenAFS `fs_utils` mount-root constants, `drivemap` APIs, `creds` token APIs, Windows SCM, and the application wizard framework (`al_wizard`).

Risks: background mapping thread shares file-static state without explicit locking. Service start failure leaves UI in failure state but may not expose detailed errors. The wizard auto-skips mapping choice when any mapping already exists.

Test signals: service stopped/start-pending/running transitions, credential success/failure, drive-letter selection, invalid submount validation, mapping activation failures, and repeated attempts while `g.pWizard` is already set.
