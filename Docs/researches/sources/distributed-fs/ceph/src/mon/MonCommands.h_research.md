# sources/distributed-fs/ceph/src/mon/MonCommands.h

## Purpose

`MonCommands.h` is a deliberately unguarded command-definition inventory for Ceph monitor command descriptions. It is intended to be included multiple times with different definitions of `COMMAND`, `COMMAND_WITH_FLAG`, or related macros so callers can generate command tables, help text, command parsing metadata, module routing data, permissions, and visibility/forwarding flags from one authoritative list. The file is data-as-C++-preprocessor rather than conventional executable code.

The leading comment documents the command signature DSL consumed by the Python `ceph` frontend and by monitor-side command parsing. Each command signature encodes literals, typed arguments, repeat counts, optional flags, allowed values, good-character constraints, and positional versus non-positional separation. The monitor ultimately sees parsed command JSON as `cmdmap_t`/`cmd_vartype` data and dispatches by prefix to the relevant monitor service.

## Important APIs, types, and command surfaces

Important macro-facing APIs are:

- `COMMAND(signature, helpstring, modulename, req_perms)` for ordinary commands.
- `COMMAND_WITH_FLAG(signature, helpstring, modulename, req_perms, FLAG(...))` for hidden, deprecated, obsolete, manager-routed, polling, tell/asok, and no-forward commands.
- `DEFAULT_GOODCHARS`, `FS_NAME_GOODCHARS`, and `CLASS_GOODCHARS`, which constrain several CephString arguments.
- `FLAG(NONE)`, `FLAG(NOFORWARD)`, `FLAG(OBSOLETE)`, `FLAG(DEPRECATED)`, `FLAG(MGR)`, `FLAG(POLL)`, `FLAG(HIDDEN)`, and `FLAG(TELL)` as documented command metadata.

The file covers monitor-visible command families for:

- Placement group and generic OSD queries near the top, such as `pg map`, `pg repeer`, and `osd last-stat-seq`.
- Authentication commands implemented by `AuthMonitor`, including export/get/list/import/add/rotate/caps/rm and pending-key workflows.
- Core monitor commands implemented by `Monitor`, including status, health, log, quorum status, node listing, ok-to-stop checks, `tell`, monitor metadata, monitor versions, and monitor store scrub/compact.
- CephFS/MDS commands implemented by `MDSMonitor` and FS command handlers, including filesystem creation/removal/reset, flags, feature and compatibility manipulation, mirroring, rename, swap, and MDS fail/repair/remove operations.
- Monmap commands, including `mon dump`, `mon getmap`, `mon add`, `mon rm`, feature listing/setting, rank/address/weight mutation, msgr2 enablement, election strategy, disallowed leaders, CRUSH-style monitor location, and stretch-mode tiebreaker operations.
- OSD and CRUSH commands, including map dumps, metadata, CRUSH bucket/rule/class/weight-set changes, OSD flags, releases, pg-upmap controls, blocklist commands, OSD creation/removal/purge/lost workflows, and pool creation/deletion/parameter/application/stretch/tiering commands.
- `config-key`, manager, central config, and NVMe-oF gateway commands.
- Legacy tell/asok aliases used during upgrade windows before all monitor command handling moved to the newer path.

## Control flow and integration points

This header has no runtime control flow on its own. Control flow is imposed by the includer. In practice, a monitor command-description generator includes this file with `COMMAND` macros expanded into command descriptor records; command dispatch code then uses the generated descriptors to validate CLI/API input, enforce permissions, and route parsed commands to service-specific handlers.

The `modulename` and `req_perms` fields are integration points with Cephx capability checks. The module also directs implementation ownership: for example auth commands go to `AuthMonitor`, monmap commands to `MonmapMonitor`, OSD commands to `OSDMonitor`, config-key commands to `KVMonitor`, manager commands to `MgrMonitor`, and core monitor/tell commands to `Monitor` or admin-socket handling.

The flag field changes dispatch behavior:

- `TELL` commands are hidden/no-forward commands for daemon admin-socket style handling.
- `MGR` commands route through ceph-mgr rather than being handled by monitors.
- `DEPRECATED` and `OBSOLETE` influence help visibility and frontend warnings/compatibility.
- `POLL` documents high-frequency status commands.
- `NOFORWARD` prevents forwarding through the leader path.

## State and persistence behavior

This file does not own persistent state. It defines the public and semi-public command surface that mutates persistent monitor service maps elsewhere. Several declared commands are persistence-sensitive because they change Paxos-backed monitor state:

- `mon feature set`, `mon set-rank`, `mon set-addrs`, `mon set-weight`, and stretch/election commands mutate monmap state.
- OSD map, CRUSH map, pool, erasure-code-profile, blocklist, and release commands mutate OSDMonitor state.
- Auth commands mutate the auth database.
- Config and config-key commands mutate monitor config stores.
- MDS/FS commands mutate FSMap/MDSMap state.

Because this file is the validation metadata source, any mismatch between a signature here and handler expectations can reject valid operations, accept malformed requests, or mis-shape `cmdmap_t` values before persistence code runs.

## Dependencies

The header depends on macro definitions supplied by includers. It also depends conceptually on:

- `cmdparse` type names and validators such as `CephInt`, `CephFloat`, `CephString`, `CephIPAddr`, `CephEntityAddr`, `CephPgid`, `CephOsdName`, `CephChoices`, `CephBool`, `CephUUID`, and `CephPrefix`.
- Monitor service handlers that recognize the literal `prefix` produced from each command signature.
- Frontend command parsers that consume `get_command_descriptions` output.
- Capability enforcement that interprets the module and permission string fields.

## Risks and edge cases

- The file intentionally has no include guard. Accidental ordinary inclusion without the right macro setup will either fail to compile or produce duplicated definitions.
- The command-signature DSL is whitespace-sensitive. Missing spaces between adjacent string fragments or extra malformed descriptors can change parser behavior.
- There is at least one suspicious descriptor typo: `osd pool application get` uses `req=fasle` for `pool`, which looks like a misspelling of `req=false`; depending on parser strictness, this may make the argument required by default or be rejected/ignored.
- Several commands use historical aliases (`auth print_key`, `mon remove`, `osd blacklist`, `config-key put/del/list`, `osd pool delete`, tier remove aliases). Changing or deleting them can break upgrade, automation, or user scripts.
- Destructive commands rely on boolean confirmation fields such as `yes_i_really_mean_it`; signature mistakes can weaken or over-tighten guardrails before service-side checks.
- Very long `CephChoices` lists for pool variables and flags can drift from handler-supported variables, producing hard-to-debug CLI/API skew.
- Module/permission mismatches are security-sensitive because they determine which Cephx caps authorize a command.

## Test signals

Useful test coverage should include:

- Command-description generation tests that include this file with descriptor-producing macros and verify parsing of representative signatures from each module.
- CLI parser tests for optional arguments, repeated `n=N` arguments, `CephBool` non-positional behavior, `--` separation, `goodchars`, and long `CephChoices` lists.
- Negative tests for deprecated/hidden/tell/no-forward/manager flags and command visibility.
- Handler-dispatch tests ensuring every declared prefix maps to an implementation path and that handler-required cmdmap keys match signature names and types.
- Upgrade/compatibility tests for deprecated aliases and legacy tell/asok commands.
- Security tests that validate module permission strings against expected Cephx caps for read-only versus mutating commands.
