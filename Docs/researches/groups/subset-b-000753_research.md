# Research: subset-b-000753

Grouped research for MIPS SiByte/SNI/TXX9/VDSO tooling and Nios II architecture support files. Each section is keyed by the exact source path for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sibyte/common/sb_tbprof.c -->

# sources/distributed-fs/ceph-client/arch/mips/sibyte/common/sb_tbprof.c

Purpose: character-device module exposing SiByte SCD trace-buffer/ZBbus profiling through major 240 and `/dev/tb`.

Important APIs/types/functions: `sbprof_tb_open`, `sbprof_tb_read`, `sbprof_tb_ioctl`, `sbprof_zbprof_start/stop`, `arm_tb`, trace-freeze and perf-counter IRQ handlers, global `struct sbprof_tb sbp`, and ioctl commands `SBPROF_ZBSTART`, `SBPROF_ZBSTOP`, `SBPROF_ZBWAITFULL`.

Control flow and state: open allocates a large vmalloc trace buffer and initializes wait queues; start requests trace-freeze and perf-counter IRQs, configures SCD performance counters, address traps, trace events/sequences, and arms delayed sampling; the trace-freeze interrupt drains 256 bundles into `sbprof_tbbuf`, re-arms until full/disabled, and wakes waiters; read copies captured samples to userspace by file offset; cleanup unregisters the class/device/char major.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: very hardware-specific MMIO and interrupt assumptions; busy interaction with global SCD counters and trace buffer can conflict with other users; open/release state is fragile, including a release check that returns when `sbp.open != SB_CLOSED`, which appears inverted for normal cleanup; stop has a documented wakeup race window; fixed major and large allocation can fail or conflict.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sibyte/common/sb_tbprof.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sibyte/sb1250/Makefile -->

# sources/distributed-fs/ceph-client/arch/mips/sibyte/sb1250/Makefile

Purpose: Kbuild list for SB1250 board support.

Important APIs/types/functions: `obj-y := setup.o irq.o time.o`; conditional `smp.o` for `CONFIG_SMP`.

Control flow and state: Kbuild includes setup, interrupt, and time support unconditionally for this platform and adds SMP mailbox/boot support when enabled.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: missing or stale object selection breaks platform boot; dependency is only Kconfig-driven build coverage.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sibyte/sb1250/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sibyte/sb1250/irq.c -->

# sources/distributed-fs/ceph-client/arch/mips/sibyte/sb1250/irq.c

Purpose: low-level SB1250 interrupt mapper setup, masking, affinity, acknowledge, and dispatch.

Important APIs/types/functions: `sb1250_mask_irq`, `sb1250_unmask_irq`, SMP `sb1250_set_affinity`, `ack_sb1250_irq`, `init_sb1250_irqs`, `arch_init_irq`, `plat_irq_dispatch`, and the `SB1250-IMR` irq_chip.

Control flow and state: boot maps all mapper interrupts to IP2, mailbox to IP3, masks everything except mailboxes, registers level handlers, and enables CP0 IP bits; dispatch prioritizes CPU perf counter, timer, SMP mailbox, then IMR status via `fls64`; affinity moves ownership by masking old CPU and unmasking new CPU under a raw spinlock; LDT acknowledge clears pending bits across CPUs and writes EOI.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: wrong mapper/IP programming can lose all board interrupts; affinity assumes valid online CPU mapping; LDT path depends on external `ldt_eoi_space`; high 64-bit register handling is delicate under o32 as noted in comments.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sibyte/sb1250/irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sibyte/sb1250/setup.c -->

# sources/distributed-fs/ceph-client/arch/mips/sibyte/sb1250/setup.c

Purpose: detects SB1250/BCM112x SoC type, revision, workaround level, bus clock, and platform setup details.

Important APIs/types/functions: `setup_bcm1250`, `setup_bcm112x`, `sys_rev_decode`, `sb1250_setup`, exported `soc_type`, `periph_rev`, `zbbus_mhz`, and `sb1250_m3_workaround_needed`.

Control flow and state: early setup reads SCD system revision, decodes pass strings and peripheral revisions, selects workaround pass flags, reports unsupported errata/config combinations, derives ZBbus MHz, and installs machine restart/halt/poweroff behavior through platform hooks.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: revision decoding must match silicon exactly; compile-time errata options can be unsafe for old passes; bus-frequency detection affects timers/profiling; boot can intentionally panic if required SB1 workarounds are absent.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sibyte/sb1250/setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sibyte/sb1250/smp.c -->

# sources/distributed-fs/ceph-client/arch/mips/sibyte/sb1250/smp.c

Purpose: SB1250 SMP operations using CFE CPU startup and IMR mailbox interrupts.

Important APIs/types/functions: `sb1250_smp_init`, `sb1250_send_ipi_single/mask`, `sb1250_init_secondary`, `sb1250_smp_finish`, `sb1250_boot_secondary`, `sb1250_prepare_cpus`, `sb1250_mailbox_interrupt`, and `plat_smp_ops` integration.

Control flow and state: setup records available CPUs, secondary boot calls `cfe_cpu_start` with `smp_bootstrap`, per-CPU finish enables timer/mailbox interrupts, IPIs write mailbox-set registers, and mailbox interrupt clears bits and dispatches scheduler/function-call actions.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: depends on CFE firmware, physical/logical CPU mapping, and mailbox register routing from IRQ setup; missed clear can retrigger IPIs; boot failure leaves CPUs offline.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sibyte/sb1250/smp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sibyte/sb1250/time.c -->

# sources/distributed-fs/ceph-client/arch/mips/sibyte/sb1250/time.c

Purpose: minimal SB1250 time initialization.

Important APIs/types/functions: `plat_time_init` sets `mips_hpt_frequency`.

Control flow and state: boot-time hook derives the MIPS high-precision timer frequency from `zbbus_mhz * 500000`.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: incorrect ZBbus frequency produces wrong scheduler clock/timer calibration.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sibyte/sb1250/time.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sibyte/swarm/Makefile -->

# sources/distributed-fs/ceph-client/arch/mips/sibyte/swarm/Makefile

Purpose: Kbuild list for SiByte SWARM board support.

Important APIs/types/functions: builds `platform.o`, `setup.o`, Xicor/M41T81 RTC support, and optionally `swarm-i2c.o`.

Control flow and state: object inclusion wires platform devices, board setup, persistent clock, and optional I2C board info into SWARM builds.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: wrong object set breaks board devices or RTC fallback paths.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sibyte/swarm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sibyte/swarm/platform.c -->

# sources/distributed-fs/ceph-client/arch/mips/sibyte/swarm/platform.c

Purpose: registers SWARM/LittleSur platform devices for PATA and SB1250 Ethernet MACs.

Important APIs/types/functions: `swarm_pata_init`, `sb1250_device_init`, `swarm_pata_device`, `sb1250_dev_struct` platform device templates.

Control flow and state: PATA init checks board IDE availability, reads GenBus chip-select mapping, computes command/control MMIO resources, and registers `pata_platform`; MAC init registers 2, 3, or 4 `sb1250-mac` devices based on `soc_type`.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: GenBus decoding must be correct or PATA maps the wrong bus region; device count depends on SoC type; resources are static and hardware-specific.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sibyte/swarm/platform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sibyte/swarm/rtc_m41t81.c -->

# sources/distributed-fs/ceph-client/arch/mips/sibyte/swarm/rtc_m41t81.c

Purpose: direct SMBus access driver helpers for the M41T81 RTC used as persistent clock.

Important APIs/types/functions: `m41t81_read`, `m41t81_write`, `m41t81_set_time`, `m41t81_get_time`, `m41t81_probe` plus BCD register definitions.

Control flow and state: read/write poll SMBus controller 1 busy/error bits, select RTC register addresses, and transfer bytes; set/get convert between `time64_t` and BCD fields, manage stop/century bits, and probe checks device presence.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: busy-wait loops have no timeout; raw SMBus access bypasses generic I2C locking; century/year handling must remain consistent; errors return sentinel values used by setup fallback logic.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sibyte/swarm/rtc_m41t81.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sibyte/swarm/rtc_xicor1241.c -->

# sources/distributed-fs/ceph-client/arch/mips/sibyte/swarm/rtc_xicor1241.c

Purpose: direct SMBus access helpers for Xicor X1241 RTC persistent clock.

Important APIs/types/functions: `xicor_read`, `xicor_write`, `xicor_set_time`, `xicor_get_time`, `xicor_probe` and X1241 CCR/SRAM register constants.

Control flow and state: helpers issue two-byte register-address SMBus transactions, convert BCD date/time values, handle status bits, and expose probe/get/set hooks used by board setup.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: same raw SMBus timeout/locking risks as M41T81; device selection and BCD conversions are board-specific; bad probe can select the wrong RTC implementation.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sibyte/swarm/rtc_xicor1241.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sibyte/swarm/setup.c -->

# sources/distributed-fs/ceph-client/arch/mips/sibyte/swarm/setup.c

Purpose: SWARM board setup for system type, bus-error handling, RTC persistent clock, memory setup, and LED writes.

Important APIs/types/functions: `get_system_type`, `swarm_be_handler`, `read_persistent_clock64`, `update_persistent_clock64`, `plat_mem_setup`, `setleds`.

Control flow and state: setup installs bus-error handler, selects Xicor or M41T81 clock through probe order, wires restart/halt/power hooks, declares board resources, and writes LED strings through board registers.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: RTC fallback depends on low-level probes; bus-error handling may hide or report platform errors differently; LED and board register writes assume SWARM-compatible hardware.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sibyte/swarm/setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sibyte/swarm/swarm-i2c.c -->

# sources/distributed-fs/ceph-client/arch/mips/sibyte/swarm/swarm-i2c.c

Purpose: I2C board-info registration for SWARM RTC devices.

Important APIs/types/functions: `swarm_i2c_info` with `m41t81` at address `0x68`; `swarm_i2c_init`.

Control flow and state: a late initcall registers board info on SMBus/I2C bus 1 so the generic I2C RTC driver can bind when enabled.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: must agree with hardware bus numbering and address; duplicates can conflict with direct RTC helpers.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sibyte/swarm/swarm-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sni/Makefile -->

# sources/distributed-fs/ceph-client/arch/mips/sni/Makefile

Purpose: Kbuild list for SNI RM platform support.

Important APIs/types/functions: `obj-y` adds IRQ, reset, setup, A20R, RM200, PCIMT, PCIT, time; `CONFIG_EISA` adds `eisa.o`.

Control flow and state: platform build always includes all SNI board variants and dispatches at runtime by `sni_brd_type`.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: build coverage must include optional EISA to catch root-device integration.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sni/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sni/a20r.c -->

# sources/distributed-fs/ceph-client/arch/mips/sni/a20r.c

Purpose: A20R-specific SNI board devices and interrupt controller handling.

Important APIs/types/functions: platform devices for 8250 serial, DS1216 RTC, 82596 Ethernet, 53c710 SCSI, SC2681 DUART; `a20r_update_cause_ip`, A20R irq_chip, `a20r_hwint`, `sni_a20r_irq_init`, `snirm_a20r_setup_devinit`.

Control flow and state: device init registers onboard resources for tower/minitower boards; IRQ init installs A20R handlers for board IRQs, uses CP0 status bits for mask/unmask, updates chipset cause state with inline assembly, and cascades ISA through the generic handler.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: inline assembly and magic addresses are fragile; shared ISA request can fail; platform resources are fixed physical addresses; only selected board types should register these devices.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sni/a20r.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sni/eisa.c -->

# sources/distributed-fs/ceph-client/arch/mips/sni/eisa.c

Purpose: virtual EISA root for SNI systems lacking a discoverable bridge.

Important APIs/types/functions: `eisa_root_dev`, `eisa_bus_root`, `sni_eisa_root_init`.

Control flow and state: registers a platform `eisa` device, attaches root data, and calls `eisa_root_register`; if a real bridge exists, it unregisters quietly.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: the return check appears suspicious because it returns immediately on successful platform-device registration before setting drvdata/registering EISA root; root probing depends on call ordering with real bridges.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sni/eisa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sni/irq.c -->

# sources/distributed-fs/ceph-client/arch/mips/sni/irq.c

Purpose: common SNI interrupt entry and board dispatch selection.

Important APIs/types/functions: `sni_hwint`, `plat_irq_dispatch`, `sni_isa_irq_handler`, `arch_init_irq`.

Control flow and state: the global dispatch hook calls the board-specific `sni_hwint`; ISA handler polls i8259 and forwards to `generic_handle_irq`; arch init initializes legacy i8259 and switches on `sni_brd_type` to initialize A20R, PCIT, PCIMT, or RM200 IRQs.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: if board detection fails, `sni_hwint` may be unset; ISA cascade depends on initialized i8259; board cases must stay synchronized with setup detection.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sni/irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sni/pcimt.c -->

# sources/distributed-fs/ceph-client/arch/mips/sni/pcimt.c

Purpose: PCIMT board setup, serial/CMOS resources, and interrupt demultiplexing.

Important APIs/types/functions: `sni_pcimt_detect`, `sni_pcimt_resource_init`, `enable_pcimt_irq`, `disable_pcimt_irq`, `pcimt_hwint0/1/3`, `sni_pcimt_hwint`, `sni_pcimt_irq_init`, `sni_pcimt_init`.

Control flow and state: detects PCIMT variant registers, initializes onboard resources, sets IRQ chips for chipset lines, demultiplexes CP0 pending bits into board IRQs and cascaded ISA, and registers serial/RTC/platform devices at device init.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: interrupt masks are board-register side effects; variant detection affects resource offsets; wrong CP0 pending priority can starve lower sources.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sni/pcimt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sni/pcit.c -->

# sources/distributed-fs/ceph-client/arch/mips/sni/pcit.c

Purpose: PCIT and PCIT-Cplus board setup, devices, and IRQ handling.

Important APIs/types/functions: 8250 resources for base/Cplus variants, CMOS resource, `sni_pcit_resource_init`, `enable_pcit_irq`, `disable_pcit_irq`, `pcit_hwint*`, `sni_pcit_irq_init`, `sni_pcit_cplus_irq_init`, `sni_pcit_init`.

Control flow and state: resource setup registers variant serial/RTC devices; IRQ setup configures chipset masks and board-specific demux routines; Cplus uses a different CP0 pending map than base PCIT.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: variant-specific IRQ maps and serial IRQs are easy to regress; fixed resources rely on board type detection; ISA cascade failure leaves legacy devices unusable.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sni/pcit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sni/reset.c -->

# sources/distributed-fs/ceph-client/arch/mips/sni/reset.c

Purpose: SNI restart and power-off hooks.

Important APIs/types/functions: `kb_wait`, `sni_machine_restart`, `sni_machine_power_off`.

Control flow and state: restart disables interrupts and repeatedly pulses the keyboard controller reset command; poweroff writes a control byte to `PCIMT_CSWCSM`.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: restart loops forever if reset does not occur; poweroff is PCIMT-specific magic MMIO and may not apply to every SNI variant.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sni/reset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sni/rm200.c -->

# sources/distributed-fs/ceph-client/arch/mips/sni/rm200.c

Purpose: RM200 board devices and two-layer interrupt handling including memory-mapped i8259A PICs.

Important APIs/types/functions: RM200 platform devices, `sni_rm200_*8259A*` mask/ack/poll/init helpers, RM200 irq_chip, `sni_rm200_hwint`, `sni_rm200_irq_init`, `sni_rm200_init`.

Control flow and state: device init registers serial, RTC, Ethernet, SCSI, and EISA root for RM200; IRQ init maps memory PICs, initializes master/slave i8259A, installs 16 PIC IRQs above base 32, then demultiplexes RM200 chipset status bits into onboard ISA, external ISA, and CPU timer/perf interrupts.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: memory-mapped PIC sequencing is order-sensitive; spurious IRQ handling is intentionally lightweight; ioremap failure partially disables PIC setup; fixed masks invert register semantics.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sni/rm200.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sni/setup.c -->

# sources/distributed-fs/ceph-client/arch/mips/sni/setup.c

Purpose: SNI platform setup and board detection from firmware/IDPROM.

Important APIs/types/functions: `sni_display_setup`, `sni_console_setup`, `sni_idprom_dump`, `plat_mem_setup`, Cirrus PCI RAM-size quirk, and machine hook assignment.

Control flow and state: boot reads firmware data, sets console/screen information, determines `sni_brd_type`, establishes memory/resource ranges, installs restart/power hooks, and applies PCI quirks for onboard graphics.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: firmware environment and IDPROM parsing are early-boot fragile; console fallback affects diagnostics; PCI quirk must target only affected Cirrus devices.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sni/setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sni/time.c -->

# sources/distributed-fs/ceph-client/arch/mips/sni/time.c

Purpose: SNI timer setup using A20R periodic timer or R4K count calibration.

Important APIs/types/functions: `a20r_set_periodic`, `a20r_interrupt`, `sni_a20r_timer_setup`, `dosample`, `plat_time_init`.

Control flow and state: A20R configures a clock event device and IRQ; other boards sample the R4K counter against a known delay loop to set `mips_hpt_frequency`; timer interrupt dispatches the registered clock event.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: calibration depends on stable delay/timer hardware; A20R periodic programming must match board IRQ setup; wrong frequency breaks timekeeping.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sni/time.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/tools/Makefile -->

# sources/distributed-fs/ceph-client/arch/mips/tools/Makefile

Purpose: Kbuild host-tool rules for MIPS build helpers.

Important APIs/types/functions: `hostprogs := elf-entry`; conditional `loongson3-llsc-check` for `CONFIG_CPU_LOONGSON3_WORKAROUNDS`.

Control flow and state: builds host utilities used during kernel image generation or validation.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: host endian/libc compatibility matters; helper failures block kernel build.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/tools/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/tools/elf-entry.c -->

# sources/distributed-fs/ceph-client/arch/mips/tools/elf-entry.c

Purpose: host utility that prints an ELF entry address as canonical 64-bit hex.

Important APIs/types/functions: `main`, `die`, ELF32/ELF64 header parsing, endian conversion fallbacks.

Control flow and state: opens an ELF file, reads enough header bytes, validates magic/class/data encoding, byte-swaps entry as needed, sign-extends ELF32 entry, and prints `0x%016PRIx64`.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: only reads the header and trusts class-specific layout; rejects unknown encodings; host endian macros vary by libc.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/tools/elf-entry.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/tools/generic-board-config.sh -->

# sources/distributed-fs/ceph-client/arch/mips/tools/generic-board-config.sh

Purpose: shell helper that merges generic MIPS board config fragments if their `# require` comments match a reference config.

Important APIs/types/functions: arguments `srctree objtree ref_cfg cfg boards_origin boards...`; requirement parser for `CONFIG_X=y/n`; `merge_config.sh` invocation.

Control flow and state: iterates requested boards, skips missing/unmet fragments, controls skip messages based on BOARDS origin, and merges accepted fragments into the output config.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: uses grep/cut/read shell parsing, so unusual requirement syntax is ignored; unquoted paths and board names should remain simple; failed merge_config propagates through the pipeline.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/tools/generic-board-config.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/tools/loongson3-llsc-check.c -->

# sources/distributed-fs/ceph-client/arch/mips/tools/loongson3-llsc-check.c

Purpose: host validator for Loongson3 LL/SC sequences in `vmlinux`.

Important APIs/types/functions: `is_ll`, `is_sc`, `is_sync`, `is_branch`, `check_ll`, `check_code`, `main` ELF section scan.

Control flow and state: maps vmlinux read-only, validates ELF64 little-endian MIPS sections, scans executable code for LL instructions, and enforces expected sync/branch/SC patterns used by Loongson3 workarounds.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: assumes instruction encoding and ELF layout; false positives can fail builds, false negatives weaken erratum protection; only active under relevant config.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/tools/loongson3-llsc-check.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/txx9/Kconfig -->

# sources/distributed-fs/ceph-client/arch/mips/txx9/Kconfig

Purpose: Kconfig options for Toshiba TXX9/TX49xx MIPS platforms.

Important APIs/types/functions: symbols `MACH_TX49XX`, `MACH_TXX9`, `TOSHIBA_RBTX4927`, `SOC_TX4927`, `SOC_TX4938`, `TOSHIBA_FPCIB0`, `PICMG_PCI_BACKPLANE_DEFAULT`, `PCI_TX4927`.

Control flow and state: select chains enable clocks, IRQ, PCI, GPIO, endian/kernel-width support, and board/SOC-specific code.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: incorrect selects can produce unbootable platform combinations; board symbol selects both TX4927 and TX4938 support for RBTX variants.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/txx9/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/txx9/Makefile -->

# sources/distributed-fs/ceph-client/arch/mips/txx9/Makefile

Purpose: Kbuild dispatcher for TXX9 platform folders.

Important APIs/types/functions: `obj-$(CONFIG_MACH_TX49XX) += generic/`; `obj-$(CONFIG_TOSHIBA_RBTX4927) += rbtx4927/`.

Control flow and state: adds generic SoC support and board support based on selected configs.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: missing folder inclusion breaks boot for selected boards.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/txx9/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/txx9/generic/Makefile -->

# sources/distributed-fs/ceph-client/arch/mips/txx9/generic/Makefile

Purpose: Kbuild list for TXX9 generic SoC support.

Important APIs/types/functions: always builds `setup.o`; PCI, TX4927, TX4938, and FPCIB0 add their specific objects.

Control flow and state: selects memory, setup, IRQ, PCI, and Super I/O helpers based on SoC/features.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: shared `mem_tx4927.o` serves TX4938 too; config coverage should include both SoCs.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/txx9/generic/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/txx9/generic/irq_tx4927.c -->

# sources/distributed-fs/ceph-client/arch/mips/txx9/generic/irq_tx4927.c

Purpose: TX4927 interrupt-controller initialization wrapper.

Important APIs/types/functions: `tx4927_irq_init` calls the generic TXX9 IRQ init with TX4927 register base and interrupt count.

Control flow and state: early board IRQ setup installs the SoC interrupt controller before board cascades/devices are enabled.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: wrong base/count breaks all SoC interrupts.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/txx9/generic/irq_tx4927.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/txx9/generic/irq_tx4938.c -->

# sources/distributed-fs/ceph-client/arch/mips/txx9/generic/irq_tx4938.c

Purpose: TX4938 interrupt-controller initialization wrapper.

Important APIs/types/functions: `tx4938_irq_init` for TX4938 register base/count.

Control flow and state: same pattern as TX4927 but targeting TX4938 register layout.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: SoC revision/register mismatch loses interrupts.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/txx9/generic/irq_tx4938.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/txx9/generic/mem_tx4927.c -->

# sources/distributed-fs/ceph-client/arch/mips/txx9/generic/mem_tx4927.c

Purpose: TX4927/TX4938 SDRAM size discovery from controller registers.

Important APIs/types/functions: `tx4927_process_sdccr`, `tx4927_get_mem_size`.

Control flow and state: reads SDCCR values, decodes row/column/bank width, computes size per memory channel, and returns total memory detected by hardware.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: decode assumes controller register format; bad values can under/over-report RAM and corrupt boot memory setup.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/txx9/generic/mem_tx4927.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/txx9/generic/pci.c -->

# sources/distributed-fs/ceph-client/arch/mips/txx9/generic/pci.c

Purpose: generic TXX9 PCI resource allocation, bridge quirks, IRQ mapping hook, and boot-option parser.

Important APIs/types/functions: `txx9_pci66_check`, `txx9_alloc_pci_controller`, `txx9_pcibios_setup`, `pcibios_map_irq`, SLC90E66 and TC35815 fixups, BIST final fixup.

Control flow and state: allocates PCI MEM/MMIO/IO windows, sets MIPS I/O base, registers arch init, probes 66MHz capability, configures ISA bridge cascade/Super I/O when enabled, applies device fixups, and parses `pci=` options such as `picmg`, `clk=`, and `err=`.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: resource allocation can fail depending on physical map; global IRQ map callback must be initialized; final BIST on every device may expose slow/broken hardware; bridge quirks are device-ID specific.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/txx9/generic/pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/txx9/generic/setup.c -->

# sources/distributed-fs/ceph-client/arch/mips/txx9/generic/setup.c

Purpose: central TXX9 generic platform framework for board selection, early setup, clocks, devices, IRQ/time wrappers, GPIO LEDs, DMA, SRAM sysfs, and helper registration.

Important APIs/types/functions: `prom_init`, `plat_mem_setup`, `arch_init_irq`, `plat_time_init`, `plat_irq_dispatch`, `txx9_reg_res_init`, `txx9_wdt_init/now`, `txx9_spi_init`, `txx9_ethaddr_init`, `txx9_sio_init`, `txx9_physmap_flash_init`, `txx9_ndfmc_init`, `txx9_iocled_init`, `txx9_dmac_init`, `txx9_sramc_init`.

Control flow and state: boot parses firmware args/env for board and clocks, selects a `txx9_board_vec`, applies cache options, installs machine hooks, delegates board memory/IRQ/time/device init, registers fixed clocks, and creates platform devices/sysfs views for SoC peripherals.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: very broad integration surface; command-line parsing mutates `arcs_cmdline`; cache disable options can hurt or save broken hardware; SRAM sysfs exposes raw memory writes to root.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/txx9/generic/setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/txx9/generic/setup_tx4927.c -->

# sources/distributed-fs/ceph-client/arch/mips/txx9/generic/setup_tx4927.c

Purpose: TX4927 SoC setup for clocks, reset/watchdog, bus-error handling, timers, serial, MTD, DMA, and unused-module gating.

Important APIs/types/functions: `tx4927_setup`, `tx4927_wdt_init`, `tx4927_time_init`, `tx4927_sio_init`, `tx4927_mtd_init`, `tx4927_dmac_init`, `tx4927_stop_unused_modules`, `tx4927_late_init`.

Control flow and state: reads CC/clock registers, initializes resource windows, installs bus-error handler, computes CPU/GBUS clocks, initializes timers/SIO/flash/DMA, and disables unused modules late.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: clock/reset register decoding must match silicon; stopping modules can break boards that forgot to register users; watchdog restart is destructive by design.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/txx9/generic/setup_tx4927.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/txx9/generic/setup_tx4938.c -->

# sources/distributed-fs/ceph-client/arch/mips/txx9/generic/setup_tx4938.c

Purpose: TX4938 SoC setup analogous to TX4927 with TX4938-specific clocks, reset, timers, serial, PCI/MTD/DMA helpers, and module gating.

Important APIs/types/functions: `tx4938_setup`, `tx4938_wdt_init`, `tx4938_time_init`, `tx4938_sio_init`, `tx4938_mtd_init`, `tx4938_dmac_init`, `tx4938_stop_unused_modules`, `tx4938_late_init`.

Control flow and state: initializes TX4938 internal resources and clocks, sets bus-error handling, exports helper init routines to board code, and trims unused peripherals.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: same SoC-register risks as TX4927 plus PCI/clock differences; board code must call helpers with matching channel/IRQ values.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/txx9/generic/setup_tx4938.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/txx9/generic/smsc_fdc37m81x.c -->

# sources/distributed-fs/ceph-client/arch/mips/txx9/generic/smsc_fdc37m81x.c

Purpose: SMSC FDC37M81x Super I/O configuration helper for TXX9 boards.

Important APIs/types/functions: `smsc_fdc37m81x_init`, config begin/end, get/set helpers, logical-device selection constants.

Control flow and state: enters Super I/O config mode through index/data ports, selects logical devices, writes register values, and exits config mode for keyboard/floppy/serial setup by PCI bridge quirks.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: port access assumes legacy Super I/O at configured base; missing locking around config mode; wrong logical device/register writes can disable console/input.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/txx9/generic/smsc_fdc37m81x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/txx9/rbtx4927/Makefile -->

# sources/distributed-fs/ceph-client/arch/mips/txx9/rbtx4927/Makefile

Purpose: Kbuild list for Toshiba RBTX4927 board support.

Important APIs/types/functions: `obj-y += setup.o irq.o prom.o`.

Control flow and state: includes board setup, IRQ routing, and PROM init in RBTX builds.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: small but essential object list.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/txx9/rbtx4927/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/txx9/rbtx4927/irq.c -->

# sources/distributed-fs/ceph-client/arch/mips/txx9/rbtx4927/irq.c

Purpose: RBTX4927 board-level IRQ routing and dispatch.

Important APIs/types/functions: board irq setup helpers, PCI/IOC interrupt mapping, `toshiba_rbtx4927_irq_setup`, dispatch callback for TXX9 core.

Control flow and state: initializes SoC IRQs, board external interrupt controller/GPIO lines, PCI IRQ mapping, and returns IRQ numbers to generic `plat_irq_dispatch` through `txx9_irq_dispatch`.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: board wiring tables must match RBTX4927/RBTX4937 variants; PCI slot/pin routing errors break devices.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/txx9/rbtx4927/irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/txx9/rbtx4927/prom.c -->

# sources/distributed-fs/ceph-client/arch/mips/txx9/rbtx4927/prom.c

Purpose: RBTX4927 PROM initialization glue.

Important APIs/types/functions: `rbtx4927_prom_init`.

Control flow and state: sets initial board vector state and firmware-derived data before generic TXX9 setup continues.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: depends on firmware argument layout and selected board vector.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/txx9/rbtx4927/prom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/txx9/rbtx4927/setup.c -->

# sources/distributed-fs/ceph-client/arch/mips/txx9/rbtx4927/setup.c

Purpose: RBTX4927/RBTX4937 board setup for PCI, GPIO, restart, memory, clocks, RTC, Ethernet, flash, LEDs, and platform devices.

Important APIs/types/functions: `tx4927_pci_setup`, `tx4937_pci_setup`, `rbtx4927_gpio_init`, `rbtx4927_arch_init`, `toshiba_rbtx4927_restart`, `rbtx4927_mem_setup`, clock/time/RTC/NE/MTD/GPIO LED/device init helpers, board vectors.

Control flow and state: board vector delegates from generic TXX9 setup to initialize board-specific clocks, memory size, PCI windows and IRQ map, RTC platform device, network and flash resources, and GPIO LEDs.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: variant differences are numerous; PCI clock auto-detection can change bus timing; restart uses watchdog/reset registers; fixed flash/network resources must match board straps.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/txx9/rbtx4927/setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/vdso/Kconfig -->

# sources/distributed-fs/ceph-client/arch/mips/vdso/Kconfig

Purpose: Kconfig switch to disable MIPS vDSO time implementation.

Important APIs/types/functions: `MIPS_DISABLE_VDSO`.

Control flow and state: when enabled, the vDSO Makefile removes `vgettimeofday.o` from the vDSO image.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: disabling changes userspace syscall/vDSO performance and ABI exposure.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/vdso/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/vdso/Makefile -->

# sources/distributed-fs/ceph-client/arch/mips/vdso/Makefile

Purpose: MIPS vDSO build rules for native, O32, and N32 images.

Important APIs/types/functions: object lists `elf.o vgettimeofday.o sigreturn.o`, `genvdso` host tool, ABI-specific object/link/image rules, vDSO checks for generic validity and `jalr t9` PIC calls.

Control flow and state: builds raw debug and stripped shared objects with restricted PIC flags, copies raw outputs, runs `genvdso` to emit kernel C images, and conditionally builds O32/N32 variants with `config-n32-o32-env.c` include.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: compiler/linker flags are ABI-sensitive; unsupported PIC calls are fatal; generated debug artifacts have a FIXME install path; disabling vDSO time changes object list.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/vdso/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/vdso/config-n32-o32-env.c -->

# sources/distributed-fs/ceph-client/arch/mips/vdso/config-n32-o32-env.c

Purpose: include shim for building O32/N32 vDSO C code in a 64-bit kernel environment.

Important APIs/types/functions: preprocessor definitions and includes that adjust types/ABI expectations before generic vDSO gettimeofday code.

Control flow and state: used only via Makefile `-include` for O32/N32 `vgettimeofday` builds.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: must precede generic library includes; subtle type-size mismatches break userspace ABI.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/vdso/config-n32-o32-env.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/vdso/elf.S -->

# sources/distributed-fs/ceph-client/arch/mips/vdso/elf.S

Purpose: assembly note data for MIPS vDSO ELF metadata.

Important APIs/types/functions: `ELFNOTE_START/END`, `.MIPS.abiflags`, `.gnu.attributes` fields.

Control flow and state: contributes ABI flags and GNU attributes sections later patched by `genvdso` to correct section names/types.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: metadata must match ABI/build flags or loaders/debuggers may misinterpret vDSO.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/vdso/elf.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/vdso/genvdso.c -->

# sources/distributed-fs/ceph-client/arch/mips/vdso/genvdso.c

Purpose: host generator that validates, patches, and converts MIPS vDSO shared objects into kernel-embedded C images.

Important APIs/types/functions: `map_vdso`, `patch_vdso32/64`, `get_symbols32/64` from `genvdso.h`, symbol table for sigreturn offsets, and `main`.

Control flow and state: maps stripped and debug vDSOs writable, validates ELF magic/class/endian/MIPS/ET_DYN, patches ABI/attribute sections, extracts required symbol offsets, msyncs debug image, and writes `vdso_image_data` plus `mips_vdso_image` structure.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: host/target endian handling is critical; missing symbols fail generation; writable mmap modifies build artifacts; section patching depends on assembler/linker output shape.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/vdso/genvdso.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/vdso/genvdso.h -->

# sources/distributed-fs/ceph-client/arch/mips/vdso/genvdso.h

Purpose: template header included twice by `genvdso.c` to specialize ELF32 and ELF64 patch/symbol routines.

Important APIs/types/functions: `FUNC(patch_vdso)`, `FUNC(get_symbols)`, section header/string/symbol scanning, ABI flag interpretation.

Control flow and state: compiled with `ELF_BITS` set to 64 then 32; locates special MIPS sections, updates section names/types, determines ABI mask, and finds symbol values for ABI-required vDSO symbols.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: template macro expansion is hard to audit; section/name assumptions must track linker script and `elf.S`; wrong ABI mask omits required symbols.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/vdso/genvdso.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/vdso/sigreturn.S -->

# sources/distributed-fs/ceph-client/arch/mips/vdso/sigreturn.S

Purpose: MIPS vDSO signal-return trampolines.

Important APIs/types/functions: `__vdso_rt_sigreturn`, `__vdso_sigreturn` leaf functions.

Control flow and state: loads the appropriate syscall number and executes `syscall` for rt/non-rt signal return entries exported to userspace.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: ABI availability differs: plain sigreturn is O32-only in generator symbol table; instruction sequence must match kernel signal ABI.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/vdso/sigreturn.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/vdso/vdso.lds.S -->

# sources/distributed-fs/ceph-client/arch/mips/vdso/vdso.lds.S

Purpose: linker script for MIPS vDSO shared objects.

Important APIs/types/functions: ABI-dependent `OUTPUT_FORMAT`, `OUTPUT_ARCH`, section layout for notes, dynsym/dynstr, text, eh_frame, dynamic, rodata, versioning, and discard rules.

Control flow and state: defines a compact ET_DYN image layout consumed by the Makefile and `genvdso`.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: section names must align with `genvdso` patching and generic vDSO validation; ABI output format preprocessor branches are critical.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/vdso/vdso.lds.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/vdso/vgettimeofday.c -->

# sources/distributed-fs/ceph-client/arch/mips/vdso/vgettimeofday.c

Purpose: MIPS vDSO time entry wrapper.

Important APIs/types/functions: `__vdso_clock_getres_time64` and generic vDSO gettimeofday include integration.

Control flow and state: delegates clock-getres behavior to generic vDSO data where supported; compiled into native/O32/N32 images unless disabled.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: time ABI types differ by ABI; correctness depends on vvar data and generic lib/vdso implementation.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/vdso/vgettimeofday.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/Kbuild -->

# sources/distributed-fs/ceph-client/arch/nios2/Kbuild

Purpose: top-level Nios II Kbuild directory selection.

Important APIs/types/functions: `obj-y += kernel/ mm/ platform/`.

Control flow and state: includes architecture kernel, MM, and platform directories.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: missing directory inclusion breaks the port.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/Kconfig -->

# sources/distributed-fs/ceph-client/arch/nios2/Kconfig

Purpose: Nios II architecture Kconfig root.

Important APIs/types/functions: root `NIOS2` symbol selects core architecture capabilities; options for checksum/hweight/calibrate delay, FPU disabled, MMU, alignment trap, command line handling, boot link offset, and advanced virtual-region bases.

Control flow and state: configuration drives compiler flags, boot arguments, memory map constants, and platform Kconfig inclusion.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: advanced region bases and command-line precedence can easily produce nonbooting kernels; alignment trap has performance cost.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/Makefile -->

# sources/distributed-fs/ceph-client/arch/nios2/Makefile

Purpose: Nios II architecture Makefile for compiler flags, libgcc, boot targets, and install/help rules.

Important APIs/types/functions: `KBUILD_DEFCONFIG`, exported `MMU`, `LIBGCC`, `KBUILD_AFLAGS/CFLAGS`, `KBUILD_IMAGE`, `BOOT_TARGETS`, `install`.

Control flow and state: sets CPU revision and optional instruction flags, disables builtins/sibling calls, links arch lib plus libgcc, and delegates `vmImage`/boot target generation to `arch/nios2/boot`.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: compiler must support selected Nios II options; libgcc path is toolchain-dependent; boot image target names must match boot Makefile.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/boot/Makefile -->

# sources/distributed-fs/ceph-client/arch/nios2/boot/Makefile

Purpose: Nios II boot image Makefile.

Important APIs/types/functions: `vmlinux.bin`, `vmlinux.gz`, `vmImage`, `zImage`, compressed `vmlinux` rules and U-Boot load/entry addresses from `nm`.

Control flow and state: objcopy creates binary, gzip compresses it, U-Boot wrapper creates `vmImage`, and compressed build links self-extracting `zImage`.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: entry/load address extraction relies on symbol names; compressed and U-Boot targets require tool availability.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/boot/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/boot/compressed/Makefile -->

# sources/distributed-fs/ceph-client/arch/nios2/boot/compressed/Makefile

Purpose: Nios II compressed boot Kbuild.

Important APIs/types/functions: targets `vmlinux`, `head.o`, `misc.o`, `piggy.o`, linker script; `OBJECTS` head/misc.

Control flow and state: links decompressor head/misc with piggybacked gzip data using `vmlinux.lds`.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: link addresses must match boot Kconfig; missing piggy source blocks zImage.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/boot/compressed/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/boot/compressed/console.c -->

# sources/distributed-fs/ceph-client/arch/nios2/boot/compressed/console.c

Purpose: early decompressor console for Nios II.

Important APIs/types/functions: `my_ioremap`, JTAG UART or Altera UART `putchar`, `console_init`, `puts` variants selected by config/base macros.

Control flow and state: maps UART registers through uncached kernel region and emits characters during decompression when a supported console is configured; otherwise stubs output.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: polling register loops can hang if base/config is wrong; early I/O mappings rely on region constants before full MMU setup.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/boot/compressed/console.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/boot/compressed/head.S -->

# sources/distributed-fs/ceph-client/arch/nios2/boot/compressed/head.S

Purpose: Nios II compressed boot entry assembly.

Important APIs/types/functions: `_start` relocation, cache init/flush, BSS clear, argument save/restore, stack setup, and `decompress_kernel` call.

Control flow and state: starts at linked decompressor image, invalidates/flushes caches, relocates if needed, clears BSS, preserves boot arguments, calls C decompressor, flushes caches again, and jumps to decompressed kernel address.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: wrong cache or relocation constants corrupt boot; register preservation is bootloader ABI-sensitive.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/boot/compressed/head.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/boot/compressed/misc.c -->

# sources/distributed-fs/ceph-client/arch/nios2/boot/compressed/misc.c

Purpose: Nios II gzip decompressor C support.

Important APIs/types/functions: `memset`, `memcpy`, `fill_inbuf`, `flush_window`, `error`, `decompress_kernel`, included inflate implementation.

Control flow and state: sets input/output buffers from linker symbols and configured memory base, inflates kernel data, optionally prints progress/errors, and returns to assembly jump path.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: minimal libc replacements must be correct; output address must not overlap decompressor/piggy data incorrectly.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/boot/compressed/misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/boot/compressed/vmlinux.lds.S -->

# sources/distributed-fs/ceph-client/arch/nios2/boot/compressed/vmlinux.lds.S

Purpose: linker script for Nios II compressed boot image.

Important APIs/types/functions: `OUTPUT_FORMAT`, `OUTPUT_ARCH`, `ENTRY(_start)`, text/rodata/data/got/bss layout and image symbols.

Control flow and state: places decompressor at configured boot link offset and emits symbols consumed by head/misc for relocation, BSS, and piggy data.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: link address and section symbols are boot-critical; GOT/data placement must remain compatible with early assembly.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/boot/compressed/vmlinux.lds.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/boot/dts/Makefile -->

# sources/distributed-fs/ceph-client/arch/nios2/boot/dts/Makefile

Purpose: Nios II device-tree build rules.

Important APIs/types/functions: `dtb-y` from `CONFIG_BUILTIN_DTB_NAME`; optional all-DTB glob for `CONFIG_OF_ALL_DTBS`.

Control flow and state: selects built-in or all available DTBs for the architecture boot build.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: configuration must name an existing DTS; glob behavior can change build size.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/boot/dts/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/boot/install.sh -->

# sources/distributed-fs/ceph-client/arch/nios2/boot/install.sh

Purpose: Nios II install helper.

Important APIs/types/functions: shell variables for `KERNELRELEASE`, `KBUILD_IMAGE`, `INSTALL_PATH`, and `INSTALLKERNEL` lookup.

Control flow and state: copies or delegates installation of the built kernel image using distro/user installkernel conventions.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: host install path/tool differences; script is packaging-time only.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/boot/install.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/Kbuild -->

# sources/distributed-fs/ceph-client/arch/nios2/include/asm/Kbuild

Purpose: Nios II asm header Kbuild export list.

Important APIs/types/functions: generic header mappings and generated header declarations.

Control flow and state: controls which asm headers are generated/exported to UAPI or generic fallbacks.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: header list drift can break userspace or internal includes.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/asm-macros.h -->

# sources/distributed-fs/ceph-client/arch/nios2/include/asm/asm-macros.h

Purpose: Nios II assembler convenience macros.

Important APIs/types/functions: `ANDI32`, `ORI32`, `XORI32`, bit-test/set/clear/branch macros, `PUSH`, `POP`.

Control flow and state: macros choose compact immediate sequences for 32-bit masks and provide reusable stack/bit operations for low-level assembly.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: some comments note register alias constraints; `BTR` high-half path appears suspicious using `%lo` with `andhi`, so assembler coverage matters.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/asm-macros.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/asm-offsets.h -->

# sources/distributed-fs/ceph-client/arch/nios2/include/asm/asm-offsets.h

Purpose: Nios II asm offsets include wrapper.

Important APIs/types/functions: includes/generated offsets contract for assembly.

Control flow and state: provides assembly-visible structure offsets generated elsewhere.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: stale generated offsets break entry/context code.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/asm-offsets.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/cache.h -->

# sources/distributed-fs/ceph-client/arch/nios2/include/asm/cache.h

Purpose: Nios II cache constants.

Important APIs/types/functions: cache line and architecture cache definitions.

Control flow and state: provides constants used by cacheflush and low-level code.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: must match CPU cache configuration.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/cacheflush.h -->

# sources/distributed-fs/ceph-client/arch/nios2/include/asm/cacheflush.h

Purpose: Nios II cache flush API declarations and page-cache clean flag.

Important APIs/types/functions: `PG_dcache_clean`, `flush_cache_*`, `flush_dcache_page/folio`, `flush_icache_range/pages`, vmap/vunmap flush macros.

Control flow and state: declares architecture cache maintenance hooks used by MM, exec, DMA, and mapping code; maps vmap flushes to dcache range flushes.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: aliasing-cache correctness depends on implementations in arch MM code; wrong clean flag handling causes stale instruction/data views.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/cacheflush.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/cachetype.h -->

# sources/distributed-fs/ceph-client/arch/nios2/include/asm/cachetype.h

Purpose: Nios II cache type helpers.

Important APIs/types/functions: small header describing cache type support/placeholder behavior.

Control flow and state: used by generic code that queries cache topology/type.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: minimal implementation must still satisfy generic include expectations.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/cachetype.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/checksum.h -->

# sources/distributed-fs/ceph-client/arch/nios2/include/asm/checksum.h

Purpose: Nios II checksum helpers.

Important APIs/types/functions: `csum_fold`, `csum_tcpudp_nofold`, aliases to generic checksum routines where appropriate, inline assembly carry folding.

Control flow and state: implements fast pseudo-header and fold operations for networking checksums using Nios II arithmetic/carry behavior.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: inline assembly constraints and endian assumptions are correctness-critical; network checksum tests are useful regression signals.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/checksum.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/cpuinfo.h -->

# sources/distributed-fs/ceph-client/arch/nios2/include/asm/cpuinfo.h

Purpose: Nios II CPU information definitions.

Important APIs/types/functions: `struct cpuinfo`, per-CPU CPU data declarations, cache/MMU feature fields.

Control flow and state: shares detected CPU/cache/TLB capability data between setup, procfs, and low-level code.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: fields must align with detection code and compiler feature flags.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/cpuinfo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/delay.h -->

# sources/distributed-fs/ceph-client/arch/nios2/include/asm/delay.h

Purpose: Nios II delay calibration interface.

Important APIs/types/functions: `__delay`, `udelay`, `ndelay`, `loops_per_jiffy` integration macros or declarations.

Control flow and state: connects generic delay users to architecture calibrated loops.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: bad calibration affects drivers and boot timing.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/delay.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/elf.h -->

# sources/distributed-fs/ceph-client/arch/nios2/include/asm/elf.h

Purpose: Nios II ELF ABI definitions.

Important APIs/types/functions: ELF class/data/machine, core dump register sets, `elf_check_arch`, `ELF_PLAT_INIT`, relocation/module ABI constants.

Control flow and state: defines how Linux recognizes and initializes Nios II ELF binaries and core dumps.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: ABI constants must match toolchain and userspace; wrong register initialization breaks exec.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/elf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/entry.h -->

# sources/distributed-fs/ceph-client/arch/nios2/include/asm/entry.h

Purpose: Nios II assembly entry save/restore macros.

Important APIs/types/functions: macros to save/restore trap frame registers and switch-stack callee-saved registers using `PT_*`/`SW_*` offsets.

Control flow and state: entry code uses these macros to capture user SP/status/EA, preserve registers on exceptions/syscalls, and restore before return.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: offsets must match generated asm offsets; restore order and SP handling are exception-return critical.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/entry.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/io.h -->

# sources/distributed-fs/ceph-client/arch/nios2/include/asm/io.h

Purpose: Nios II I/O address translation helpers.

Important APIs/types/functions: `virt_to_phys`, `phys_to_virt`, `ioremap`/ioport constraints via region-base masking.

Control flow and state: maps physical and virtual addresses using configured kernel/IO region base bits for early and normal MMIO access.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: custom region bases from Kconfig must be coherent; no-I/O-port architecture means generic port assumptions fail.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/irq.h -->

# sources/distributed-fs/ceph-client/arch/nios2/include/asm/irq.h

Purpose: Nios II IRQ constants/header glue.

Important APIs/types/functions: architecture IRQ definitions such as `NR_IRQS` or include contracts for irqdomain-based sparse IRQ.

Control flow and state: provides minimal arch IRQ interface to generic interrupt code.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: must match platform interrupt controller configuration.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/irqflags.h -->

# sources/distributed-fs/ceph-client/arch/nios2/include/asm/irqflags.h

Purpose: Nios II local IRQ flag primitives.

Important APIs/types/functions: `arch_local_save_flags`, `arch_local_irq_restore`, `arch_local_irq_disable`, `arch_local_irq_enable`, `arch_irqs_disabled_flags`, `arch_local_irq_save`.

Control flow and state: uses Nios II control-register reads/writes for status/PIE bits to save, restore, disable, and enable local interrupts.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: control-register hazards and exact status-bit masks are critical; bugs manifest as lost interrupts or unsafe critical sections.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/irqflags.h -->
