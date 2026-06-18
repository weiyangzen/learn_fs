<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/bdev_cli.rs -->
## sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/bdev_cli.rs

### Purpose
This file implements v1 bdev CLI operations. It mirrors the v0 bdev command set but uses v1 service-specific RPCs and includes capacity in default list output.

### Important APIs, Types, And Functions
`BdevArgs` and `BdevCommands` define list, create, share, destroy, and unshare. `BdevShareProtocol` supports `Nvmf`. `CreateArgs`, `ShareArgs`, `DestroyArgs`, and `UnshareArgs` define command inputs. The implementation uses `ctx.v1.bdev`.

### Control Flow
`list` sends `ListBdevOptions { name: None }`, computes capacity as `num_blocks * blk_size`, and prints bdev metadata. `create` sends `CreateBdevRequest` and unwraps the optional returned bdev to print its name. `destroy` lists all bdevs, finds by name, unshares by name, then destroys by URI. `share` maps to `common::ShareProtocol::Nvmf` and propagates allowed hosts. `unshare` sends the name.

### State, Persistence, And Dependencies
All state changes occur in the remote v1 bdev service. Dependencies include v1 protobufs, `byte_unit`, `url`, colored JSON, SNAFU, and the shared context. It integrates with NVMf target management and lower-level bdev creation modules.

### Risks And Test Signals
Returned optional bdev fields are unwrapped in create/share. Capacity multiplication can overflow in theory. Destroy has the same list-then-unshare-then-destroy race as v0. Tests should cover optional response fields, allowed-host propagation, list filtering future compatibility, destroy not found, and default/JSON output.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/bdev_cli.rs -->
