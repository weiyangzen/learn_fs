<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/supervisor/supervisor.go -->
## sources/cloud-native/nydus-snapshotter/pkg/supervisor/supervisor.go

Purpose: supervises nydusd runtime state handoff for failover/live upgrade. It receives serialized daemon state plus a Unix file descriptor from an old daemon and can later send those resources to a new daemon over a per-daemon Unix socket.

Important APIs/types: `StatesStorage`, in-memory `MemStatesStorage`, `Supervisor`, socket helpers `recv`/`send`, `FetchDaemonStates`, `SendStatesTimeout`, `Sock`, `SupervisorsSet`, `NewSupervisorSet`, `NewSupervisor`, `GetSupervisor`, and `DestroySupervisor`. `Supervisor` stores ID, socket path, last FD, data storage, mutex, and a single-flight semaphore.

Control flow and state: `FetchDaemonStates` acquires a semaphore, listens on the supervisor socket, runs a caller trigger, accepts the daemon connection, reads data/oob control messages, parses Unix rights, and saves the data/FD atomically. `SendStatesTimeout` listens on the same socket and asynchronously sends the stored state and FD to a connecting daemon. Timeout modes close the listener to unblock `Accept`. `DestroySupervisor` removes the supervisor from the set and closes any held FD.

Dependencies/integration: uses Unix domain sockets, `unix.ParseSocketControlMessage`, `syscall.UnixRights`, errgroup, semaphore, and project error definitions. It is integrated through daemon manager upgrade/recovery paths and the system controller hot-upgrade flow.

Risks and test signals: FD lifecycle is delicate; `save` overwrites state and keeps only positive FDs, and `load` does not consume resources. `recv` requires at least one control message, so state-only transfers fail. Tests cover large multi-read state payloads, FD transfer, sendback, and timeout behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/supervisor/supervisor.go -->
