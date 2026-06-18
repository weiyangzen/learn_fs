# sources/cloud-native/cri-o/internal/config/seccomp/notifier.go

Purpose: implements Linux seccomp user-notification socket handling for containers whose sandbox annotations request syscall tracing/action.

Important APIs/types/functions: `Notifier` wraps the Unix listener, syscall count map, expiry timer, and stop-containers policy. Public methods include `StopContainers`, `Close`, `AddSyscall`, `UsedSyscalls`, and `OnExpired`. `Notification` carries context, container ID, and syscall. Internal functions include `injectNotifier`, `NewNotifier`, `handler`, `handleNewMessage`, `closeStateFds`, and `parseStateFds`.

Control flow: `injectNotifier` gates on non-empty container ID, annotations, and message channel, then requires the seccomp notifier action annotation. It rewrites kill/errno syscall actions to `ActNotify`, sets `ListenerPath`, and starts a notifier. `NewNotifier` listens on a Unix socket, accepts runtime connections, receives a passed seccomp fd from OCI state, then spawns `handler`. `handler` receives one seccomp notification, sends a CRI-O notification, validates the ID, responds with `ENOSYS`, and exits. `parseStateFds` finds the named seccomp fd and closes unrelated received fds.

State and persistence behavior: creates a Unix socket at `NotifierPath/containerID`, holds listener state, counts syscalls in a `sync.Map`, and uses a timer for expiry callbacks. It closes file descriptors explicitly.

Dependencies/integration points: uses libseccomp-golang, runtime-spec seccomp state, Unix socket control messages, CRI-O annotations, and CRI-O logging. It is called from seccomp profile setup after profile conversion to runtime-spec format.

Risks: fd-passing parsing is strict about message sizes and SCM count. The accept goroutine lives until listener close. `OnExpired` refresh semantics depend on `Timer.Stop` behavior. Only the first syscall per fd is handled. Socket path parent creation is not handled here.

Test signals: no direct tests in this subset for notifier fd passing, action rewriting, timers, or socket lifecycle.
