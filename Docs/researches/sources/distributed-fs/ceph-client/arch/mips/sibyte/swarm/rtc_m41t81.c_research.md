# sources/distributed-fs/ceph-client/arch/mips/sibyte/swarm/rtc_m41t81.c

Purpose: direct SMBus access driver helpers for the M41T81 RTC used as persistent clock.

Important APIs/types/functions: `m41t81_read`, `m41t81_write`, `m41t81_set_time`, `m41t81_get_time`, `m41t81_probe` plus BCD register definitions.

Control flow and state: read/write poll SMBus controller 1 busy/error bits, select RTC register addresses, and transfer bytes; set/get convert between `time64_t` and BCD fields, manage stop/century bits, and probe checks device presence.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: busy-wait loops have no timeout; raw SMBus access bypasses generic I2C locking; century/year handling must remain consistent; errors return sentinel values used by setup fallback logic.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.
