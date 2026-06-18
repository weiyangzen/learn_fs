# sources/distributed-fs/ceph-client/arch/mips/sni/time.c

Purpose: SNI timer setup using A20R periodic timer or R4K count calibration.

Important APIs/types/functions: `a20r_set_periodic`, `a20r_interrupt`, `sni_a20r_timer_setup`, `dosample`, `plat_time_init`.

Control flow and state: A20R configures a clock event device and IRQ; other boards sample the R4K counter against a known delay loop to set `mips_hpt_frequency`; timer interrupt dispatches the registered clock event.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: calibration depends on stable delay/timer hardware; A20R periodic programming must match board IRQ setup; wrong frequency breaks timekeeping.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.
