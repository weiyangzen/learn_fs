# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_uc_fw_types.h

Purpose: Defines the uC firmware state machine enums, firmware type/version enums, version struct, and `struct xe_uc_fw` storage.

Important APIs/types/functions: `enum xe_uc_fw_status` models states from `NOT_SUPPORTED` and `UNINITIALIZED` through `SELECTED`, `MISSING`, `ERROR`, `AVAILABLE`, `LOADABLE`, `LOAD_FAIL`, `TRANSFERRED`, `RUNNING`, and `PRELOADED`. `enum xe_uc_fw_type` distinguishes GuC, HuC, and GSC. `enum xe_uc_fw_version_types` distinguishes release versus compatibility versions. `struct xe_uc_fw` stores type/status, path, override/full-version flags, size, BO, GSC-header flag, wanted/found versions, RSA/uCode/CSS offsets, private data size, and build type.

Control flow: The comments document expected phase transitions used by `xe_uc_fw.c` and uC subcomponents. Code elsewhere tests status ordering and type fields to decide whether firmware is supported, enabled, loadable, loaded, or PF-preloaded.

State and persistence behavior: `struct xe_uc_fw` persists inside GuC/HuC/GSC objects. The `status` field is exposed as const through a union while firmware loader internals mutate `__status`, discouraging arbitrary writes outside the loader.

Dependencies and integration points: Forward-declares `struct xe_bo`; used by firmware loader headers and GuC/HuC/GSC type definitions.

Risks: The state machine is explicitly noted as complicated. Status enum ordering affects inline predicates, and `PRELOADED` is a special high-valued state that is not locally loadable. Version arrays must be indexed by `xe_uc_fw_version_types`.

Test signals: Status transition tests across init/fetch/copy/upload/auth/reset and VF preloaded flows; compile-time coverage of all firmware types and version-type indexes.
