# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_uc_fw.h

Purpose: Declares uC firmware operations and inline status/type/version helper predicates.

Important APIs/types/functions: Declares init, RSA copy, upload, version check, and print functions. Inline helpers compute RSA offset, change status, stringify status/type, map status to errno, query supported/enabled/available/loadable/loaded/running/overridden/error states, sanitize loadable firmware, compute upload size, and expose the firmware download URL.

Control flow: Firmware code and uC subcomponents use status predicates to gate operations. Upload size and RSA offset helpers are consumed by firmware transfer/authentication paths. `xe_uc_fw_sanitize` resets loadable-or-later firmware back to `LOADABLE` across reset cycles.

State and persistence behavior: `xe_uc_fw_change_status` mutates the private `__status` field. Other helpers are read-only except sanitize. Status ordering is semantically significant because predicates compare enum values.

Dependencies and integration points: Includes errno, Xe macros, firmware ABI, and firmware types. Integrated across GuC/HuC/GSC firmware loaders and diagnostics.

Risks: Enum ordering underpins helper logic; inserting statuses in the wrong location can break `>=` predicates. `__xe_uc_fw_status` warns on uninitialized checks, so callers must follow init ordering. `xe_uc_fw_is_loadable` excludes `PRELOADED` despite its high enum value.

Test signals: Unit tests for each status-to-string/error/predicate combination, reset sanitize behavior, upload-size calculation, and RSA offset calculation for CSS-at-zero and GSC-contained CSS offsets.
