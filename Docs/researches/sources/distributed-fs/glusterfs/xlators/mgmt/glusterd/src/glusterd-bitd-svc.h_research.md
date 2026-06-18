# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-bitd-svc.h

Purpose: declares the BitD service management interface for glusterd.

Important APIs/types/functions: defines `bitd_svc_name` as `"bitd"` and declares `glusterd_bitdsvc_build()`, `glusterd_bitdsvc_init()`, `glusterd_bitdsvc_manager()`, `glusterd_bitdsvc_stop()`, and `glusterd_bitdsvc_reconfigure()`.

Control flow: glusterd initialization uses the build/init declarations to wire a `glusterd_svc_t`; bitrot option changes use the manager/reconfigure declarations.

State and persistence behavior: no state is stored in the header. The functions operate on `glusterd_svc_t` and generated service volfiles/processes.

Dependencies and integration points: includes `glusterd-svc-mgmt.h` for `glusterd_svc_t`. Used by bitrot and service initialization code.

Risks and edge cases: service name macro must match volfile path naming, process management, and logs. Prototype drift breaks callers at compile time.

Test signals: compile/link glusterd with bitd service enabled and exercise all declared functions through bitrot operations.
