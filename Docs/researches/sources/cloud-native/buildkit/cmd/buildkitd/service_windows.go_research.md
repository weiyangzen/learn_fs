# Research: sources/cloud-native/buildkit/cmd/buildkitd/service_windows.go

Purpose: implements Windows Service Control Manager integration for buildkitd, including service registration/unregistration, service-mode logging/stderr redirection, panic file handling, and graceful gRPC server control.

Important APIs and flow: `serviceFlags` exposes service name, register/unregister, hidden run-service, and log-file flags. `registerService` creates an automatic service with restart failure actions and reuses current args minus registration flags. `unregisterService` deletes the service. `applyPlatformFlags` stores global flag values. `registerUnregisterService` handles early register/unregister, service-mode detection, log directory creation, panic file setup, stderr redirection, and logrus output. `launchService` starts service handling when `--run-service` is set. `handler.Execute` responds to SCM stop/shutdown by stopping the gRPC server. `initPanicFile` and `removePanicFile` manage a marker for unexpected crashes.

State and persistence: mutates Windows SCM service definitions, writes log and panic files under daemon root or requested log path, redirects process stderr, and controls server lifecycle.

Risks and test signals: service registration requires privileges and unsafe Windows API calls for failure actions/stderr handles. Panic marker correctness affects diagnostics. No direct tests are present in this subset.
