# subset-b-009973 Research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/nbt/winsreplication.c -->
# sources/user-network-fs/samba/source4/torture/nbt/winsreplication.c

## Purpose

This file defines the Samba torture suite for NetBIOS WINS replication behavior. It exercises the WREPL client/server protocol paths for association context handling, pull replication table/name enumeration, replica conflict resolution, and conflicts between replicated records and locally owned WINS records. The suite is integration-heavy: most tests connect to a configured WINS server, inject WREPL replication updates, register and release NBT names, and then pull replicated state back to verify the server's database decisions.

## Important APIs, Types, and Functions

- `torture_nbt_winsreplication()` builds the suite named `winsreplication` and registers `assoc_ctx1`, `assoc_ctx2`, `wins_replication`, `replica`, and `owned`. `assoc_ctx1` is flagged dangerous, and `owned` skips in quick mode.
- `test_assoc_ctx1()` and `test_assoc_ctx2()` validate WREPL association context semantics through `wrepl_socket_init()`, `wrepl_connect()`, `wrepl_associate()`, `wrepl_request()`, `wrepl_request_send()/recv()`, and `wrepl_associate_stop()`.
- `test_wins_replication()` performs a pull cycle using `wrepl_pull_table()` followed by `wrepl_pull_names()` for each partner and logs records through `display_entry()`.
- `struct test_wrepl_conflict_conn` is the shared fixture for conflict tests. It stores the target server address, a long-lived pull socket and association, synthetic owner records `a`, `b`, `c`, `x`, local NBT sockets, bound socket addresses, and address lists for best/all/multihomed test variants.
- `test_create_conflict_ctx()` creates that fixture: it connects and associates with WREPL, discovers existing owner version ranges via `wrepl_pull_table()`, opens client and optional server NBT sockets, binds to local interfaces and port 137 when possible, and prepares address lists used by the test matrices.
- `test_wrepl_update_one()` sends a two-phase WREPL update: first `WREPL_REPL_UPDATE`, expecting `WREPL_REPL_SEND_REQUEST`, then `WREPL_REPL_SEND_REPLY` carrying one `wrepl_wins_name`, expecting `WREPL_STOP_ASSOCIATION`.
- `test_wrepl_is_applied()`, `test_wrepl_mhomed_merged()`, and `test_wrepl_sgroup_merged()` are the main state verification helpers. They pull names for an owner and assert expected presence, flags, version IDs, scopes, and address ownership/merge results.
- `test_conflict_same_owner()` covers same-owner replacement behavior across name scopes, name type, state, static bit, and address changes.
- `test_conflict_different_owner()` is a large table-driven matrix for owner A/B/X replica conflicts. It tests unique, normal group, special group, and multihomed records in active/released/tombstone states, including special-group merge and cleanup behavior.
- `test_conflict_owned_released_vs_replica()` creates a locally owned name, releases it, then checks whether incoming replica records should replace that released local record.
- `test_conflict_owned_active_vs_replica()` creates active local names and then applies replica records. It can emulate owner-defense NBT query/release responses via `test_conflict_owned_active_vs_replica_handler*()` callbacks.
- `_NBT_NAME`, `WREPL_NAME_FLAGS()`, `CHECK_STATUS`, `CHECK_VALUE`, `CHECK_VALUE_UINT64`, and `CHECK_VALUE_STRING` compact the many test rows and assertions.

## Control Flow

The suite starts with simple protocol sanity tests. `test_assoc_ctx1()` opens two WREPL connections to the same server and checks that an association context created on one connection is not accepted as a valid context on the other in the way a caller might incorrectly expect. It sends a send-only table query using the first connection's context over the second connection, verifies the request path still returns cleanly, then sends additional association/table requests to ensure each connection remains usable. It also validates stop-association behavior, including an end-of-file result for one stop reason.

`test_assoc_ctx2()` is narrower: it repeatedly sends start-association requests on one connection and asserts that the returned `assoc_ctx` is stable for the connection.

`test_wins_replication()` performs the read-only replication pull flow. It connects, associates, pulls the owner table, handles `NT_STATUS_NETWORK_ACCESS_DENIED` as an explicit "not a valid pull partner" failure, then pulls and displays names for each partner. This gives a broad signal that the server can expose replication metadata and records over WREPL.

The replica-conflict lane starts in `torture_nbt_winsreplication_replica()`, creates a fixture, then runs same-owner and different-owner conflict matrices. Each matrix row constructs one or two `wrepl_wins_name` records with increasing owner version IDs, sends them through `test_wrepl_update_one()`, and validates final state by pulling the affected owner. The same-owner path expects the newest same-owner non-released record to replace older state, with released rows not retained. The different-owner path alternates owner records, checks table invariants before running non-extra rows, supports explicit cleanup rows, and uses merge-specific helpers for special-group merges.

The owned-conflict lane starts in `torture_nbt_winsreplication_owned()`. Released-owned tests register a local NBT name through `nbt_name_register()`, release it through `nbt_name_release()`, then feed a replica update and verify whether the replica survived. Active-owned tests register one or more local addresses, install incoming NBT handlers on sockets bound to port 137 when available, apply the replica, optionally wait for server owner-defense queries or release demands, and then verify replacement, rejection, multihomed merge, or special-group merge. This path models real WINS defense behavior rather than only database-to-database replication.

The NBT handler dispatches incoming packets by opcode. Query handling validates the requested name and sends either a positive `NBT_QTYPE_NETBIOS` answer with configured address records or a negative name-error answer. Release handling validates that a release was expected and echoes a release reply. Both flush the socket send queue and update the row's timeout/ret state to unblock the waiting test loop.

## State and Persistence Behavior

The file does not persist state itself, but it deliberately mutates the target WINS server database. State is represented as WINS owner version counters, records identified by owner/name/type/scope, and address lists. The conflict fixture seeds owner max/min version values from the server's current pull table, then increments `ctx->a.max_version`, `ctx->b.max_version`, or `ctx->x.max_version` before emitting synthetic replicated records. This keeps injected records monotonic relative to existing server state.

The tests use reserved loopback-like owner addresses (`127.65.65.1`, `127.66.66.1`, `127.88.88.1`) and many synthetic names such as `_SAME_OWNER_A`, `_DIFF_OWNER`, and matrix-specific abbreviations. Cleanup rows intentionally leave tombstoned unique records or clear special-group records so repeated smbtorture runs do not inherit active conflicts. Some cleanup is conditional on previous merge behavior.

Memory lifetime is managed through `talloc` under the torture context or conflict context. Network operations rely on Samba's `tevent` loop. Active-owned tests temporarily install incoming handlers in `nbt_name_socket` private data to respond to server defense traffic.

## Dependencies and Integration Points

The file integrates multiple Samba subsystems: WREPL client protocol (`libcli/wrepl/winsrepl.h`), event handling (`tevent`), socket binding/listening (`lib/socket/socket.h`), network interface discovery (`lib/socket/netif.h`), NBT packet/name APIs (`librpc/gen_ndr/ndr_nbt.h`, `libcli/nbt/libnbt.h`), torture framework assertions and suite registration, and loadparm configuration for NBT port and server settings.

It depends on `torture_nbt_get_name()` to supply a target server name/address and on `wrepl_best_ip()` / `iface_list_best_ip()` to choose local and remote addresses. Some tests require the process to bind to the configured NBT port, usually port 137; if that bind fails the active-owned conflict test is skipped rather than failed. The suite is intended for Samba's smbtorture/NBT test environment and is sensitive to socketwrapper/root privileges, interface layout, and whether the target WINS server allows the client as a replication partner.

## Risks and Edge Cases

- The tests are destructive against the target WINS database. They inject replica records, register and release names, and depend on cleanup rows to leave stable tombstoned state.
- Version IDs are derived from live server owner metadata; stale or unexpected preexisting records for synthetic owners can alter behavior.
- The different-owner and owned-active matrices are extremely table-driven. A wrong boolean in a row (`apply_expected`, `sgroup_merge`, `mhomed_merge`, `cleanup`, `skip`) changes the behavioral contract without changing procedural code.
- Active-owned tests depend on timing. They use fixed timeouts, manual `tevent_loop_once()` loops, socket send-queue drains, and `smb_msleep(1000)`, which can be brittle on slow or unusual test hosts.
- Binding to port 137 may fail outside privileged or socketwrapper environments; the code treats this as non-fatal for setup and skips active-owned tests if no server NBT socket is available.
- Address-list indexing assumes usable IPv4 interfaces. Optional second-interface tests are skipped via `skip` when there are not enough addresses, but some setup paths still require at least one IPv4 address.
- `test_wrepl_is_applied()` truncates expected scope to 237 bytes when the server returns a scoped name, explicitly testing long-scope behavior but also encoding a protocol limit assumption.
- The comments contain known TODO/FIXME-style uncertainty around late release demands for some multihomed/unique positive-response cases; these are intentional observations and not fully resolved by the test.

## Test Signals

The primary signal is smbtorture pass/fail for the `NBT-WINSREPLICATION` suite and its subtests. Assertions check NTSTATUS values, NBT return codes, WREPL message types/commands, owner/name/type/scope equality, raw WREPL flags, version IDs, address counts, address ownership, and expected merge composition. Diagnostic `torture_comment()` output prints row descriptions such as `REPLACE`, `NOT REPLACE`, `SGROUP_MERGE`, and `MHOMED_MERGE`, making matrix failures traceable to source row `__location__` values.

Good coverage indicators are successful association-context tests, a complete pull table/name pass, same-owner replacement coverage across normal and maximum-length scopes, different-owner matrix coverage for all type/state pairs, released-owned replacement checks, and active-owned defense checks in an environment where port 137 binding and multiple IPv4 addresses are available.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/nbt/winsreplication.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/ndr/atsvc.c -->
# sources/user-network-fs/samba/source4/torture/ndr/atsvc.c

## Purpose

This file defines a compact Samba NDR torture suite for ATSVC RPC marshalling. It verifies that generated NDR pull code for selected AT Scheduler service operations decodes known wire byte streams into the expected generated C structures. The coverage is fixture-oriented rather than live RPC-oriented: each test feeds static byte arrays into the NDR torture helpers and asserts decoded fields.

## Important APIs, Types, and Functions

- `ndr_atsvc_suite()` creates the `atsvc` NDR torture suite and registers pull tests with `torture_suite_add_ndr_pull_fn_test()`.
- Generated RPC/NDR types under test are `struct atsvc_JobEnum`, `struct atsvc_JobAdd`, `struct atsvc_JobDel`, and `struct atsvc_JobGetInfo` from `librpc/gen_ndr/ndr_atsvc.h`.
- Static fixture arrays encode in/out stubs: `jobenum_in_data`, `jobenum_out_data`, `jobadd_in_data`, `jobadd_out_data`, `jobdel_in_data`, `jobdel_out_data`, `jobgetinfo_in_data`, and `jobgetinfo_out_data`.
- Check callbacks `jobenum_in_check()`, `jobenum_out_check()`, `jobadd_in_check()`, `jobadd_out_check()`, `jobdel_in_check()`, `jobdel_out_check()`, `jobgetinfo_in_check()`, and `jobgetinfo_out_check()` validate the decoded structures with torture assertions.

## Control Flow

Suite construction is linear. `ndr_atsvc_suite()` allocates a suite named `atsvc` and adds eight NDR pull tests. Each registration specifies the operation type, fixture byte array, NDR direction (`NDR_IN` or `NDR_OUT`), and a callback that validates decoded output.

The JobEnum input fixture decodes a server name pointer/string for `WIN2KDC1`, an empty job enumeration container, preferred max length of `-1`, and a resume handle of zero. The JobEnum output fixture decodes seven entries, checks the first job's ID, time, day flags, command string `foo.exe`, total entry count, resume handle, and NT success result.

The JobAdd input fixture checks a server name and job information including time `84600000`, day-of-week bit `0x2`, flags `17`, and command `foo.exe`; its output fixture checks returned job ID `14` and success. JobDel input checks deletion range `14..14`; its output fixture intentionally does not assert the return value beyond a FIXME noting an unknown `0x00000ede` status. JobGetInfo input checks server name and job ID `1`; output checks a non-null job info pointer and the expected time, calendar flags, flags `0x13`, and command.

## State and Persistence Behavior

There is no persistent state and no live scheduler interaction. All state is local, static test data plus decoded temporary structures allocated by the NDR torture framework. The tests are deterministic so long as the generated ATSVC NDR definitions and scalar/string decoding semantics remain compatible with the fixture data.

## Dependencies and Integration Points

The file depends on Samba's NDR torture harness (`torture/ndr/ndr.h`), generated ATSVC NDR declarations (`librpc/gen_ndr/ndr_atsvc.h`), and suite prototype integration (`torture/ndr/proto.h`). It integrates into the broader NDR test registry through the exported `ndr_atsvc_suite()` function. The generated pull functions are selected by the `torture_suite_add_ndr_pull_fn_test()` macro/function based on the operation type name supplied in each registration.

## Risks and Edge Cases

- The byte arrays encode exact historical wire layouts. Changes to generated IDL, pointer layout, conformant/varying string handling, status typing, or structure defaults can break tests even if higher-level ATSVC behavior still works.
- Only selected fields are asserted. For JobEnum output, only the first of seven entries is deeply checked, so regressions in later entries could be missed.
- `jobdel_out_check()` accepts the fixture without validating the unknown return code, leaving a known gap in status semantics coverage.
- Pointer assumptions are explicit for fields such as `servername`, `ctr`, `first_entry`, `resume_handle`, `job_id`, and `job_info`; if generated code changes pointer ownership or nullability, these tests will catch some but not all consequences.

## Test Signals

Passing this suite means the ATSVC generated NDR pull path can decode the embedded fixtures and populate key fields for JobEnum, JobAdd, JobDel, and JobGetInfo in both input and output directions. Failures usually indicate an IDL/NDR layout regression, endian/alignment issue, string decoding change, pointer conformance issue, or a changed interpretation of ATSVC status/result fields. The strongest positive signals are the decoded Unicode server/command strings, job time and flag values, total/resume counters, returned job ID, and NT success statuses for the checked operations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/ndr/atsvc.c -->
