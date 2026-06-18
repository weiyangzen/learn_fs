# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_core_status.h

Purpose: this header defines numeric RAS core status codes shared by the RAS core modules. `RAS_CORE_OK` is zero and the remaining values encode not-supported and failure categories near 248-255.

Important definitions: `RAS_CORE_NOT_SUPPORTED`, `RAS_CORE_FAIL_ERROR_QUERY`, `RAS_CORE_FAIL_ERROR_INJECTION`, `RAS_CORE_FAIL_FATAL_RECOVERY`, `RAS_CORE_FAIL_POISON_CONSUMPTION`, `RAS_CORE_FAIL_POISON_CREATION`, `RAS_CORE_FAIL_NO_VALID_BANKS`, and `RAS_CORE_GPU_IN_MODE1_RESET`. Several call sites return the negative form of these constants, for example `-RAS_CORE_NOT_SUPPORTED` from notifier wrappers or `-RAS_CORE_GPU_IN_MODE1_RESET` from event handling.

Control flow and state: there is no runtime state. The constants influence error propagation through core, MP1, PSP, process, and RAS command paths, so consumers must know whether a function returns Linux `-errno`, a negative RAS status value, or zero.

Dependencies and integration: only include guards are present. It is pulled into core, CPER, GFX, MP1, and log-ring sources. Risks are semantic rather than structural: these values overlap neither conventional Linux errno values nor positive TA statuses, but they are not self-describing once negated. Test signals should verify callers do not compare these codes to raw positive constants and that reset handling treats `-RAS_CORE_GPU_IN_MODE1_RESET` as a special control signal rather than a generic failure.
