<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_acl_flex_actions.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_acl_flex_actions.c

## Purpose

`spectrum_acl_flex_actions.c` connects the generic ACL flexible-action engine to Spectrum resources. It supplies `mlxsw_afa_ops` for KVDL action-set storage, forwarding entries, counters, mirroring, policing, and packet sampling, and initializes/destroys `mlxsw_sp->afa`.

## Important APIs, Types, And Functions

- `mlxsw_sp_act_kvdl_set_add()` allocates non-first action sets from KVDL and writes them with `PEFA`.
- Spectrum-1 and Spectrum-2 wrappers differ in the `ca` flag and activity support.
- `mlxsw_sp_act_kvdl_fwd_entry_add()` allocates PBS KVDL entries and writes `PPBS`.
- Counter helpers allocate/free flow counters.
- Mirror helpers acquire SPAN agents and analyzed-port references.
- Policer helpers allocate/delete single-rate byte policers.
- Spectrum-2 sampler helpers program policy-engine sample trigger params and use SPAN session `MLXSW_SP_SPAN_SESSION_ID_SAMPLING`.
- `mlxsw_sp1_act_afa_ops` and `mlxsw_sp2_act_afa_ops` export chip-specific AFA callbacks.
- `mlxsw_sp_afa_init()` and `mlxsw_sp_afa_fini()` own AFA object lifetime.

## Control Flow

When AFA needs extra action sets, the first set is left in TCAM and later sets are allocated in KVDL and written to `PEFA`. Spectrum-2 queries `PEFA` for activity, while Spectrum-1 reports unsupported. Forward actions allocate PBS entries and write the local port. Mirror and sampler actions acquire shared SPAN/analyzed-port resources before returning a span id to AFA; delete releases in reverse. Sampling is rejected on Spectrum-1 and fully wired on Spectrum-2 by setting sample trigger params before acquiring a SPAN agent.

## State And Persistence

State is mainly owned by referenced subsystems: KVDL allocations for action sets/PBS, flow counters, SPAN agents, analyzed-port references, policer indexes, and sample trigger params. Hardware state persists in `PEFA`, `PPBS`, policer/counter blocks, and SPAN/sample configuration until AFA destruction or action deletion.

## Dependencies And Integration Points

The file integrates `core_acl_flex_actions` with Spectrum KVDL, counters, policers, SPAN, sampling, ports, and core resource `ACL_ACTIONS_PER_SET`. It is initialized during Spectrum ACL setup and used by rule action helper functions in `spectrum_acl.c`.

## Risks

- Add/delete callbacks must be exactly balanced or KVDL, SPAN, policer, or sampling resources leak.
- Sampling uses one policy-engine trigger; multiple users must be compatible with trigger-param lifetime.
- Spectrum-1 sampler delete warns unconditionally and should only be reached after impossible add success.
- `local_port` indexes directly into `mlxsw_sp->ports`; invalid callers can dereference missing ports.

## Test Signals

Validate multi-set ACL actions, activity query on Spectrum-2, mirror add/delete, forward-to-port actions, policer and counter allocation cleanup, Spectrum-1 sampling rejection, Spectrum-2 sampling with truncation/rate parameters, and failure unwind at every allocation/register-write step.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_acl_flex_actions.c -->
