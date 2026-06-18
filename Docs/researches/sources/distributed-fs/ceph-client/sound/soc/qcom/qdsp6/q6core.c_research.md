# sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6core.c

Purpose: `q6core.c` implements the APR Q6 core/AVCS service helper. It detects whether ADSP is ready and retrieves service API versions for other QDSP6 audio services.

Important APIs and types: `struct q6core` holds the APR device, wait queue, AVCS state, lock, response flags, version response buffers, feature-support booleans, and request state. Exported APIs are `q6core_is_adsp_ready` and `q6core_get_svc_api_info`. Internal payload types model old `AVCS_GET_VERSIONS` and newer framework-version responses.

Control flow: callbacks handle basic unsupported responses, framework-version responses, legacy version responses, and ADSP state responses, then wake waiters. `q6core_get_svc_api_info` lazily requests framework versions, falls back to legacy service versions if unsupported, caches the result, and searches for the requested service ID. `q6core_is_adsp_ready` loops for up to 3000 ms, sending get-state probes with 100 ms waits; if firmware does not support the command, it assumes ADSP is up.

State and persistence: `g_core` is a singleton set at probe and cleared on remove. Version responses are duplicated into heap memory and reused after the first request. Support booleans determine fallback behavior.

Dependencies and integration points: depends on APR, q6dsp errno for `ADSP_EUNSUPPORTED`, and DT compatible `qcom,q6core`. Other services call it during probe to fill service API info or to gate readiness.

Risks: if `g_core` or `ainfo` is missing, `q6core_get_svc_api_info` returns 0 without filling info, which can look like success. The readiness loop does not sleep beyond wait time and may issue repeated commands quickly. Version response allocation uses GFP_ATOMIC in callback and can fail under pressure, causing request errors.

Test signals: unsupported command fallback, framework-vs-legacy version lookup, absent service ID returning `-ENOTSUPP`, ADSP ready timeout, singleton probe/remove cleanup, and allocation-failure callback paths.
