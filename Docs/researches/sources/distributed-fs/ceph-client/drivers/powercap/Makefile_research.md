# sources/distributed-fs/ceph-client/drivers/powercap/Makefile

## Purpose
`drivers/powercap/Makefile` maps powercap Kconfig symbols to built objects.

## Important APIs, Types, And Functions
It declares `obj-$(CONFIG_DTPM) += dtpm.o`, CPU and devfreq DTPM backends, generic `powercap_sys.o`, Intel RAPL core/MSR/TPMI objects, `idle_inject.o`, and `arm_scmi_powercap.o`.

## Control Flow
Kbuild includes each object when the corresponding config is `y` or `m`, subject to symbol type. `powercap_sys.o` follows `CONFIG_POWERCAP`; DTPM backends are independently gated by their specific symbols.

## State, Persistence, And Dependencies
There is no runtime state. Build state follows Kconfig. Because `DTPM`, `DTPM_CPU`, and `DTPM_DEVFREQ` are bool in Kconfig, their objects are built-in when enabled, not modules.

## Integration Points
The file is the build bridge for the Kconfig options and source files in `drivers/powercap`. It must stay consistent with `dtpm_subsys.h` conditional subsystem list.

## Risks
Missing object entries would silently omit enabled subsystems; current entries cover the visible Kconfig options. Ordering builds generic `dtpm.o` before its backends but link order rarely matters for these symbols in built-in code.

## Test Signals
Run build matrix checks for each config symbol and verify expected objects appear in `drivers/powercap/` build output, especially `CONFIG_POWERCAP=m/y`, Intel RAPL variants, DTPM backend combinations, and SCMI module naming.
