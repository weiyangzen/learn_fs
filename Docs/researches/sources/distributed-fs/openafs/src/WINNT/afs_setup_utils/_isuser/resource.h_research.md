# sources/distributed-fs/openafs/src/WINNT/afs_setup_utils/_isuser/resource.h

Purpose: resource ID header for InstallShield custom dialogs used by OpenAFS setup.

Important APIs/types/functions: defines IDs for home/root path controls, drive lists, enable/install/web/file checkboxes, previous/browse file controls, dialog templates (`DLG_TEMPLATE`, `DLG_DRIVEPATH`, `DLG_CELLSERVDB`), and `IDC_STATIC`.

Control flow: no executable flow. Dialog procedures and resource scripts use these numeric constants to map Windows controls to setup behavior.

State/persistence: no state. User choices made through these controls are persisted elsewhere by setup code.

Dependencies/integration: used by `_IsUser.RC` and InstallShield/Visual Studio resource compilation.

Risks/test signals: there are intentional ID aliases such as `IDC_ENABLEROOT`/`IDC_INSTALL` and `IDC_CHECK_FILE`/`IDC_CHECK_BROWSEFILE`; dialog code must disambiguate by template context. Tests should verify resource compilation and correct control lookup for each dialog.
