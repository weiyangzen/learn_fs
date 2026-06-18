# sources/cloud-native/nydus/service/src/daemon.rs

Purpose: defines the common daemon lifecycle contract for Nydus services and the state-machine/controller infrastructure used by FUSE and singleton fscache daemons. Important APIs are `DaemonState`, `DaemonInfo`, the `NydusDaemon` trait, `DaemonStateMachineContext`, `DaemonStateMachineSubscriber`, and `DaemonController`.

Control flow: callers emit `DaemonStateMachineInput` through a concrete daemon's `on_event`; the dedicated `state_machine` thread consumes events and runs actions such as `start`, `stop` plus `wait_service`, `umount`, `restore`, and `StopStateMachine`. `trigger_stop` and `trigger_exit` intentionally send multiple events for running daemons so they move through `Running -> Ready -> Die` or `Running -> Ready -> Die` via exit.

State and persistence: daemon state is abstracted as `INIT`, `RUNNING`, `READY`, `STOPPED`, or `UNKNOWN`; concrete daemons own storage and upgrade persistence through `save`/`restore`. `DaemonController` stores the active daemon, optional blob cache manager, optional default filesystem service, singleton mode, and a `mio::Waker`/`Poll` pair for shutdown.

Dependencies and integration: integrates `rust_fsm`, `mio`, `nydus_api::BuildTimeInfo`, service `FsService`, `BlobCacheMgr`, and `UpgradeManager`. `export_info` serializes daemon metadata and optionally the backend collection for API status.

Risks: the FSM thread panics if channels are broken, invalid events are returned as `UnexpectedEvent`, `get_daemon` panics before registration, and `trigger_stop` behavior relies on concrete daemon state remaining synchronized with FSM state. Controller shutdown behavior differs in singleton mode, which can affect long-running service hosting.

Test signals: unit tests cover integer/string state conversion, exported JSON without fs info, trigger event sequences, controller lifecycle, daemon replacement, singleton mode writes, and waker allocation.
