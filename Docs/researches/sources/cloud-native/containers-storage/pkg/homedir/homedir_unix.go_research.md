## sources/cloud-native/containers-storage/pkg/homedir/homedir_unix.go

Purpose: Unix home, config, runtime directory, and sticky runtime-file helpers.

Important APIs/types/functions: `Key`, `Get`, `GetShortcutString`, `StickRuntimeDirContents`, `stick`, `isWriteableOnlyByOwner`, `GetConfigHome`, and `GetRuntimeDir`.

Control flow: `Get` delegates to `unshare.HomeDir`. `GetConfigHome` is cached with `sync.Once`, uses `XDG_CONFIG_HOME` or resolves `$HOME/.config`, creates it, and verifies ownership. `GetRuntimeDir` uses `XDG_RUNTIME_DIR`, `/run/user/<uid>`, or a temp fallback, requiring owner-only write permissions. `StickRuntimeDirContents` absolute-normalizes paths under runtime dir and chmods sticky bit.

State and persistence: reads env, creates config/runtime directories, chmods files, and caches config/runtime results process-wide.

Dependencies and integration points: rootless storage path selection and runtime file retention. Depends on `unshare`, filesystem ownership from `syscall.Stat_t`, and logrus.

Risks: `sync.Once` caches env-derived paths and errors, so tests or callers changing env after first call will not affect results. Runtime dir prefix check is string-based after `Abs`, not `EvalSymlinks` for each file. Directory creation can fail in restricted environments.

Test signals: selected tests only smoke `Get` and shortcut; no coverage for config/runtime/sticky behavior.
