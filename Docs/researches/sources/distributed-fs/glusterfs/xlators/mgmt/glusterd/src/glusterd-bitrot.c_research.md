# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-bitrot.c

Purpose: implements glusterd CLI/RPC handling, staging, commit, option mutation, and daemon orchestration for bitrot and scrub features.

Important APIs/types/functions: `gd_bitrot_op_list` maps option enum values to strings. Request entry points are `__glusterd_handle_bitrot()` and `glusterd_handle_bitrot()`. Option handlers include `glusterd_bitrot_enable()`, `glusterd_bitrot_disable()`, scrub throttle/frequency/state handlers, expiry-time, and signer-thread handlers. Service policy functions are `glusterd_should_i_stop_bitd()` and `glusterd_manage_bitrot()`. Operation phases are `glusterd_op_stage_bitrot()` and `glusterd_op_bitrot()`.

Control flow: the handler decodes the CLI dict, extracts volume/type, routes scrub status and ondemand commands to specialized ops, and otherwise starts the `GD_OP_BITROT` synctask. Stage validates volume existence, started status, bitrot enablement for non-enable commands, op-version for ondemand handled earlier, and duplicate scrub state. Commit finds the volume, switches on operation type, mutates `volinfo->dict`, reconfigures bitd or scrub services when needed, manages bitd/scrub daemon start/stop for enable/disable, recreates volfiles, notifies services, and stores `volinfo` with version increment.

State and persistence behavior: persistent volume options include `features.bitrot`, `features.scrub`, `features.scrub-throttle`, `features.scrub-freq`, `features.expiry-time`, and `features.signer-threads`. Service side effects include BitD and scrub daemon restarts/reconfigures and generated volfiles. Runtime decisions inspect `conf->volumes`, brick locality, brick status, and cluster op-version.

Dependencies and integration points: depends on glusterd op-state-machine, store, utils, volgen, scrub service, bitd service, RPC/XDR decode, dict APIs, compatibility errno, and op-version constants. It integrates CLI commands with management transaction phases and service managers.

Risks and edge cases: service reconfiguration can partially succeed before store failure. `is_bitd_configure_noop()` skips restart unless a local started brick needs bitrot; wrong locality/status data can leave BitD stopped incorrectly. Duplicate code artifacts in this snapshot show repeated lines around scrub frequency and switch, which deserve syntax/build validation. Scrub resume maps to `Active`, so string comparisons must remain compatible with stored values.

Test signals: enable/disable bitrot on stopped/started volumes, repeat enable/disable, scrub pause/resume/status/ondemand with op-version gating, throttle/frequency/expiry/signer thread changes, local vs remote brick service decisions, store failure injection, and volfile regeneration/reconfigure behavior.
