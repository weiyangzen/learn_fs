<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/package/launch-simple-longhorn -->
## sources/control-plane/longhorn-engine/package/launch-simple-longhorn

Purpose: simple demo/dev launcher that starts one Longhorn replica process and one controller process under instance-manager.

Important behavior: requires `volume`; defaults size to `1g` and frontend to `tgt-blockdev`; bind-mounts `/host/dev`; waits for instance-manager health; starts TGT; creates a replica process with 15 ports; sleeps five seconds; creates controller process with one port and replica `tcp://localhost:10000`.

Control flow and state: background setup performs process creation while foreground execs `longhorn-instance-manager daemon`.

Dependencies and integration points: integrates TGT, instance-manager process create, `longhorn replica`, `longhorn controller`, and health probe.

Risks: fixed sleep for replica readiness is brittle. Hardcoded localhost port assumptions can collide. Unquoted shell tests are fragile. Script is suitable for simple local launch, not resilient orchestration.

Test signals: local container smoke tests covering instance-manager health, replica creation, controller creation, and frontend startup.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/package/launch-simple-longhorn -->
