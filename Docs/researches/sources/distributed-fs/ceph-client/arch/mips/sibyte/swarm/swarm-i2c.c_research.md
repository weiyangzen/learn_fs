# sources/distributed-fs/ceph-client/arch/mips/sibyte/swarm/swarm-i2c.c

Purpose: I2C board-info registration for SWARM RTC devices.

Important APIs/types/functions: `swarm_i2c_info` with `m41t81` at address `0x68`; `swarm_i2c_init`.

Control flow and state: a late initcall registers board info on SMBus/I2C bus 1 so the generic I2C RTC driver can bind when enabled.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: must agree with hardware bus numbering and address; duplicates can conflict with direct RTC helpers.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.
