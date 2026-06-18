# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_rogue_defs.h

Purpose: This header provides common Rogue GPU constants used across firmware boot, reset, MMU, power, cache, and feature setup code. It sits below the FWIF structures and above raw register definitions by combining `pvr_rogue_cr_defs.h` fields into reusable policy macros.

Important APIs/types/functions: The file exports OS/thread limits (`ROGUE_FW_MAX_NUM_OS`, `ROGUE_FW_HOST_OS`, `ROGUE_FW_THREAD_0/1`), cache-line conversion (`GET_ROGUE_CACHE_LINE_SIZE`), maximum geometry/fragment contexts, all-on/all-auto clock-control values, S7 soft-reset group masks, PM physical/virtual page sizes, dust/phantom/Bernado/BlackPearl cluster-count rounding macros, FW MMU context IDs, CAT base address macros (`BIF_CAT_BASEX`, `FWCORE_MEM_CAT_BASEX`), remap field aliases, shared register capacity constants, timer tick size, no-HW multicore cap, SLC cache thresholds, FW boot-stage register, virtualization register stride, HWPerf feature marker, and TRP core cap. There are no structs or functions.

Control flow: None directly. The reset masks imply a hardware reset sequence: dusts, Jones blocks, optional BIF/SLC/Garten, then secondary blackpearl/pixel/CDM/vertex reset domains. Consumers choose masks based on feature and power state.

State and persistence behavior: No local state. Constants determine persistent hardware register values, firmware-visible initialization choices, MMU context mappings, and virtualized OS partition geometry.

Dependencies and integration points: Depends on `pvr_rogue_cr_defs.h` for raw register fields and Linux `BIT`. It is included by `pvr_rogue_fwif.h` and by lower-level driver code configuring clocking, reset, FW boot, PM memory, and virtualization.

Risks: This is a high-impact constants file. Wrong reset masks can leave functional blocks live during reset or over-reset shared units. Wrong page sizes or CAT base formulas can break PM allocation and MMU setup. `GET_ROGUE_CACHE_LINE_SIZE` depends on signed positive input semantics and should not be used with unknown-width values without validation.

Test signals: Kernel build, boot-to-firmware-init tests, GPU reset/HWR recovery loops, PM freelist allocation tests, virtualization OSID tests, and hardware trace comparisons for clock/reset register writes are the strongest signals.
