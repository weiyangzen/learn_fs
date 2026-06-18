# sources/distributed-fs/openafs/src/WINNT/client_creds/resource.h

Purpose: defines string, icon, dialog, bitmap, menu, command, and control resource identifiers for `afscreds.exe`.

Important identifiers: service/status strings (`IDS_SERVICE_*`), error text (`IDS_ERROR_*`), mapping and wizard strings, tray menu commands (`M_TERMINATE`, `M_ACTIVATE`, `M_REMIND`, `M_TERMINATE_NOW`), dialogs (`IDD_MAIN`, tab dialogs, wizard pages, mapping/auth dialogs), icons (`IDI_CREDS_*`), and controls (`IDC_*`).

Control flow: no executable code; IDs drive message dispatch and resource lookup across almost every credentials module.

State/persistence: none.

Dependencies/integration: must match `.rc` files and localized resources. IDs are consumed by `TaLocale`, dialog templates, menu resources, and Windows message handlers.

Risks: duplicate values exist intentionally for different resource classes but can confuse maintenance. Renumbering without updating resources breaks UI dispatch. Some controls share IDs across dialogs, requiring context-aware handlers.

Test signals: resource compilation, all dialogs load, menu commands dispatch correctly, and localized strings/icons resolve for startup/service/token/mapping scenarios.
