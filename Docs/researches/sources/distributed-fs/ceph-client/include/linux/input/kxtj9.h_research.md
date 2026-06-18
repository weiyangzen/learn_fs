<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/input/kxtj9.h -->
# sources/distributed-fs/ceph-client/include/linux/input/kxtj9.h

Purpose: Defines board data for Kionix KXTJ9 accelerometer input drivers.

Important APIs/types/functions: `KXTJ9_I2C_ADDR` gives the default address. `struct kxtj9_platform_data` includes minimum and initial poll interval, axis remapping, per-axis negation, resolution selection, g range, and optional init/exit/power callbacks. Macros define 8/12-bit resolution and 2g/4g/8g ranges.

Control flow: Probe configures orientation, polling, resolution/range, and power; report paths remap/negate raw axes before input events.

State/persistence: Board orientation and callbacks persist for device lifetime; resolution/range/power state is hardware state.

Dependencies/integration: Integrates I2C, input polling, platform power management, and absolute axis reporting.

Risks: Axis maps must be a valid permutation; power callbacks can fail during resume/probe.

Test signals: Orientation matrix equivalents, polling interval limits, g range scaling, suspend/resume callbacks, and input axis direction tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/input/kxtj9.h -->
