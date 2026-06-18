# sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6routing.h

Purpose: declares the public Q6 routing hooks used by QDSP6 PCM/ASM frontend code to notify the routing component that a stream is opening or closing.

Important APIs: `q6routing_stream_open(int fedai_id, int perf_mode, int stream_id, int stream_type)` registers a frontend DAI/session with the routing component and triggers backend COPP/matrix setup. `q6routing_stream_close(int fedai_id, int stream_type)` tears down the session mapping.

Control flow and state: this header holds no state. It deliberately hides `struct session_data`, `struct msm_routing_data`, COPP arrays, and DAPM mixer implementation details from callers.

Dependencies and integration: included by QDSP6 PCM/ASM users that know the frontend DAI ID and stream ID. The implementation depends on ASoC mixer route setup having already selected `session->port_id`.

Risks: no type safety for stream direction, performance mode, or ID ranges. Callers must keep open/close calls balanced and pass the same frontend DAI ID used in mixer setup.

Test signals: compile/link of QDSP6 PCM users, route-open succeeds only after userspace mixer selection, and route-close releases all COPPs for the frontend without affecting other sessions.
