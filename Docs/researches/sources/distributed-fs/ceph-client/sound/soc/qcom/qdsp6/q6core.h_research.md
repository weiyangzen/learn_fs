# sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6core.h

Purpose: `q6core.h` exposes the small public contract for Q6 core service readiness and service-version lookup.

Important APIs and types: `struct q6core_svc_api_info` carries service ID version data as `service_id`, `api_version`, and `api_branch_version`. `q6core_is_adsp_ready` returns whether the ADSP/Q6 service is considered ready. `q6core_get_svc_api_info` fills API version fields for a service ID.

Control flow: service drivers call these helpers during probe before constructing service-specific command behavior. The header itself has no implementation state.

State and persistence: no local state. Returned data is derived from the singleton `q6core` cache in `q6core.c`.

Dependencies and integration points: consumed by `q6afe.c` and `q6asm.c`, and potentially other QDSP6 services that need firmware API version information.

Risks: callers must handle the implementation's ambiguous zero return when core state is missing. Header users need Linux integer types in scope through transitive includes.

Test signals: compile users and verify service API info is filled for known service IDs on hardware or mocked APR responses.
