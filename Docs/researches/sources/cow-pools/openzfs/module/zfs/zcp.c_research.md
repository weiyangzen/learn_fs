# File Research: sources/cow-pools/openzfs/module/zfs/zcp.c

## Summary
Implements the ZFS Channel Program runtime: a bounded Lua 5.2 environment that executes scripts either in syncing context or open context, converts between Lua values and nvlists, exposes ZFS modules, and enforces argument, memory, and instruction limits.

## Main Responsibilities
- Creates and configures the Lua interpreter for channel programs.
- Converts input nvlists to Lua tables and Lua return values back to nvlists.
- Installs ZFS Lua libraries under `zfs.list`, `zfs.check`, `zfs.sync`, and `zfs.get_prop`.
- Tracks current run state in the Lua registry.
- Enforces instruction and memory limits.
- Handles cleanup callbacks when Lua longjmps through C code.
- Parses callback arguments uniformly for positional and table/keyword calling forms.

## Key APIs
- `zcp_eval()`
- `zcp_run_info()`
- `zcp_parse_args()`
- `zcp_argerror()`
- `zcp_nvlist_to_lua()`
- `zcp_dataset_hold()`
- `zcp_register_cleanup()`, `zcp_deregister_cleanup()`, `zcp_cleanup()`

## Important Behavior
`zcp_eval()` builds a Lua state with a custom allocator, loads limited core Lua libraries, exposes ZFS-specific modules, compiles the user program, converts the input nvpair, and runs either through `dsl_sync_task_sig()` or an open-context dry-run transaction.

Lua-to-nvlist conversion supports nil, boolean, number, string, and nested tables up to depth 20. It detects string/number/bool key collisions such as `"1"` versus `1`.

The instruction hook checks cancellation and timeout every `zfs_lua_check_instrlimit_interval` instructions. Memory allocation switches from must-succeed setup mode to limit-enforced execution mode before calling user code.

## State and Lifetime
`zcp_run_info_t` owns the Lua state’s execution context, transaction pointer, credential reference, cleanup-handler list, output nvlist, space accounting, timeout/cancel flags, and pending zvol minor list.

## Risks
Fatal Lua errors and limit violations do not roll back work already performed in the same channel program. C callbacks that allocate temporary kernel objects must register cleanup handlers before any path that can longjmp. Numeric Lua values are converted through Lua number/integer APIs, so value-range expectations must match nvlist consumers.
