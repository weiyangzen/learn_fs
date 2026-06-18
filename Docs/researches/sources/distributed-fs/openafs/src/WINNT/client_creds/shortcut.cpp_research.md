# sources/distributed-fs/openafs/src/WINNT/client_creds/shortcut.cpp

Purpose: initializes COM shortcut support, creates `.lnk` files, and maintains the AFS Credentials Startup shortcut.

Important APIs/functions: `Shortcut_Init`, `Shortcut_Exit`, `Shortcut_Create`, and `Shortcut_FixStartup`.

Control flow: initialization calls apartment-threaded `CoInitializeEx`. Shortcut creation instantiates `CLSID_ShellLink`, sets target path, description, optional arguments, and saves through `IPersistFile`. Startup repair locates the common or user Startup folder from Explorer shell-folder registry keys or falls back to the Windows Start Menu path; it then creates or deletes `AFS Credentials.lnk`.

State/persistence: creates/deletes a Startup folder shortcut and reads optional `AfscredsShortcutParams` from HKCU then HKLM OpenAFS keys, defaulting to `-A -M -N -Q`.

Dependencies/integration: uses COM shell interfaces, `shlobj`, registry helpers/constants, current module path, and `afscreds.h` shortcut constants.

Risks: missing braces around `if (pszArgs) rc = psl->SetArguments(pszArgs); if (SUCCEEDED(rc))` make save occur regardless of `pszArgs` only because of indentation-sensitive intent. Shell folder registry paths are legacy. Deleting the shortcut reports failure if the file is already absent.

Test signals: COM initialization balance, shortcut creation with args, Unicode/non-Unicode save path, HKCU/HKLM parameter precedence, missing startup folder fallback, and autostart disable idempotency.
