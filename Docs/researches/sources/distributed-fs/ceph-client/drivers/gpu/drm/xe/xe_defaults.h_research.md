# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_defaults.h

## Purpose
This header centralizes default values for Xe module/runtime configuration, including GuC logging, display probing, VRAM BAR size, force-probe policy, SR-IOV PF limits, wedged mode, and SVM notifier sizing.

## Important APIs, Types, and Functions
It defines constants such as `XE_DEFAULT_GUC_LOG_LEVEL`, `XE_DEFAULT_PROBE_DISPLAY`, `XE_DEFAULT_VRAM_BAR_SIZE`, `XE_DEFAULT_FORCE_PROBE`, `XE_DEFAULT_MAX_VFS`, `XE_DEFAULT_ADMIN_ONLY_PF`, `XE_DEFAULT_WEDGED_MODE`, `XE_DEFAULT_WEDGED_MODE_STR`, and `XE_DEFAULT_SVM_NOTIFIER_SIZE`.

## Control Flow
There is no runtime flow. Some defaults depend on compile-time configuration, such as debug builds selecting a higher GuC log level and display probing following `CONFIG_DRM_XE_DISPLAY`.

## State and Persistence Behavior
The file stores no mutable state. The constants seed module parameters, configfs defaults, and device initialization choices.

## Dependencies and Integration Points
It includes `xe_device_types.h` for wedged-mode enum values and is used by module parameter setup, configfs fallback/default logic, and device probe wedged-mode initialization.

## Risks
Defaults are user-visible policy. Changing them affects boot behavior, debug verbosity, SR-IOV exposure, and recovery semantics. Default strings must match numeric defaults to avoid misleading sysfs/module parameter presentation.

## Test Signals
Build tests, module parameter default inspection, configfs default reads, wedged-mode startup behavior, debug vs non-debug GuC log level checks, and display-enabled/disabled kernel configs validate this file.
