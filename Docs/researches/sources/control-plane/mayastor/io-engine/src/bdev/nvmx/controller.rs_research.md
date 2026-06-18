## sources/control-plane/mayastor/io-engine/src/bdev/nvmx/controller.rs

### Purpose
`nvmx/controller.rs` is the core Rust-native NVMe controller implementation. It owns controller lifecycle, namespace discovery, admin queue polling, channel traversal for reset/shutdown, asynchronous event handling, listener notifications, and controller option/transport builders.

### Important APIs, Types, And Functions
`NvmeControllerInner` wraps the SPDK controller, adminq poller, namespace list, and SPDK I/O device. `NvmeController` stores name, id, protection flags, optional inner state, `ControllerStateMachine`, event dispatcher, and timeout config. Important methods include `new()`, `populate_namespaces()`, `reset()`, `shutdown()`, `hot_remove()`, `get_io_stats()`, `register_device_listener()`, `destroy_device()`, and `connected_attached_cb()`. The `options` module builds controller opts; `transport` builds and formats transport IDs.

### Control Flow
After `uri.rs` completes async attach, `connected_attached_cb()` transitions to `Initializing`, installs the SPDK controller into timeout config, assigns a pointer-derived ID, constructs `NvmeControllerInner`, configures timeouts, populates namespace 1, registers AER callbacks, inserts an ID alias into `NVME_CONTROLLERS`, transitions to `Running`, and wakes the waiter. Reset is allowed only from `Running` or `Faulted`, sets `ResetActive`, traverses channels to drop qpairs, then traverses again to recreate qpairs unless shutdown was observed. Shutdown transitions to `Unconfiguring`, marks destroy in progress, traverses channels to shut them down, fails the SPDK controller, clears namespaces, transitions to `Unconfigured`, and invokes the callback. `destroy_device()` runs shutdown, removes both name and id map entries, notifies listeners, then waits until the last `Arc` reference can be unwrapped so Drop can detach the SPDK controller.

### State, Persistence, And Dependencies
Controller state is in-memory and synchronized through `parking_lot::Mutex` and the global `NVME_CONTROLLERS` `RwLock`. Admin queue and I/O resources are SPDK runtime objects. Dependencies include `IoDevice`, `PollerBuilder`, `NvmxSubsystem`, `TimeoutConfig`, `ControllerStateMachine`, `NvmeNamespace`, `DeviceEventDispatcher`, and SPDK NVMe APIs for AER, detach, namespace lookup, and controller fail.

### Integration Points
This controller backs `NvmeBlockDevice`, `NvmeDeviceHandle`, and `NvmfDeviceTemplate`. Admin queue failures dispatch `AdminCommandCompletionFailed`, `AdminQNoticeCtrlFailed`, or `AdminQBroken` to registered listeners, enabling nexus fault/retire behavior. Namespace attribute-change AERs trigger namespace repopulation and removal notification.

### Risks
Correctness depends on strict state-machine transitions and `ResetActive` flag ownership. Drop asserts that controllers are `New` or `Unconfigured`; leaked references can delay destroy indefinitely. Controller ID is the SPDK pointer value and is also used as a global map key. `destroy_device()` loops until `Arc::try_unwrap()` succeeds, so listener/channel references must be released. Some shutdown reset comments indicate behavior is still under design. `connected_attached_cb()` sends attach failure if namespace population fails but leaves cleanup to the caller.

### Test Signals
High-value tests include attach success/failure, namespace absent transitioning to `Faulted`, AER namespace removal, reset from legal and illegal states, concurrent reset rejection, reset racing shutdown, shutdown channel failure, `destroy_device()` removing both keys and notifying listeners, adminq error event dispatch, option builder fields, IPv4/IPv6 transport ID builder, and Drop assertions through controlled lifecycle tests.
