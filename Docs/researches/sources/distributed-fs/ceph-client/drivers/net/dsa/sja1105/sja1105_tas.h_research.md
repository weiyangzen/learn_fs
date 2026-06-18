# sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/sja1105_tas.h

Purpose: this header defines the SJA1105 TAS feature boundary. It exposes the taprio offload API, TAS setup/teardown hooks, PTP adjustment notifications, gate-conflict checking, and scheduling-table rebuild entry point when `CONFIG_NET_DSA_SJA1105_TAS` is enabled, and provides stubs otherwise.

Important APIs, types, and functions: `SJA1105_TAS_MAX_DELTA` is the maximum representable hardware interval in scheduler deltas. `enum sja1105_tas_state` models disabled, enabled-not-running, and running hardware states. `enum sja1105_ptp_op` records whether the last PTP operation was none, a clock step, or an adjustfreq. `struct sja1105_gate_entry` and `struct sja1105_gating_config` hold the global tc-gate schedule consumed by TAS. `struct sja1105_tas_data` is embedded in `struct sja1105_private` and carries all TAS runtime state.

Control flow: callers invoke `sja1105_tas_setup()` during switch setup, use `sja1105_setup_tc_taprio()` for taprio replace/destroy, call `sja1105_tas_clockstep()` or `sja1105_tas_adjfreq()` from PTP clock operations, and call `sja1105_tas_teardown()` on removal. The VL file calls `sja1105_gating_check_conflicts()` and `sja1105_init_scheduling()` when tc-gate rules change.

State and persistence: the enabled build persists offload pointers, gate lists, state-machine work, base times, and max cycle time. The disabled build intentionally reduces `struct sja1105_tas_data` to a dummy byte so the private structure remains valid without TAS code.

Dependencies and integration points: it includes `<net/pkt_sched.h>` for taprio types and relies on DSA, SJA1105 private state, PTP callbacks, and optional VL support. The stubs preserve linkability for builds without TAS while making taprio return `-EOPNOTSUPP`.

Risks: the disabled stub for `sja1105_gating_check_conflicts()` has a signature that differs from the enabled declaration in this snapshot, which is only harmless if no disabled-build caller type-checks that path. Consumers must honor the config guard because `struct sja1105_tas_data` layout changes substantially. Gate entries point at `struct sja1105_rule`, so rule lifetime must exceed schedule rebuild and teardown.

Test signals: build with TAS enabled and disabled, exercise taprio callbacks, verify PTP notifications schedule work only when needed, delete VL/taprio rules without dangling gate entries, and check that disabled builds reject offload cleanly.
