# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/selftest_guc.c

Purpose: provides live GuC submission selftests for CTB recovery, GuC ID exhaustion and stealing, and fast error response handling.

Important APIs/types/functions: helpers are `request_add_spin()` and `nop_user_request()`. Subtests are `intel_guc_scrub_ctbs()`, `intel_guc_steal_guc_ids()`, and `intel_guc_fast_request()`, registered through `intel_guc_live_selftests()`. The code uses `igt_spinner`, request fences, runtime PM wakerefs, context creation, `intel_gt_wait_for_idle()`, `intel_gt_handle_error()`, and `intel_guc_send_nb()`.

Control flow: CTB scrub creates contexts with injected dropped schedule-enable, schedule-disable, and deregister G2H messages, waits for completion, forces GT error handling, then verifies idle. GuC ID stealing temporarily reduces available GuC IDs, blocks submissions behind a spinner until creation returns `-EAGAIN`, releases the spinner, submits again, and verifies `number_guc_id_stolen` increments. Fast request sends an invalid asynchronous H2G while a spinner proves the GPU remains alive, then waits for `fast_response_selftest` to record the expected error response.

State and persistence: tests temporarily mutate context drop flags, `guc->submission_state.num_guc_ids`, `guc->fast_response_selftest`, and request/context references. Cleanup restores the GuC ID count, releases requests and contexts, ends spinners, idles the GT where needed, and drops runtime PM refs.

Risks and test signals: risks include leaked request references on error paths, timeout sensitivity, leaving a spinner active, and failing to restore reduced GuC ID limits. Expected signals are skipped tests on wedged GTs or non-GuC submission, successful idle after reset scrub, observed GuC ID steal count change, and invalid H2G producing a fast response without killing the spinner.
