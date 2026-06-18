# sources/cloud-native/containerd/cmd/containerd/command/service_windows.go

Purpose: implements Windows Service Control Manager integration, log redirection, panic log handling, and service lifecycle shutdown for `containerd`.

Important APIs/functions: `serviceFlags()` adds service-name/register/unregister/run-service/log-file flags; `applyPlatformFlags()` captures flag values in package globals; `registerService()` and `unregisterService()` manage SCM entries; `registerUnregisterService()` handles early register/unregister/run-service setup; `launchService()` starts the SCM/debug service runner; `handler.Execute()` handles stop/shutdown; `initPanicFile()` redirects `STD_ERROR_HANDLE`; `removePanicFile()` removes empty panic logs.

Control flow: daemon startup applies flags and calls `registerUnregisterService(root)`. Register/unregister modes perform SCM operations and stop startup. Run-service mode allocates a console, initializes `root/panic.log`, redirects stderr/logrus/stdlog to either `--log-file` or NUL, then later `launchService()` starts the SCM handler and waits for it to report running. On SCM stop/shutdown, the handler stops the server, removes an empty panic file, closes `done`, and exits.

State and persistence: uses package-level service flags, panic file handle, and old stderr handle. Creates or rotates `panic.log` under the containerd root. Optional `--log-file` receives logrus/stdlog/stderr output.

Dependencies/integration: depends on `golang.org/x/sys/windows/svc`, `svc/mgr`, `svc/debug`, Win32 console/std-handle APIs, logrus, stdlib log, and containerd server stop semantics.

Risks: package globals mean tests or multiple app instances in one process would share service state. Panic file rotation ignores `os.Rename` errors. Running as service with no log file intentionally discards normal logs, leaving only panic diagnostics. SCM recovery actions are fixed to two restarts.

Test signals: no local tests cover Windows SCM behavior, log redirection, panic file rotation, or service stop.
