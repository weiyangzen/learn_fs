# sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6prm.c

Purpose: implements the Q6 Proxy Resource Manager GPR service client used to request/release AudioReach LPASS hardware clocks and hardware cores from the audio DSP.

Important APIs and functions: exported symbols are `q6prm_set_lpass_clock()`, `q6prm_vote_lpass_core_hw()`, and `q6prm_unvote_lpass_core_hw()`. Internally, `q6prm_set_hw_core_req()`, `q6prm_request_lpass_clock()`, and `q6prm_release_lpass_clock()` allocate AudioReach command packets, fill `apm_module_param_data`, and send synchronous PRM commands. `prm_callback()` receives `PRM_CMD_RSP_REQUEST_HW_RSC` and `PRM_CMD_RSP_RELEASE_HW_RSC`.

Control flow: `prm_probe()` allocates `struct q6prm`, initializes a mutex and waitqueue, stores it as GPR driver data, defers until ADSP readiness, and then populates child platform devices. Clock/core clients are children, so exported calls recover the PRM instance through `dev->parent`. `q6prm_send_cmd_sync()` serializes command submission and waits for the matching response opcode.

State and persistence: persistent runtime state is the per-device `q6prm` object containing the GPR device pointer, last response result, waitqueue, and mutex. No settings survive driver unbind or DSP restart.

Dependencies and integration: integrates Linux GPR/APR transport, AudioReach packet helpers, APM command layouts, q6apm readiness, and OF compatible `qcom,q6prm`.

Risks: command payload sizes and parameter IDs must match DSP firmware exactly. `q6prm_release_lpass_clock()` only fills `clock_id`, leaving attr/root/freq unused in the release payload, so firmware expectations matter. Parent-child device assumptions are central.

Test signals: successful GPR probe after ADSP readiness, no command timeout, correct PRM response status, and observable enable/disable of MI2S or codec macro clocks during PCM startup/shutdown.
