## sources/cloud-native/containers-storage/pkg/homedir/homedir_windows.go

Purpose: Windows home/config/runtime directory helpers.

Important APIs/types/functions: `Key`, `Get`, `GetConfigHome`, `GetShortcutString`, `StickRuntimeDirContents`, and `GetRuntimeDir`.

Control flow: uses `USERPROFILE` or `os.UserHomeDir`; config home is `<home>/.config`; sticky operation is a no-op; runtime dir is `<data home>/containers/storage`.

State and persistence: reads environment; does not create directories in this file.

Dependencies and integration points: portable homedir API for Windows storage paths.

Risks: `GetConfigHome` can return `.config` relative to empty home if lookup fails; runtime dir depends on `GetDataHome` and can fail if home lookup fails.

Test signals: shared homedir tests validate non-empty absolute `Get` and shortcut when run on Windows.
