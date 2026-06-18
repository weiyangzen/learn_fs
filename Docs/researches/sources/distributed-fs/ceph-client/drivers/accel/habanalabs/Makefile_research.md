# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/Makefile

Purpose: assembles the HabanaLabs accelerator driver object from common and ASIC-specific object lists.

Important entries: builds `habanalabs.o` when `CONFIG_DRM_ACCEL_HABANALABS` is enabled. It includes common, gaudi2, gaudi, and goya makefile fragments and appends their object lists. Debugfs support adds `common/debugfs.o` when `CONFIG_DEBUG_FS` is enabled.

Control flow: Kbuild includes this top-level makefile, then imported fragments contribute source objects for shared and per-ASIC code.

State and persistence: no runtime state; controls build composition.

Dependencies: subdirectory Makefiles must define `HL_COMMON_FILES`, `HL_GAUDI2_FILES`, `HL_GAUDI_FILES`, and `HL_GOYA_FILES`.

Risks: include order matters because each fragment populates variables used immediately afterward. Missing debugfs conditional coverage can hide unresolved references.

Test signals: all ASIC families build, debugfs on/off, module and built-in configurations, and incremental build after adding/removing common or ASIC files.
