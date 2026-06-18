# sources/control-plane/rook/pkg/daemon/ceph/client/mon.go

Purpose: wraps monitor quorum/dump reads and stretch-cluster monitor configuration commands.

Important APIs/types: `MonStatusResponse`, `MonMapEntry`, `AddrvecEntry`, `MonDump`, and `MonDumpEntry` model quorum and mon dump JSON. Public functions include `GetMonQuorumStatus()`, `GetMonDump()`, `EnableStretchElectionStrategy()`, `CreateDefaultStretchCrushRule()`, `SetMonStretchTiebreaker()`, and `SetNewTiebreaker()`.

Control flow and state: quorum and dump functions are read-only JSON commands. `EnableStretchElectionStrategy()` runs `mon set election_strategy connectivity`. `CreateDefaultStretchCrushRule()` builds a replicated pool spec using stretch cluster sub-failure-domain and delegates to CRUSH rule creation helpers defined elsewhere. `SetMonStretchTiebreaker()` runs `mon enable_stretch_mode <mon> <default-rule> <bucket-type>` and treats EINVAL containing "stretch mode is already engaged" as idempotent success. `SetNewTiebreaker()` mutates the active tiebreaker with `mon set_new_tiebreaker`.

Dependencies and integration: used by stretch-cluster reconciliation and monitor status flows. It depends on `cephv1.ClusterSpec`, CRUSH rule helpers, errno extraction, and shared command execution. Risks include string matching for idempotent stretch-mode errors, partial stretch configuration if CRUSH rule creation succeeds but tiebreaker setting fails, and JSON schema drift in monitor address structures. Tests cover arg finalization, election strategy, tiebreaker commands, and mon dump parsing.
