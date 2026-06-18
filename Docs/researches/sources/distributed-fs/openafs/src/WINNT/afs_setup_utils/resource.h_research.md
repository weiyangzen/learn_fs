# sources/distributed-fs/openafs/src/WINNT/afs_setup_utils/resource.h

Purpose: central resource ID header for the OpenAFS setup utilities DLL.

Important APIs/types/functions: defines string IDs for install/uninstall failures, service errors, product names, preservation prompts, progress messages, dialogs (`IDD_PROGRESS`, `IDD_LICENSE`), controls (`IDC_LOGO`, `IDC_MSG`, `IDC_PRINT`, `IDC_TEXT`), and spinner icons (`IDI_SPIN1` through `IDI_SPINSTOP`).

Control flow: no executable flow. Resource IDs are consumed by `TaLocale`, message boxes, dialogs, and animation code.

State/persistence: no runtime state.

Dependencies/integration: used by setup resource scripts, `afs_setup_utils.cpp`, `progress_dlg.cpp`, and `animate_icon.cpp`.

Risks/test signals: ID stability matters for localized resource DLLs and dialog/control lookup. Tests should compile all localized `.rc` files and smoke-test resource loading for every ID used by code.
