## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_rc.c

Purpose: manages GuC RC (render/GT power state control) support selection and toggling between firmware-controlled and host-controlled RC modes.

Important APIs, types, and functions:
- `__guc_rc_supported()` allows GuC RC only when GuC submission is supported and graphics version is Gen12+.
- `__guc_rc_selected()` requires support and GuC submission selection.
- `intel_guc_rc_init_early()` stores support/selection booleans on `struct intel_guc`.
- `guc_action_control_gucrc()` sends `INTEL_GUC_ACTION_SETUP_PC_GUCRC` with `INTEL_GUCRC_FIRMWARE_CONTROL` or `INTEL_GUCRC_HOST_CONTROL`.
- `__guc_rc_control()` checks `intel_uc_uses_guc_rc()`, GuC readiness, sends control action, logs failures/success.
- `intel_guc_rc_enable()` and `intel_guc_rc_disable()` are public wrappers.

Control flow:
- Early init derives capability. Enable/disable are called once GuC is ready and UC policy says GuC RC is used.
- Control action is synchronous over the GuC send path and positive firmware return is normalized to `-EPROTO`.

State and persistence:
- Persistent selection state is `guc->rc_supported` and `guc->rc_selected`. Runtime hardware/firmware RC mode changes after successful control action.

Dependencies and integration points:
- Depends on GuC submission selection, UC policy checks, GuC readiness, GuC send path, and GuC print helpers.

Risks:
- Calling enable/disable before GuC readiness returns `-EINVAL`.
- Platform/support gating must remain aligned with firmware capabilities.
- RC mode changes affect power management behavior and can interact with reset/suspend flows.

Test signals:
- Gen12+ GuC submission boot should enable RC successfully when policy selects it.
- Unsupported/pre-Gen12 and GuC-submission-disabled paths should return/use false selectors.
- Fault GuC action failures and verify probe-error logging.
