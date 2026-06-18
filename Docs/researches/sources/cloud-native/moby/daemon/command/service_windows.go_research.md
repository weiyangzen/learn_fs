<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/service_windows.go -->
# sources/cloud-native/moby/daemon/command/service_windows.go

## Purpose
Implements Windows service registration, unregistration, SCM/debug service execution, event log forwarding, panic-file redirection, and service lifecycle signaling for dockerd.

## Important APIs, Types, And Functions
Service flag globals; `installServiceFlags`; `handler`; `etwHook.Levels` and `Fire`; `registerService`; `unregisterService`; `initService`; `handler.started`; `handler.stopped`; `handler.Execute`; `initPanicFile`; `removePanicFile`.

## Control Flow
`initService` handles mutually exclusive register/unregister actions, creates SCM/debug service handlers for `--run-service`, opens the event log when running as a service, starts `svc.Run` or `debug.Run`, and waits for handler readiness. `handler.Execute` reports pending/running/stopping status, reloads on `ParamChange`, stops on SCM stop/shutdown, and returns success or failure exit codes.

## State And Persistence Behavior
Registers/deletes Windows services and event logs, sets service recovery actions, redirects stderr and logger output to `<data-root>/panic.log`, rotates non-empty panic logs to `.old`, and removes an empty panic file after shutdown.

## Dependencies And Integration Points
Integrates Windows SCM packages, eventlog, daemon system checks, command lifecycle, and containerd/log hooks.

## Risks And Test Signals
Risks include global flag pointers, event-log open failures preventing service start, stderr handle restoration only for empty panic logs, and service readiness ordering. Signals come from Windows service registration/start/stop behavior and event log output.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/service_windows.go -->
