# sources/cloud-native/containerd/cmd/containerd/command/main_windows.go

Purpose: provides Windows signal handling, ETW logging integration, and a Windows stack-dump trigger for the daemon.

Important APIs/functions: `handledSignals` handles `os.Interrupt`; `handleSignals()` mirrors Unix shutdown behavior; `setupDumpStacks()` creates a secured global Win32 event; `etwCallback()` dumps stacks on ETW capture-state requests; `init()` registers an ETW provider and logrus hook.

Control flow: `handleSignals()` starts a goroutine that records the server from `serverC`, handles interrupt by notifying stopping, canceling context, stopping the server, and closing `done`, then calls `setupDumpStacks()`. Stack dumps can be requested by signaling `Global\stackdump-<pid>` or by ETW provider capture.

State and persistence: stack dumps can be written to temp files. The Win32 event and ETW provider are intentionally process-lifetime resources.

Dependencies/integration: integrates `Microsoft/go-winio` ETW packages, Win32 security descriptors/events, logrus hooks, and containerd server shutdown.

Risks: event creation failures only log and do not fail startup. The stackdump goroutine waits forever for the process lifetime. ETW hook/provider are not explicitly closed.

Test signals: no local tests cover Windows signal, ETW, or event behavior.
