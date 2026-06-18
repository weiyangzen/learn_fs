<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/abx500/ab8500-sysctrl.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/abx500/ab8500-sysctrl.h

## Purpose
This header exposes AB8500 system-control register accessors and a register/bit map for power-on/reset status, software shutdown/reset, watchdog, battery thresholds, system clocks, RF clock requests, ultra-low-power clock control, dither clocks, SWAT, and related AB9540 extensions.

## Important APIs, Types, And Functions
- Conditional APIs: `ab8500_sysctrl_read()` and `ab8500_sysctrl_write()` are available with `CONFIG_AB8500_CORE`; otherwise inline stubs return success without touching hardware.
- Convenience helpers: `ab8500_sysctrl_set()` and `ab8500_sysctrl_clear()` compose masked writes for bit set/clear operations.
- Register constants span status (`AB8500_TURNONSTATUS`, `AB8500_RESETSTATUS`), watchdog, low-battery, clock timers, SMPS clock selection, ULP clock control, system clock request validity, RF clock buffers, dither control, SWAT, HIQ clock control, VSIM clock control, and AB9540 SYSCLK12 registers.
- Bit constants provide masks/shifts for every field, including shutdown/reset bits, watchdog enable/kick, low-battery thresholds, clock source selectors, request-valid bits, and dither delay fields.

## Control Flow
Sysctrl users read status registers to determine boot/reset reasons and use masked writes to update control fields. `ab8500_sysctrl_set()` writes `bits` with the same mask and value, while `ab8500_sysctrl_clear()` writes zero under the same mask. When `CONFIG_AB8500_CORE` is disabled, callers compile but sysctrl requests are no-ops.

## State And Persistence
State is entirely in AB8500 system-control hardware registers. Some fields represent latched status, while others control persistent live behavior such as shutdown/reset, watchdog, low-battery detection, clock-buffer requests, clock source selection, and dither enables. The inline stubs create no software state.

## Dependencies And Integration Points
The header depends on `linux/bitops.h` and AB8500 core support. It integrates with platform power management, watchdog, reset/shutdown paths, clock management, regulator/power logic, and drivers that need to coordinate system clock requests.

## Risks And Edge Cases
- The no-op stubs return success when the core is disabled, which can hide missing hardware support if callers do not guard by Kconfig or device presence.
- Register constants use combined bank/register-style `u16` addresses; users must pass them through sysctrl accessors rather than generic single-bank helpers unless they know the encoding.
- Shutdown, reset, and watchdog bits are high-impact controls and should only be written from controlled paths.
- Bitfield masks and shifts require callers to pre-shift values correctly before masked writes.

## Test Signals
Test boot reason and reset-status reads, sysctrl set/clear operations, software reset/shutdown paths, watchdog enable/kick/timer behavior, low-battery threshold programming, clock request/valid fields, AB9540-specific SYSCLK12 programming, and compile/runtime behavior with `CONFIG_AB8500_CORE` disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/abx500/ab8500-sysctrl.h -->
