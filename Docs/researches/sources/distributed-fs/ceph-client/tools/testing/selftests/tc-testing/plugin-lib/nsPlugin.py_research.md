# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/plugin-lib/nsPlugin.py

## Purpose
Implements the tc-testing namespace plugin. It creates a disposable network namespace and veth/dummy devices for tests requiring isolated networking, rewrites test commands to run inside that namespace, and cleans up namespaces after cases and suites.

## Important APIs, Types, And Functions
Class `SubPlugin(TdcPlugin)` implements `prepare_test()`, `pre_case()`, `post_case()`, `post_suite()`, `adjust_command()`, `_nl_ns_create()`, `_ipr2_ns_create_cmds()`, `_ipr2_ns_create()`, `_nl_ns_destroy()`, `_ipr2_ns_destroy_cmd()`, `_ipr2_ns_destroy()`, `_proc`, `_proc_check()`, `_exec_cmd()`, `_exec_cmd_batched()`, and `_replace_keywords()`. It optionally uses `pyroute2.netns` and `IPRoute`; otherwise it drives `ip -b -` through a persistent subprocess.

## Control Flow
Before a case, the plugin skips cases marked skipped or not requiring `nsPlugin`. For required cases it creates the namespace, veth peer, dummy device, and optional passed-through device, then waits until `/run/netns/$NS` is visible. During setup/execute/verify/teardown stages, `adjust_command()` prefixes commands with `$IP netns exec $NS`. After each case it removes the namespace, and after the suite it force-deletes any remaining namespaces with `ip -a netns del`.

## State And Persistence
State includes plugin args, substituted names from `tdc_config`, optional persistent `ip -b -` process cached in `_proc`, and kernel network namespace/device state. Namespace cleanup should remove veth and dummy devices automatically.

## Dependencies And Integration Points
Depends on root privileges, `iproute2`, optional `pyroute2`, veth/dummy kernel support, and tc-testing plugin lifecycle hooks. JSON tests request it through `plugins.requires`.

## Risks
The pyroute2 path and iproute2 fallback differ in implementation, so bugs may be backend-specific. `adjust_command()` uses naive `split()` for string commands, which can alter quoting. The cached batch `ip` subprocess can fail and poison later commands. Cleanup is broad (`ip -a netns del`) and must run in an isolated test environment.

## Test Signals
Signals include namespace visibility under `/run/netns`, `$DEV0/$DEV1/$DUMMY` links up, commands executing inside the namespace, no namespace leaks after suite cleanup, and tc action tests with `nsPlugin` passing.
