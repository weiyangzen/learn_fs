# sources/distributed-fs/ceph-client/drivers/platform/x86/amd/pmf/tee-if.c

## Purpose
`tee-if.c` implements the AMD PMF Smart PC policy engine interface to AMDTEE. It loads a platform policy binary from firmware memory, opens a trusted application session, initializes the policy builder TA, periodically invokes policy enactment, and applies returned actions to PMF firmware limits, BIOS outputs, or synthetic input events.

## Important APIs, Types, and Functions
The exported PMF entry points are `amd_pmf_init_smart_pc()`, `amd_pmf_deinit_smart_pc()`, `amd_pmf_tee_init()`, `amd_pmf_tee_deinit()`, `amd_pmf_start_policy_engine()`, and `amd_pmf_invoke_cmd_enact()`. Shared-memory command setup is centralized in `amd_pmf_prepare_args()`. `amd_pmf_invoke_cmd_init()` sends the policy binary to the TA, while `amd_pmf_invoke_cmd()` is the delayed-work callback that repeatedly calls `amd_pmf_invoke_cmd_enact()`. `amd_pmf_apply_policies()` interprets TA actions and programs PMF command IDs such as `SET_SPL`, `SET_SPPT`, `SET_FPPT`, `SET_STT_LIMIT_APU`, `SET_P3T`, and PMF PPT variants.

The file uses TEE core types `struct tee_context`, `struct tee_ioctl_invoke_arg`, `struct tee_param`, and TEE shared memory, plus PMF TA protocol structures such as `struct ta_pmf_shared_memory`, `struct ta_pmf_init_table`, `struct ta_pmf_enact_table`, and `struct ta_pmf_enact_result`. Debug builds expose module parameters `pb_actions_ms` and `pb_side_load` and a debugfs policy-binary sideload path.

## Control Flow
`amd_pmf_init_smart_pc()` first checks BIOS Smart PC advertisement with `apmf_check_smart_pc()`. It initializes delayed work, asks firmware to expose the DRAM address with `amd_pmf_set_dram_addr()`, maps the policy resource with `devm_ioremap_resource()`, copies the policy into a devm buffer, rejects all-`0xff` policy buffers, allocates `prev_data`, then tries each UUID in `amd_pmf_ta_uuid`. For each UUID it opens AMDTEE context/session/shared memory through `amd_pmf_tee_init()` and starts the policy engine. On success, it enables callback buffering state and registers an input device for TA system-state events.

`amd_pmf_start_policy_engine()` validates the policy cookie and length, adjusts `dev->policy_sz` to the real policy length plus header padding, invokes TA initialization, marks `smart_pc_enabled`, and schedules periodic enactment after a startup delay. Each periodic enactment clears shared memory, populates TA inputs, invokes the TA command, and, when the TA returns success with actions, applies each action. Duplicate power-limit writes are suppressed by comparing against `dev->prev_data`.

## State and Persistence
Policy binary contents are copied into `dev->policy_buf`, shared with the TA through `dev->fw_shm_pool`, and tracked by `dev->policy_sz`. Runtime state includes `dev->tee_ctx`, `dev->session_id`, `dev->shbuf`, `dev->prev_data`, `dev->smart_pc_enabled`, `dev->cb_flag`, and the delayed work item. None of this persists across boot. The TA's output affects live firmware power limits and BIOS output values immediately. In debug mode, policy sideload replaces the devm policy buffer and restarts the policy engine.

## Dependencies and Integration Points
This file integrates with AMDTEE through the Linux TEE client API, PMF core firmware command helpers, PMF sensor/input population helpers, APMF Smart PC resource setup, input subsystem key events (`KEY_SLEEP`, `KEY_SUSPEND`, `KEY_SCREENLOCK`), and debugfs for policy sideloading. BIOS output actions are delegated to `amd_pmf_smartpc_apply_bios_output()`.

## Risks and Test Signals
Important risks include policy-size validation mistakes, TA ABI drift, repeated delayed-work scheduling after error paths, and action-count trust. The code validates cookie presence and minimum sizes, but action array bounds depend on TA-provided structures. `amd_pmf_update_bios_output()` converts an action index to `bios_idx` without checking `amd_pmf_get_bios_output_idx()` for `-EINVAL`; current callers only pass BIOS output cases, but this assumption should remain protected. Deinit unregisters the input device with `input_unregister_device()` even though it was devm-allocated, which is a lifetime pattern worth regression testing. Test signals include successful Smart PC enablement, no policy path returning `-EINVAL`, periodic enactment cadence, duplicate-action suppression, suspend/shutdown cleanup via `cancel_delayed_work_sync()`, debugfs sideload failure handling, and validation that input events are emitted for TA system-state actions.
