<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/cfg_utils.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/cfg_utils.cpp

Purpose: Provides shared helpers for interpreting configuration-state flags, redrawing the wizard graphic, resolving the current application title resource, logging admin-library errors, and showing standard error/warning UI.

Important APIs/functions: `IsStepEnabled`, `EnableStep`, `ShouldConfig`, `DontConfig`, `ShouldUnconfig`, `ConfiguredOrConfiguring`, `Configured`, and `ToggleConfig` wrap raw `CONFIG_STATE` tests. `RedrawGraphic` invalidates the wizard left pane. `GetAppTitleID` chooses wizard vs config-manager title. `GetAdminLibErrorCodeMessage`, `LogError`, `ShowError`, and `ShowWarning` connect OpenAFS error translation, the global log, and UI messages.

Control flow: Page code uses the state predicates to decide availability and later the config page uses `Should*` to build steps. Error display logs the raw/translated status, shows an `ErrorDialog`, and updates `IDC_STATUS_MSG` when a dialog handle is supplied.

State and persistence: Mutates only the disabled bit passed by reference. Persists diagnostic information via `g_LogFile`.

Dependencies and integration points: Relies on `g_pWiz`, `g_CfgData`, `g_LogFile`, `util_AdminErrorCodeTranslate`, localized resource strings, and app-library `ErrorDialog`/`MessageBox` helpers.

Risks: Predicate functions use equality rather than masking disabled state, so a disabled step combined with `CS_CONFIGURE` will not be considered configurable by `ShouldConfig`. `ShowError` blindly writes `IDC_STATUS_MSG`, which may not exist on every caller dialog. `GetAdminLibErrorCodeMessage` returns an admin-library-owned string whose lifetime depends on the utility API.

Test signals: Unit-check every state combination with and without `CS_DISABLED`; verify warnings and errors on wizard/config-manager dialogs; test error translation success/failure and absent status controls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/cfg_utils.cpp -->
