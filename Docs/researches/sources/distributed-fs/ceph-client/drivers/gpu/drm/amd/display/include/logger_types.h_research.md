# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/include/logger_types.h

Purpose: Defines the low-level logging macro vocabulary for AMD DC and the minimal logger state needed to route logs to a DRM device.

Important APIs and types: `DC_LOG_ERROR`, `DC_LOG_WARNING`, `DC_LOG_DEBUG`, `DC_LOG_INFO`, and many category-specific macros map to `drm_err`, `drm_warn`, `drm_dbg`, `drm_dbg_dp`, `drm_dbg_kms`, `drm_info`, or `pr_debug`. `struct dc_log_buffer_ctx` tracks an append buffer, and `struct dal_logger` stores `struct drm_device *dev`.

Control flow: Category macros route messages by compile-time macro expansion through a global/current `DC_LOGGER`. Some categories use DRM device-scoped logging; others use `pr_debug` with literal prefixes such as `[GAMMA]`, `[DML]`, `[SMU_MSG]`, or `[REGISTER_WRITE]`.

State and persistence: `dal_logger` only persists a DRM device pointer. Buffer contexts track caller-managed buffers and positions. Category enablement is governed by DRM dynamic debug/kmsg mechanisms outside this header.

Dependencies and integration points: Includes `os_types.h` and depends on DRM logging APIs. Used by `logger_interface.h` and display modules for hotplug, MST, link training, bandwidth validation, gamma, DSC, SMU, MALL, and register access logs.

Risks: Macros require `DC_LOGGER` to resolve to a valid logger; null logger/device paths can crash. Category selection affects debug visibility, especially `pr_debug` categories not tied to a DRM device. Excess logging in hot paths can affect timing-sensitive link training if enabled broadly.

Test signals: Build coverage with DRM logging headers, dynamic debug category checks, null logger defensive coverage in callers, and log-rate behavior under hotplug/link-training storms.
