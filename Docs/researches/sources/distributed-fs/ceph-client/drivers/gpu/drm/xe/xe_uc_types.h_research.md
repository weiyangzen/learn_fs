# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_uc_types.h

Purpose: Defines the aggregate Xe microcontroller container embedded in each GT.

Important APIs/types/functions: `struct xe_uc` contains `struct xe_guc guc`, `struct xe_huc huc`, `struct xe_gsc gsc`, and `struct xe_wopcm wopcm`.

Control flow: No executable flow. Lifecycle code in `xe_uc.c` initializes and operates these members in a defined order.

State and persistence behavior: The aggregate persists for GT lifetime and owns all uC subcomponent state. WOPCM state is present even though VF paths skip WOPCM initialization.

Dependencies and integration points: Includes GuC, HuC, GSC, and WOPCM type headers. Used by GT structures, uC lifecycle, debugfs, firmware code, and subcomponent helpers.

Risks: Struct layout couples `container_of` helpers in `xe_uc.c` and `xe_uc_fw.c` to member placement in surrounding GT/subcomponent structs. Adding new uC components requires lifecycle/debugfs updates.

Test signals: Compile coverage and GT initialization tests that validate all subcomponents are initialized, exposed, and torn down appropriately.
