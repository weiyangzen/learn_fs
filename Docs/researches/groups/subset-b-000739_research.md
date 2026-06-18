# subset-b-000739 research

Grouped research for SGI SN, Siemens-Nixdorf, MIPS SMP/signal, and Broadcom SiByte architecture headers. Each section is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/sb1250_scd.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/sb1250_scd.h

Purpose: Defines the Broadcom SiByte SB1250/BCM112x/BCM1480 System Control and Debug register bit layout used by early platform setup, clock/reset handling, watchdog/timer code, performance counters, bus error reporting, address traps, and trace-buffer programming.

Important APIs/types/functions: `M_SYS_*`, `S_SYS_*`, `V_SYS_*`, and `G_SYS_*` macros for system revision, part, SOC type, manufacturing, and system configuration fields; revision constants such as `K_SYS_REVISION_BCM1250_C0`; `SYS_SOC_TYPE`; watchdog and timer constants `V_SCD_WDOG_FREQ`, `M_SCD_WDOG_*`, `V_SCD_TIMER_FREQ`, `M_SCD_TIMER_*`; bus/ECC fields `S_SCD_BERR_*`, `S_SCD_L2ECC_*`, `S_SCD_MEM_ECC_*`; address trap fields `M_ATRAP_*`; trace controls `M_SCD_TRACE_CFG_*`, `V_SCD_TREVT_*`, and `V_SCD_TRSEQ_*`.

Control flow: There is no executable control flow apart from macro expressions. Callers read memory-mapped SCD registers, decode fields through the `G_` macros, compose register writes through the `V_` and `M_` macros, and branch on revision/SOC constants. `SYS_SOC_TYPE` has both assembler and C forms and normalizes alternate BCM1250 encodings back to the canonical BCM1250 SOC type.

State and persistence: The file names persistent hardware state rather than owning software state: reset bits, watchdog and timer enable/count values, performance counter source/enable bits, captured bus/ECC error fields, and trace-buffer configuration. Writes through these masks can reset CPUs, trigger soft or system reset, enable watchdog reset behavior, clear trace buffers, or alter diagnostic capture.

Dependencies and integration points: Depends on `asm/sibyte/sb1250_defs.h` for `_SB_MAKE64`, `_SB_MAKEMASK`, `_SB_MAKEVALUE`, and feature-selection macros. Integrated by SiByte board setup, timer, watchdog, interrupt, performance, and low-level debug code that already knows the SCD register addresses.

Risks: Register programming is hardware destructive if masks are applied to the wrong revision; several fields are conditional on `SIBYTE_HDR_FEATURE*`. The header also carries legacy quirks, including duplicate `M_ATRAP_INDEX` and a likely typo in `G_SCD_TREVT_DATAID` referencing `M_SCD_TREVT_DATID`, so build coverage is important when touching trace definitions.

Test signals: Useful signals are MIPS SiByte build coverage, boot on SB1250/BCM112x hardware or emulator, timer/watchdog interrupt tests, reset-path smoke tests, and any diagnostics that read SCD bus/ECC/trace registers.

Source read size: 641 lines, 24159 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/sb1250_scd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/sb1250_smbus.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/sb1250_smbus.h

Purpose: Provides bit definitions for the SiByte SMBus controller, covering bus clock setup, command/start formatting, direct line control, interrupt/status bits, data registers, packet-error-check fields, and extended transfer formats.

Important APIs/types/functions: `S_SMB_FREQ_DIV`, `V_SMB_FREQ_DIV`, frequency constants `K_SMB_FREQ_400KHZ`, `K_SMB_FREQ_100KHZ`, `K_SMB_FREQ_10KHZ`; control/status flags `M_SMB_ERR_INTR`, `M_SMB_FINISH_INTR`, `M_SMB_BUSY`, `M_SMB_ERROR`; transaction fields `V_SMB_ADDR`, `V_SMB_TT_*`, `M_SMB_PEC`; data fields `V_SMB_LB`, `V_SMB_MB`; extended-format fields `V_SMB_DFMT_*`, `V_SMB_AFMT_*`, and `M_SMB_DIR`.

Control flow: The header encodes the caller sequence for a transaction: set clock divisor, optionally drive/directly sample the lines, program command/address/data/extra registers, select a transaction type, start the transfer, then poll or handle finish/error status.

State and persistence: Hardware state is in the SMBus controller registers and external bus lines. The macros expose interrupt enable state, busy/error latches, SCL/SDA input samples, queued data, packet error check bytes, and multi-byte command/address layout.

Dependencies and integration points: Depends on `sb1250_defs.h` for bitfield helpers and feature predicates. Integrated by the SiByte I2C/SMBus platform driver and board code that accesses EEPROMs, RTCs, sensors, and other board-management devices.

Risks: Clock divisor assumptions are tied to the controller input clock. Extended transfer and SCL input fields are feature-gated by chip revision. `V_SPEC_MB` appears to build the PEC field despite the name mismatch, so renames must preserve compatibility.

Test signals: Signals include compile coverage for SiByte I2C code, SMBus probe/read/write tests against board EEPROM/RTC devices, interrupt completion/error tests, and bus recovery tests for busy/error conditions.

Source read size: 191 lines, 6365 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/sb1250_smbus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/sb1250_syncser.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/sb1250_syncser.h

Purpose: Defines control, clocking, DMA, status, and sequencer-table bits for the SB1250 synchronous serial block, including HDLC/CRC-oriented operation.

Important APIs/types/functions: Mode flags `M_SYNCSER_CRC_MODE`, `M_SYNCSER_MSB_FIRST`, `V_SYNCSER_FLAG_NUM`, `M_SYNCSER_HDLC_EN`, loopback flags; clock/interface flags `M_SYNCSER_RXCLK_EXT`, `V_SYNCSER_RXSYNC_DLY`, `M_SYNCSER_TXCLK_EXT`; command bits `M_SYNCSER_CMD_RX_EN`, `M_SYNCSER_CMD_TX_EN`, reset and pause bits; DMA bits `M_SYNCSER_DMA_RX_EN`, `M_SYNCSER_DMA_TX_EN`; status bits for CRC, abort, overrun, sync, descriptor, high/low-watermark, and sequencer-entry macros.

Control flow: Drivers use the masks to configure framing and line timing, reset RX/TX engines, enable command and DMA paths, and react to status interrupts. Sequencer entries describe byte/strobe/count/last behavior for programmed serial waveforms.

State and persistence: State lives in device registers, DMA descriptors, watermarks, and sequencer table entries. The header does not allocate state but exposes flags that enable DMA engines, clear or reset FIFOs, and report underrun/overrun and frame-boundary conditions.

Dependencies and integration points: Depends on `sb1250_defs.h`. It integrates with platform serial or WAN-style drivers that own register base addresses and DMA descriptor management.

Risks: Incorrect clock polarity, sync delay, or byte-order flags can make line protocols silently fail. RX/TX reset and DMA-enable bits interact with descriptor ownership, so ordering errors may lose frames. `V_SYNCSER_FLAG_NUM` omits an `(x)` parameter in the macro body definition, a legacy typo that can break new use.

Test signals: Compile coverage plus loopback, DMA RX/TX, CRC-error, abort, underrun/overrun, and sequencer waveform tests are the useful signals.

Source read size: 133 lines, 4482 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/sb1250_syncser.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/sb1250_uart.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/sb1250_uart.h

Purpose: Defines SB1250 dual-UART register fields for character format, parity, flow control, commands, status, baud-rate programming, input/output pins, interrupts, masks, and full-interrupt timing.

Important APIs/types/functions: Mode macros `V_DUART_BITS_PER_CHAR_*`, `V_DUART_PARITY_MODE_*`, stop-bit and channel-mode flags; command macros `M_DUART_RX_EN`, `M_DUART_TX_EN`, `V_DUART_MISC_CMD_*`; status bits `M_DUART_RX_RDY`, `M_DUART_TX_RDY`, error bits; baud helper `V_DUART_BAUD_RATE`; data masks; input/output pin and change bits; per-channel and combined interrupt status/mask macros; `M_DUART_OUT_PIN_SET/CLR(chan)` and full interrupt control fields.

Control flow: UART code composes mode registers, enables RX/TX, uses `V_DUART_BAUD_RATE` for the divisor, polls status or services interrupts, transfers data through hold registers, and manipulates modem/board pins through output-port macros.

State and persistence: The header describes UART register state: FIFO readiness, line errors, break state, pin changes, interrupt masks, baud divisor, and output latch commands. It owns no software buffers or locking.

Dependencies and integration points: Depends on `sb1250_defs.h` and feature predicates for newer full-interrupt fields. Integrated by early console, serial driver, and board support using SiByte DUART register addresses.

Risks: `V_DUART_BAUD_RATE` assumes a 100 MHz source clock and integer division, so clock changes require care. Reserved bits are documented as must-be-zero in several registers. Interrupt macros have both combined and per-channel forms that can be confused.

Test signals: Serial console boot, baud-rate smoke tests, RX/TX interrupt tests, modem-control pin tests, and allmodconfig/SiByte defconfig builds provide the main signals.

Source read size: 349 lines, 11709 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/sb1250_uart.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/sentosa.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/sentosa.h

Purpose: Supplies Sentosa/Rhone SiByte board identity and simple board-specific constants for LEDs and debug GPIO.

Important APIs/types/functions: `SIBYTE_BOARD_NAME` selected by `CONFIG_SIBYTE_SENTOSA` versus Rhone, `LEDS_CS`, `LEDS_PHYS`, and `K_GPIO_DBG_LED`.

Control flow: Board setup includes this header to choose strings and fixed physical resources. There is no runtime logic in the header.

State and persistence: State is external board hardware: the LED chip-select/physical address and GPIO line used as a debug LED.

Dependencies and integration points: Includes `asm/sibyte/sb1250.h` and `asm/sibyte/sb1250_int.h`. Integrated by SiByte Sentosa/Rhone platform setup and diagnostic LED code.

Risks: The constants are board-specific; using them for a different SiByte board will point LED/GPIO code at wrong physical resources.

Test signals: Board defconfig compile, platform boot banner checks, and LED/GPIO smoke tests on Sentosa/Rhone hardware are the useful signals.

Source read size: 27 lines, 587 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/sentosa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/swarm.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/swarm.h

Purpose: Defines SWARM, LittleSur, and CRhone board names and fixed board resources for LEDs, IDE, and PCMCIA on SiByte evaluation systems.

Important APIs/types/functions: `SIBYTE_BOARD_NAME`, feature constants `SIBYTE_HAVE_PCMCIA`, `SIBYTE_HAVE_IDE`, optional `SIBYTE_DEFAULT_CONSOLE`, physical chip-select constants `LEDS_*`, `IDE_*`, `PCMCIA_*`, and GPIO/interrupt mappings `K_GPIO_GB_IDE`, `K_INT_GB_IDE`, `K_GPIO_PC_READY`, `K_INT_PC_READY`.

Control flow: Board setup selects constants through preprocessor configuration and platform code uses them to register resources and route GPIO-backed interrupts.

State and persistence: The header exposes immutable board layout rather than allocating state. The mapped resources represent persistent device placement in the physical address space and GPIO interrupt wiring.

Dependencies and integration points: Includes SiByte core and interrupt headers. Integrated by `arch/mips/sibyte/swarm` platform setup, IDE, PCMCIA, LED, and early console paths.

Risks: Wrong `CONFIG_*` selection changes physical addresses and interrupt lines. Optional IDE/PCMCIA feature flags must match the actual board variant.

Test signals: SWARM-family defconfig builds, resource registration logs, IDE/PCMCIA probe tests, LED access, and console boot with LittleSur default console are relevant.

Source read size: 46 lines, 1140 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/swarm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sigcontext.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sigcontext.h

Purpose: Connects kernel-private MIPS signal context handling to the UAPI signal context and defines a 32-bit compatibility `sigcontext32` layout for compat signal frames.

Important APIs/types/functions: Includes `<uapi/asm/sigcontext.h>` and defines `struct sigcontext32` with 32-bit register, FP register, FPC CSR, used-math, DSP, and reserved fields for 32-bit user ABI compatibility on a 64-bit kernel.

Control flow: Signal setup and restore code uses the structure when copying user signal frames for compat tasks. No functions are implemented here.

State and persistence: The structure serializes per-thread CPU/FPU/DSP state into user memory during signal delivery and reads it back during sigreturn. Persistence is the user-visible signal frame ABI.

Dependencies and integration points: Depends on the UAPI MIPS sigcontext definition and is included by `asm/signal.h` and arch signal code.

Risks: Field order and width are ABI-sensitive; changing the layout breaks existing 32-bit user programs and sigreturn. Padding/reserved fields must remain stable.

Test signals: Compat signal delivery/sigreturn tests, ptrace/register-state tests around signals, FP/DSP signal context tests, and 32-bit userspace on 64-bit MIPS are key signals.

Source read size: 37 lines, 1060 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sigcontext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/signal.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/signal.h

Purpose: Provides MIPS kernel-side signal helpers and declarations on top of the UAPI signal definitions.

Important APIs/types/functions: Includes `<uapi/asm/signal.h>`, declares `mips_abi_32`, defines `sig_uses_siginfo(ka, abi)` with different behavior for `CONFIG_TRAD_SIGNALS`, includes signal context/info headers, declares `__ARCH_HAS_IRIX_SIGACTION`, protected FP context helpers, and `do_notify_resume`.

Control flow: Signal-delivery paths use `sig_uses_siginfo` to choose old-style versus `siginfo` frames, call protected FP save/restore helpers around user copies, and invoke `do_notify_resume` when returning to user mode with pending work.

State and persistence: The header coordinates per-task ABI and signal-frame state, but stores no data itself. The declarations interact with user signal frames, FP context, and thread-info flags.

Dependencies and integration points: Depends on UAPI signal constants, MIPS ABI structures, `asm/sigcontext.h`, `asm/siginfo.h`, and signal implementation files under `arch/mips/kernel`.

Risks: Signal-frame selection is ABI-sensitive, especially with traditional IRIX-style signals and O32 compat. Protected FP context helpers must handle user access failures without corrupting saved state.

Test signals: Signal ABI tests across O32/N32/N64, siginfo versus old signal handlers, FP context preservation tests, and kernel return-to-user tests are relevant.

Source read size: 36 lines, 1126 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/signal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sim.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sim.h

Purpose: Provides assembler macros for simulator-oriented static function save metadata, allowing assembly code to emit named address/size records in a `.data` subsection.

Important APIs/types/functions: `save_static_function(symbol)` for 32-bit and 64-bit builds, stringification helpers `__str`/`__str2`, and offsets from `asm/asm-offsets.h`.

Control flow: Assembly code invokes the macro after a static function. The macro switches to `.data`, emits a symbol name string, aligns, stores start/end or size information, then returns to `.text`.

State and persistence: It emits object-file metadata consumed by simulator/debug tooling. No runtime mutable state is created by C code.

Dependencies and integration points: Depends on assembler context and `asm/asm-offsets.h`; uses MIPS assembler directives such as `.pushsection`, `.ascii`, `.align`, `.dword`, and `.word`.

Risks: The macro is assembler-only and layout-sensitive. Incorrect use around local labels or function boundaries will produce misleading metadata. The 32/64-bit forms differ in record width and alignment.

Test signals: Assembler build coverage and inspection of generated object sections in simulator-enabled MIPS builds are the main signals.

Source read size: 70 lines, 2070 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sim.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/smp-cps.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/smp-cps.h

Purpose: Declares data structures and entry points for MIPS Coherent Processing System SMP boot and power-management support.

Important APIs/types/functions: `CPS_ENTRY_PATCH_INSNS`; `struct vpe_boot_config`, `struct core_boot_config`, `struct cluster_boot_config`; global `mips_cps_cluster_bootcfg`; boot/init APIs `mips_cps_core_boot`, `mips_cps_core_init`, `mips_cps_boot_vpes`; PM hooks `mips_cps_pm_save`, `mips_cps_pm_restore`; exception vector externs; and `mips_cps_smp_in_use()` with a non-SMP false stub.

Control flow: CPS SMP code fills cluster/core/VPE boot descriptors, patches or copies boot vectors, boots secondary VPEs/cores, initializes per-core state, and saves/restores CPS state over power-management transitions.

State and persistence: Persistent state is the shared cluster boot configuration and per-core/VPE boot descriptors containing PC, GP, SP, and synchronization fields. Hardware state includes GCR/CPS registers and exception vectors.

Dependencies and integration points: Integrated by `arch/mips/kernel/smp-cps.c`, CPS assembly boot code, exception handlers, and `CONFIG_MIPS_CPS`/SMP build paths.

Risks: Boot descriptors are shared between CPUs before normal scheduling is active; cache coherency, CCA setup, and ordering are critical. Stub behavior must match non-SMP builds.

Test signals: MIPS CPS SMP boot on multi-core systems, hotplug/secondary bring-up tests, suspend/resume, and non-SMP compile coverage are the main signals.

Source read size: 63 lines, 1383 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/smp-cps.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/smp-ops.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/smp-ops.h

Purpose: Defines the platform SMP operation vector used by generic MIPS SMP code to delegate CPU setup, boot, IPI, and hotplug behavior to the active platform implementation.

Important APIs/types/functions: `struct plat_smp_ops` callbacks `send_ipi_single`, `send_ipi_mask`, `init_secondary`, `smp_finish`, `boot_secondary`, `smp_setup`, `prepare_cpus`, `prepare_boot_cpu`, `cpu_disable`, `cpu_die`, and `cleanup_dead_cpu`; `register_smp_ops`; wrappers `plat_smp_setup`, registration helpers for UP/VSMP/CPS, and generic IPI send declarations.

Control flow: Early boot registers an SMP ops implementation, generic MIPS setup calls `plat_smp_setup`/prepare hooks, secondary bring-up calls platform boot/init/finish callbacks, and IPI helpers route reschedule or call-function events through the registered ops.

State and persistence: The central state is the registered `plat_smp_ops` pointer held by implementation code. Callback side effects include CPU masks, boot state, interrupt routing, and hotplug state.

Dependencies and integration points: Depends on Linux CPU masks and errno handling. Integrated with MIPS SMP core, platform-specific SMP backends, `CONFIG_SMP`, `CONFIG_MIPS_MT_SMP`, and `CONFIG_MIPS_CPS`.

Risks: Missing callbacks or wrong registration can leave secondary CPUs unbootable or IPIs unrouted. Stub helpers for non-SMP must remain harmless and compile away cleanly.

Test signals: SMP boot/hotplug, IPI stress, call-function/reschedule tests, and defconfig coverage for UP, VSMP, and CPS registrations are useful.

Source read size: 107 lines, 2296 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/smp-ops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/smp.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/smp.h

Purpose: Provides MIPS architecture SMP declarations, CPU mapping helpers, IPI action bits, hotplug hooks, and arch-level IPI wrappers.

Important APIs/types/functions: `raw_smp_processor_id`, logical/physical CPU maps, sibling/core/foreign masks, `NO_PROC_ID`, IPI action flags `SMP_RESCHEDULE_YOURSELF`, `SMP_CALL_FUNCTION`, `SMP_ICACHE_FLUSH`, `smp_bootstrap`, `start_secondary`, `calculate_cpu_foreign_map`, hotplug hooks `__cpu_disable`, `__cpu_die`, `play_dead`, kexec helpers, and `mips_smp_ipi_allocate/free`.

Control flow: Boot code maps physical CPU IDs to logical IDs, starts secondaries through platform ops, then uses `arch_smp_send_reschedule` and call-function wrappers to deliver IPIs. Hotplug and kexec paths either call arch hooks or become no-ops depending on configuration.

State and persistence: Global CPU masks and mapping arrays describe topology and active CPUs. IPI allocation state is managed by implementation code. The current CPU ID is read from `current_thread_info()->cpu`.

Dependencies and integration points: Depends on Linux cpumask/thread headers, `asm/smp-ops.h`, and MIPS topology/hotplug implementation files.

Risks: CPU map array bounds depend on `CONFIG_MIPS_NR_CPU_NR_MAP` and `NR_CPUS`. IPI action bit semantics must stay in sync with interrupt handlers. Hotplug stubs can hide unsupported operations.

Test signals: SMP boot, topology reporting, IPI/call-function stress, CPU hotplug, kexec on nonboot CPUs, and UP build coverage are relevant.

Source read size: 139 lines, 3730 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/smp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/addrs.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/addrs.h

Purpose: Defines SGI SN physical/virtual address construction macros for node address spaces, small/big windows, aliases, PROM/kernel layout, hub register access, and KLDIR-derived firmware areas.

Important APIs/types/functions: NASID helpers `NASID_GET_META`, `NASID_GET_LOCAL`, `NASID_MAKE`; node base helpers `NODE_CAC_BASE`, `NODE_IO_BASE`, `TO_NODE_*`; window helpers `RAW_NODE_SWIN_BASE`, `NODE_SWIN_ADDR`, `WIDGETID_GET`; alias and boot areas `UALIAS_*`, `LBOOT_*`, `RBOOT_*`; backdoor directory/ECC helpers; hub access `LOCAL_HUB_L/S`, `REMOTE_HUB_L/S`; KLDIR accessors `KLD_*`, `LAUNCH_ADDR`, `NMI_ADDR`, `KLCONFIG_ADDR`, `GDA_ADDR`, and `NODE_OFFSET_TO_K0/K1`.

Control flow: SN code constructs addresses by combining NASID/node offsets with architectural base segments, translates between local/remote node offsets, then uses raw 64-bit hub accessors to read/write registers. Firmware table macros derive launch/NMI/KLCONFIG/GDA locations from KLDIR entries.

State and persistence: The header maps persistent hardware and firmware state: per-node memory windows, hub registers, PROM-reserved areas, backdoor directory memory, and KLDIR entries. The access macros directly perform MMIO reads/writes.

Dependencies and integration points: Depends on Linux SMP/types, MIPS address-space macros, `asm/sn/kldir.h`, and SN0/SN1 address variants. Integrated across IP27/SN platform boot, interrupt, memory, and firmware-discovery code.

Risks: Address composition is highly architecture-specific; a wrong NASID or segment base can cause remote memory/register corruption. Hub accessors are raw and require correct ordering from callers.

Test signals: IP27/SN boot, KLDIR parsing, remote hub register access, NUMA node discovery, and memory-window mapping tests are relevant.

Source read size: 377 lines, 12909 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/addrs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/agent.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/agent.h

Purpose: Provides macros for accessing a hub agent's NIC/micro-LAN register on SGI SN systems.

Important APIs/types/functions: `HUB_NIC_ADDR(cpuid)`, `SET_HUB_NIC`, `SET_MY_HUB_NIC`, `GET_HUB_NIC`, and `GET_MY_HUB_NIC`.

Control flow: Code maps a CPU ID to NASID through `cputonasid`, computes the hub NIC register offset, and reads/writes it through `REMOTE_HUB_L/S` or local wrappers.

State and persistence: State is the hub NIC/micro-LAN register used for board identity and management interactions. The macros directly mutate/read hardware registers.

Dependencies and integration points: Includes SN address and architecture headers and SN0/SN1 hub variants. Depends on CPU-to-NASID mapping being initialized.

Risks: Using these macros before CPU/NASID maps are valid, or against the wrong CPU ID, targets the wrong hub. MMIO ordering and serialization are caller responsibilities.

Test signals: SN boot inventory discovery, NIC read/write diagnostics, and multi-node CPU mapping validation are useful signals.

Source read size: 45 lines, 1133 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/agent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/arch.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/arch.h

Purpose: Defines common SGI SN architecture identity helpers and invalid sentinel values.

Important APIs/types/functions: `cputonasid(cpu)`, `cputoslice(cpu)`, and invalid sentinels `INVALID_NASID`, `INVALID_PNODEID`, `INVALID_MODULE`, `INVALID_PARTID`.

Control flow: Callers index `sn_cpu_info` to convert Linux CPU numbers into SN NASID/slice coordinates used for hub access and interrupt routing.

State and persistence: The header reads `sn_cpu_info` but does not define it. The state is platform CPU topology discovered during boot.

Dependencies and integration points: Depends on `asm/sn/types.h` and SN0 architecture constants. Integrated by nearly all SN platform code needing CPU-to-node translation.

Risks: Macros assume `sn_cpu_info` is populated and CPU indices are valid. Invalid sentinels are typed casts and must not be confused with valid signed IDs.

Test signals: SN CPU discovery, NUMA topology reporting, and SMP boot on IP27 are the key signals.

Source read size: 28 lines, 762 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/arch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/fru.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/fru.h

Purpose: Defines field-replaceable-unit confidence records used by SGI SN firmware/kernel diagnostics for memory, CPU, and PCI bus components.

Important APIs/types/functions: `confidence_t`, `kf_mem_t`, `kf_cpu_t`, and `kf_pci_bus_t` with maximum DIMM and PCI-device counts.

Control flow: Diagnostic code fills confidence values indicating likely failing components, and inventory/error reporting code interprets those values.

State and persistence: The structs persist diagnostic belief/confidence state associated with FRUs. They do not allocate or update state themselves.

Dependencies and integration points: Used by `klconfig.h` and SN diagnostic/inventory paths.

Risks: Array sizes are fixed ABI-like firmware assumptions. Misinterpreting confidence values can lead to bad service/inventory reports.

Test signals: KLCONFIG/FRU parsing, synthetic error injection, and diagnostic inventory output tests are useful.

Source read size: 44 lines, 1489 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/fru.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/gda.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/gda.h

Purpose: Defines the SGI SN Global Data Area layout and PROM operation commands used for boot coordination, partitioning, and PROM control.

Important APIs/types/functions: `GDA_VERSION`, field offsets, `gda_t`, `GDA`, partition GDA version, `PROMOP_*` magic/commands/options, and `PROMOP_REG`.

Control flow: Kernel/PROM code locates the GDA through `GDA_ADDR(get_nasid())`, reads bootmaster/partition/table fields, and writes PROM operation commands such as halt, powerdown, restart, reboot, or imode to the PROM operation register.

State and persistence: The GDA is firmware-provided persistent boot metadata. PROMOP values in PI error-stack space communicate requested PROM actions and boot options.

Dependencies and integration points: Depends on SN address macros and PI register definitions through included address headers. Integrated by SN boot, shutdown, restart, partition, and PROM handoff code.

Risks: Offsets are firmware ABI. Writing the wrong PROMOP command can halt or reboot hardware. The `GDA` macro assumes a valid current NASID.

Test signals: SN boot metadata parsing, reboot/powerdown paths, partition startup, and firmware handoff tests are relevant.

Source read size: 103 lines, 3170 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/gda.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/intr.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/intr.h

Purpose: Defines SGI SN hub interrupt send/clear macros and reserved interrupt level assignments for IP27/SN0.

Important APIs/types/functions: `LOCAL_HUB_SEND_INTR`, `REMOTE_HUB_SEND_INTR`, `LOCAL_HUB_CLR_INTR`, `REMOTE_HUB_CLR_INTR`, and interrupt numbers for UART, cross-calls, reschedule/call IPIs, bridge/IO errors, debug, clock, correction, NI, and panic events.

Control flow: Interrupt code writes hub PI pending set/clear registers using per-level bit shifts to raise or clear local or remote interrupts. The numeric constants reserve levels used by PROM, kernel, and platform devices.

State and persistence: State is hub interrupt pending/mask registers and assigned interrupt vector namespace. Macros directly mutate MMIO pending state.

Dependencies and integration points: Relies on hub address access macros and PI register offsets. Integrated by SN interrupt controller, SMP IPI, UART, error, and debug handlers.

Risks: Interrupt levels are shared ABI between PROM and kernel. Wrong level writes can disturb reserved PROM/debug or error interrupts.

Test signals: IPI tests, timer/UART interrupt delivery, error interrupt injection, and SN boot interrupt-controller initialization are useful.

Source read size: 112 lines, 2663 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/intr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/io.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/io.h

Purpose: Defines SGI SN hub I/O translation table entry helpers and I/O PRB register selection macros.

Important APIs/types/functions: `IIO_ITTE`, field shifts/masks for offset/widget/IOSP, `HUB_PIO_MAP_TO_MEM`, `HUB_PIO_MAP_TO_IO`, `IIO_ITTE_PUT`, `IIO_ITTE_DISABLE`, `IIO_ITTE_GET`, and `IIO_IOPRB(x)`.

Control flow: I/O setup writes ITTEs to map big-window PIO space to memory or widget I/O targets, disables mappings by writing an invalid widget, and locates PRB registers for widget flow-control/error management.

State and persistence: State is hardware I/O translation table entries and PRB registers in the hub. The macros write remote hub registers directly.

Dependencies and integration points: Includes SN0 hub I/O definitions and depends on `REMOTE_HUB_S/PTR` from SN address macros.

Risks: Incorrect ITTE programming can route PIO to the wrong widget or memory region. `IIO_ITTE_PUT` packs fields without runtime validation.

Test signals: PCI/Xtalk device probing, big-window PIO mapping tests, widget access, and error recovery for disabled mappings are relevant.

Source read size: 59 lines, 1868 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/ioc3.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/ioc3.h

Purpose: Defines the SGI IOC3 PCI multifunction chip register layout and bit definitions for serial, SuperIO, keyboard/mouse, parallel port, GPIO, Ethernet DMA, SSRAM, PCI status, and subsystem IDs.

Important APIs/types/functions: Register structs `ioc3_serialregs`, `ioc3_uartregs`, `ioc3_sioregs`, `ioc3_ethregs`, `ioc3_serioregs`, `ioc3`; DMA descriptors `ioc3_erxbuf`, `ioc3_etxd`; base offsets `IOC3_SIO_*`, bytebus offsets, PCI status flags, KM/serial status/control masks, SIO interrupt masks, GPIO masks, Ethernet control/status/ring masks, MII access masks, and IOC3 subsystem IDs.

Control flow: Drivers map IOC3 PCI BAR space to `struct ioc3`, then configure subblocks: reset/control SIO, program serial rings, service SIO interrupts, configure GPIO/PHY reset, manage Ethernet RX/TX rings, and access SuperIO UART/RTC/parallel registers at byte offsets.

State and persistence: Hardware state includes PCI config/status, GPIO latches, keyboard/mouse FIFOs, serial DMA rings and producer/consumer pointers, Ethernet rings, MAC/MII registers, interrupt enables, and SSRAM diagnostic space. The header itself owns no software state.

Dependencies and integration points: Depends only on Linux integer types. Integrated by SGI IOC3 serial, Ethernet, keyboard/mouse, MFD, and PCI bridge drivers.

Risks: The C structs must match hardware offsets exactly; padding or type-size changes are dangerous. The file contains legacy duplicate fields/macros (`ioc3_etxd.cmd`, `INT_OUT_MODE_*`) that consumers tolerate but should not be expanded. DMA ring alignment constants are hardware requirements.

Test signals: IOC3 driver compile, serial console, keyboard/mouse, Ethernet RX/TX under load, MII access, interrupt masking, and PCI subsystem detection tests are relevant.

Source read size: 606 lines, 21824 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/ioc3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/irq_alloc.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/irq_alloc.h

Purpose: Provides a minimal placeholder `struct irq_alloc_info` for SGI SN IRQ allocation interfaces.

Important APIs/types/functions: `struct irq_alloc_info { };`.

Control flow: Code can pass or declare IRQ allocation metadata uniformly even when this architecture variant has no fields.

State and persistence: No state is represented in this empty structure.

Dependencies and integration points: Integrated by IRQ allocation call sites that need an architecture-specific type.

Risks: Adding fields changes API expectations and may require initializer changes across IRQ setup code.

Test signals: Build coverage for SN IRQ allocation paths is sufficient.

Source read size: 11 lines, 199 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/irq_alloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/klconfig.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/klconfig.h

Purpose: Defines the SGI SN KLCONFIG firmware inventory format: board lists, component records, console metadata, allocation headers, board/component classes, device-specific structures, and lookup declarations.

Important APIs/types/functions: `KLCFGINFO_MAGIC`, `klconf_off_t`, board/component flags, `console_t`, `klc_malloc_hdr_t`, `kl_config_hdr_t`; access macros `KL_CONFIG_HDR`, `KL_CONFIG_INFO`, `KLCF_*`; class/type constants `KLCLASS_*`, `KLTYPE_*`; structures `lboard_t`, `klinfo_t`, `klcpu_t`, `klhub_t`, `klmembnk_t`, `klxbow_t`, `klbri_t`, `klioc3_t`, `klrou_t`, graphics/SCSI/FDDI/device structs; unions `klcomp_t`, `kldev_t`; and lookup declarations `find_lboard*`, `find_component*`.

Control flow: Firmware builds a linked list of local and remote board records in node-local KLCONFIG memory. Kernel code checks the magic, walks boards through offsets, resolves component offsets through NASID-aware macros, discovers CPUs, memory, bridges, IOC3s, routers, graphics, and devices, then binds drivers or reports inventory/errors.

State and persistence: KLCONFIG is persistent firmware-provided topology and diagnostic state. It encodes board flags, component flags, NIC IDs, physical/widget IDs, NASIDs, ARCS component pointers, error-info offsets, and console/device metadata.

Dependencies and integration points: Depends on Linux types, SN types, SN0/SN1 address definitions, FRU definitions, ARC firmware types, and platform-specific bridge/router headers under IP27/IP35 configurations.

Risks: The file explicitly warns that PROM assembly depends on struct layout; field reordering or insertion breaks firmware ABI. Offset-to-pointer macros assume correct NASID and K1 mapping. Some legacy constants reference IP35-only classes or external headers not present under all configs.

Test signals: IP27/SN boot inventory, CPU/memory/IO discovery, KLCONFIG walker tests, driver binding for IOC3/bridge/SCSI, and struct-offset compile checks are essential signals.

Source read size: 894 lines, 30637 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/klconfig.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/kldir.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/kldir.h

Purpose: Defines the generic SGI SN Kernel Launch Directory entry format and includes SN0-specific directory offsets.

Important APIs/types/functions: `KLDIR_MAGIC`, field offsets `KLDIR_OFF_*`, `KLDIR_ENT_SIZE`, `KLDIR_MAX_ENTRIES`, and `kldir_ent_t` with magic, offset, pointer, size, count, stride, and reserved fields.

Control flow: Boot code treats the KLDIR memory page as an array of fixed-size entries and uses generic plus SN0-specific constants to locate launch, NMI, KLCONFIG, GDA, and other firmware/kernel handoff areas.

State and persistence: The directory is firmware-populated persistent boot metadata. The header defines its in-memory ABI but does not mutate it.

Dependencies and integration points: Includes `asm/sn/sn0/kldir.h` for IP27 offsets and is used by `sn/addrs.h`.

Risks: Entry size and offsets are assembly/firmware ABI. Mis-sized structures break low-level boot and per-node firmware area discovery.

Test signals: Boot-time KLDIR validation, struct-size checks, and SN PROM handoff tests are relevant.

Source read size: 36 lines, 1068 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/kldir.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/klkernvars.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/klkernvars.h

Purpose: Defines the SN kernel variables handoff block used to communicate mapped-kernel physical bases and NASIDs.

Important APIs/types/functions: Offsets `KV_MAGIC_OFFSET`, `KV_RO_NASID_OFFSET`, `KV_RW_NASID_OFFSET`, magic `KV_MAGIC`, and `kern_vars_t` with magic, read-only/read-write NASIDs, padding, and physical base addresses.

Control flow: Mapped-kernel setup reads the KLDIR kernel-vars block, verifies magic, and uses the RO/RW NASIDs and base addresses to translate mapped kernel addresses to physical/K0 addresses.

State and persistence: Persistent state is firmware/kernel handoff data for mapped-kernel placement.

Dependencies and integration points: Depends on SN types and is consumed by `mapped_kernel.h` and hub/node setup code.

Risks: Offsets are used by assembly or firmware, so layout changes can break mapped-kernel boot. Invalid NASIDs or bases corrupt address translation.

Test signals: Mapped-kernel boot on SN, magic validation, and address translation tests are useful.

Source read size: 29 lines, 614 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/klkernvars.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/launch.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/launch.h

Purpose: Defines the SGI SN PROM launch structure and PROM entry-point wrappers for starting and managing slave CPUs.

Important APIs/types/functions: `LAUNCH_MAGIC`, struct offsets, launch states, `launch_state_t`, `launch_proc_t`, `launch_t`, and function-pointer macros `LAUNCH_SLAVE`, `LAUNCH_WAIT`, `LAUNCH_POLL`, `LAUNCH_LOOP`, `LAUNCH_FLASH`.

Control flow: The kernel fills per-CPU launch records with function, call parameter, stack, GP, and exception vector addresses, invokes PROM launch/wait/poll entry points, and secondary CPUs report state through the busy/state fields.

State and persistence: State is per-NASID/per-slice launch memory from KLDIR plus PROM entry points at fixed addresses. Fields are shared between PROM, boot CPU, and slave CPU.

Dependencies and integration points: Depends on SN types/address macros and SN0 PROM address constants. Integrated by IP27 SMP bring-up and PROM interaction code.

Risks: The structure has fixed offsets used by low-level code. Bad stack/GP/vector values or wrong NASID/slice can hang secondary boot.

Test signals: SN SMP secondary CPU boot, PROM launch wait/poll paths, and CPU hotplug/diagnostic launch tests are relevant.

Source read size: 106 lines, 3420 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/launch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/mapped_kernel.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/mapped_kernel.h

Purpose: Provides address translation helpers for SGI SN mapped kernels, converting replicated/mapped read-only and read-write kernel addresses to physical or K0 addresses.

Important APIs/types/functions: `REP_BASE`, `MAPPED_ADDR_RO_TO_PHYS`, `MAPPED_ADDR_RW_TO_PHYS`, `MAPPED_KERN_RO_PHYSBASE`, `MAPPED_KERN_RW_PHYSBASE`, `MAPPED_KERN_RO_TO_PHYS`, `MAPPED_KERN_RW_TO_PHYS`, `MAPPED_KERN_RO_TO_K0`, and `MAPPED_KERN_RW_TO_K0`.

Control flow: Code subtracts the mapped kernel base and adds per-node kernel-var physical bases where mapped-kernel support is enabled; otherwise it performs direct `REP_BASE` subtraction. Results can be converted to K0 with `PHYS_TO_K0`.

State and persistence: The translation depends on per-node `hub_data(n)->kern_vars` populated from firmware handoff. The header does not store state itself.

Dependencies and integration points: Depends on `linux/mmzone.h`, MIPS address-space macros, hub data, and `klkernvars.h`-style state.

Risks: Incorrect node selection for an address yields wrong physical translation. The 16 MiB RW offset convention is ABI-like and must match linker/PROM layout.

Test signals: Mapped-kernel boot, symbol/address translation checks, module/debug memory access, and non-mapped build coverage are relevant.

Source read size: 55 lines, 1975 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/mapped_kernel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/nmi.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/nmi.h

Purpose: Defines SGI SN NMI handoff records and saved-register frame layout used for non-maskable interrupt handling and diagnostics.

Important APIs/types/functions: `NMI_MAGIC`, size/offset constants, `nmi_t`, `struct reg_struct`, and register offset macros `R0_OFF` through `NMISR_OFF`.

Control flow: NMI setup fills per-CPU NMI records with magic, flags, callback, call parameter, and global-master state. NMI handlers save CPU registers into the fixed `reg_struct` layout for diagnostics and recovery.

State and persistence: State is per-NASID/per-slice NMI memory and saved register frames. It persists long enough for crash/debug handlers or PROM tools to inspect.

Dependencies and integration points: Depends on SN address macros and fixed KLDIR NMI locations. Integrated by SN NMI, panic, debug, and crash paths.

Risks: Offsets are assembly ABI; changing `reg_struct` layout or offset constants breaks NMI save/restore code. NMI callbacks must be safe in catastrophic contexts.

Test signals: NMI injection, panic/crash dump register validation, and assembly offset checks are useful.

Source read size: 125 lines, 3390 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/nmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/sn0/addrs.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/sn0/addrs.h

Purpose: Defines SN0/IP27-specific NASID geometry, node/window address layout, PROM memory map, UART/I2C addresses, cache-error frame locations, and error-workaround addresses.

Important APIs/types/functions: `NODE_SIZE_BITS`, `NASID_*`, `NODE_SWIN_BASE`, big-window helpers `NODE_BWIN_BASE`, `NODE_BWIN_ADDR`; PROM constants `IP27PROM_*`, `IO6PROM_*`; local UART/I2C register bases; cache-error offsets; and error workaround macros such as `ERR_STS_WAR_ADDR`.

Control flow: Generic SN address macros include this file to get SN0-specific bit shifts and boot memory map. Boot and PROM code use the constants to locate firmware entry points, launch loops, stacks, console buffers, flash/diagnostic areas, and local hub I/O registers.

State and persistence: The header describes fixed physical layout and PROM-reserved persistent areas. It owns no variables but points code at memory/register regions with boot-critical meaning.

Dependencies and integration points: Depends on MIPS address-space conversion macros through includers and on hub register constants for workaround addresses.

Risks: Many constants are physical addresses used before full MMU setup; mistakes can overwrite PROM, stacks, or diagnostic buffers. N-mode versus M-mode geometry changes NASID/node size semantics.

Test signals: IP27 PROM handoff, early console, secondary launch, KLDIR/GDA discovery, and cache-error handling tests are relevant.

Source read size: 283 lines, 9296 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/sn0/addrs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/sn0/arch.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/sn0/arch.h

Purpose: Defines SN0/IP27 architecture limits for CPUs, NASIDs, regions, partitions, memory slots, and CPUs per node.

Important APIs/types/functions: `MAXCPUS`, `MAX_NASIDS`, `MAX_REGIONS`, `MAX_PARTITIONS`, `NASID_MASK_BYTES`, `MAX_MEM_SLOTS`, `SLOT_SHIFT`, `SLOT_MIN_MEM_SIZE`, and `CPUS_PER_NODE`.

Control flow: Topology and memory-discovery code uses these compile-time limits to size masks/arrays and interpret slot/NASID geometry.

State and persistence: No mutable state is stored; constants constrain topology state held elsewhere.

Dependencies and integration points: Included by generic SN architecture and KLCONFIG headers.

Risks: Changing limits affects array sizes and firmware topology assumptions. N-mode versus M-mode changes maximum memory slots.

Test signals: SN topology discovery, memory slot reporting, and build coverage for SN0 modes are relevant.

Source read size: 56 lines, 1496 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/sn0/arch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/sn0/hub.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/sn0/hub.h

Purpose: Aggregates SN0 hub register definitions and provides small hub identity/attribute helpers.

Important APIs/types/functions: `HUB_PASSWORD`, chip/revision constants, `MAX_HUB_PATH`, included subheaders `hubpi.h`, `hubmd.h`, `hubio.h`, `hubni.h`, uncached attribute constants `UATTR_*`, and inline `get_nasid()`.

Control flow: SN0 code includes this umbrella header to access PI/MD/IIO/NI registers and to read the current hub NASID from the local network status register.

State and persistence: State is hub hardware revision, identity, and current node ID in hub registers. No software state is allocated.

Dependencies and integration points: Depends on SN0 address, processor-interface, memory-directory, I/O, and network-interface headers.

Risks: `get_nasid()` relies on local hub access being valid. Including this header brings many low-level MMIO macros into scope, increasing compile coupling.

Test signals: SN0 boot, NASID discovery, hub revision detection, and compile coverage for all hub subheaders are useful.

Source read size: 62 lines, 1428 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/sn0/hub.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/sn0/hubio.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/sn0/hubio.h

Purpose: Defines SN0 hub I/O interface register offsets, BTE registers, widget/LLP control/status formats, I/O translation/error/CRB registers, PRB formats, and BTE control/status fields.

Important APIs/types/functions: Friendly aliases `IIO_WIDGET*`, raw offsets `IIO_WID`, `IIO_ILCSR`, `IIO_PRTE`, `IIO_ICRB_*`, BTE aliases and offsets; union formats `hubii_wid_t`, `hubii_wcr_t`, `hubii_wstat_t`, `hubii_ilcsr_t`, `icrba_t`, `icrbb_t`, `icrbc_t`, `icrbd_t`, `iprte_a_t`, `iprb_t`, `icrbp_a_t`, `hubii_idsr_t`; error/command constants `IIO_ICRB_ECODE_*`, `IIO_ICCR_CMD_*`, `IECLR_*`, `IBLS_*`, `IBCT_*`, widget constants.

Control flow: I/O setup and error handlers read widget/LLP state, program protection/access registers, configure PIO read table entries, inspect/deallocate CRBs, control BTE transfers, clear IO errors, and manage per-widget PRBs. The file warns that CRB writes require I/O quiescence.

State and persistence: Hardware state includes hub widget identity, LLP link state, scratch registers, ITTE/PRTE mappings, CRB/PRB queues, BTE length/source/destination/control/interrupt registers, interrupt destination, and error-clear latches.

Dependencies and integration points: Consumed by SN I/O setup, Xtalk/PCI bridge code, BTE DMA support, and IO error recovery. Relies on SN address accessors from includers.

Risks: CRB manipulation is explicitly dangerous if DMA/PIO is active. Several legacy duplicate field/macro names and typo-like aliases exist, so compiler coverage per config matters. Wrong BTE or PRB programming can corrupt memory or wedge I/O.

Test signals: SN I/O link bring-up, Xtalk/PCI probing, BTE transfer tests, IO error injection/recovery, and CRB dump tooling are useful signals.

Source read size: 972 lines, 31329 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/sn0/hubio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/sn0/hubmd.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/sn0/hubmd.h

Purpose: Defines SN0 hub Memory/Directory register offsets, memory-bank configuration fields, directory/protection entry formats, page migration controls, error register formats, LED helpers, and performance counter formats.

Important APIs/types/functions: `MD_*` register offsets, memory size constants and `MD_SIZE_BYTES/MBYTES`, `MMC_*` memory config fields, refresh/DIMM/MOQ/MLAN fields, directory states `MD_DIR_*`, premium/standard directory masks, protection/migration fields, LED macros `CPU_LED_ADDR`, `SET_CPU_LEDS`, migration threshold/candidate macros, error unions `md_dir_error_t`, `md_mem_error_t`, `md_proto_error_t`, directory entry unions, `dir_mem_entry_t`, and MD perf counter unions.

Control flow: Memory setup programs memory config/refresh/DIMM registers, directory code initializes directory/protection entries, NUMA migration code configures thresholds and reads candidates, diagnostics read/clear MD error registers, and LED/debug code writes hub LED registers.

State and persistence: State is the hub MD register block, memory bank sizing, directory/protection memory, migration counters/candidates, ECC/protocol/misc error latches, MLAN/NIC controls, and performance counters.

Dependencies and integration points: Used by SN memory initialization, NUMA/page-migration code, error handlers, and diagnostics. Relies on `REMOTE_HUB_L/S`, `get_nasid`, `get_slice`, and platform private data through includers.

Risks: Directory and protection bitfields are hardware ABI. Incorrect migration threshold or directory writes can affect coherency. The header includes legacy typo/duplicate artifacts (`md_dir_error_t` duplicated close, `MMCE_lONG_PACK_SHFT`) that should be handled carefully.

Test signals: SN memory discovery, ECC/protocol error injection, page migration enable/disable tests, LED diagnostics, and build coverage for premium/standard directory modes are relevant.

Source read size: 789 lines, 26673 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/sn0/hubmd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/sn0/hubni.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/sn0/hubni.h

Purpose: Defines SN0 hub Network Interface registers and bitfields for link status, routing/vector PIO, age controls, LLP parameters/errors, routing tables, and region-size detection.

Important APIs/types/functions: `NI_*` register offsets, status masks `NSRI_*`, reset/protection masks, global/diagnostic parameter fields, vector PIO fields `NVP_*` and `NVS_*`, age control fields, port parameter/error fields, routing table helpers, `hubni_port_error_t`, LLP maxima, and inline `get_region_shift()`.

Control flow: SN networking/topology code reads NI status to determine node ID, link state, region mode, and hub revision; programs routing/vector PIO and age controls; handles port errors; and uses routing table macros for meta/local routes.

State and persistence: State is NI hardware: link/reset/protection, vector PIO status/data, aging parameters, LLP port parameters/errors, and routing table entries.

Dependencies and integration points: Depends on Linux types for C builds and on `LOCAL_HUB_L` from SN address accessors through includers.

Risks: Reset bits can reset the link or hub. Region shift controls NASID-to-region interpretation and must match hardware status. Wrong routing table or vector PIO programming can isolate nodes.

Test signals: SN multi-node boot, NI link status/routing table validation, vector PIO tests, link error injection, and region-size detection tests are useful.

Source read size: 263 lines, 9525 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/sn0/hubni.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/sn0/hubpi.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/sn0/hubpi.h

Purpose: Defines SN0 hub Processor Interface register offsets and bitfields for CPU protection, CPU enable/NMI/reset, interrupt pending/masks, cross-call interrupts, realtime/profiling timers, graphics controls, error stacks/status, BIST, SYSAD checking, and NACK counters.

Important APIs/types/functions: `PI_*` register offsets for protection, CPU presence/enable, interrupt masks, CC pending set/clear, realtime/profiling counters, BIST, graphics, and error registers; CALIAS constants; error masks `PI_ERR_*`; composed fatal/misc error masks; error status/stack field masks; `ERR_STACK_SIZE_BYTES`; C formats `pi_err_stack_t`, `pi_err_stat0_t`, `pi_err_stat1_t`; `rtc_time_t`; and SYSAD/interrupt-pending/NACK constants.

Control flow: Low-level SN code programs CPU and IO protection, enables CPUs, sends NMIs or soft resets, sets/clears interrupt and cross-call pending bits, configures realtime/profiling interrupts, records processor-interface errors into stack/status registers, and reads or clears those errors during machine-check style recovery.

State and persistence: State is entirely hardware-visible: per-CPU pending/mask registers, CPU present/enable bits, realtime compare/pending/enables, graphics credit/page controls, error-stack base/size, error status words, CRB timeout state, SYSAD checking enables, and NACK counters.

Dependencies and integration points: Depends on Linux integer types and is included by `hub.h`, SN interrupt code, NMI/error handling, realtime clock code, and SMP cross-call/IPI paths. Address access is supplied by hub address macros from includers.

Risks: Many registers are per-slice with A/B offsets, so wrong offset arithmetic targets the wrong CPU. Error-status fields use different shifts for stack versus status registers. Duplicate `ERR_STK_ADDR_SHFT` is a legacy artifact; changes here can break assembly/error decode code.

Test signals: SN CPU interrupt/IPI tests, realtime timer/profiler interrupts, NMI and soft-reset paths, PI error injection/decoding, and SYSAD error-check build/runtime coverage are useful signals.

Source read size: 409 lines, 15947 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/sn0/hubpi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/sn0/kldir.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/sn0/kldir.h

Purpose: Defines SN0/IP27-specific KLDIR entry offsets, sizes, counts, and strides for launch, KLCONFIG, NMI, PI error, symmon stack, free memory, GDA, and NMI register frames.

Important APIs/types/functions: `SYMMON_STACK_SIZE`, `IP27_LAUNCH_*`, `IP27_KLCONFIG_*`, `IP27_NMI_*`, `IP27_PI_ERROR_*`, `IP27_SYMMON_STK_*`, `IP27_FREEMEM_*`, `IO6_GDA_*`, `IP27_NMI_KREGS_OFFSET`, and `IP27_NMI_EFRAME_*`.

Control flow: Generic KLDIR code uses these constants to seed or interpret KLDIR entries, and address macros use the resulting entries to locate per-CPU launch/NMI areas and firmware/kernel handoff blocks.

State and persistence: The constants describe fixed boot memory reservations in each node's low memory and IO6 PROM area.

Dependencies and integration points: Included by generic `asm/sn/kldir.h` and used by SN0 address macros.

Risks: Offsets overlap boot-critical PROM/kernel areas if changed incorrectly. Negative/variable free-memory sizing is an ABI convention with PROM.

Test signals: KLDIR dump validation, secondary launch, NMI frame capture, GDA discovery, and boot memory reservation tests are relevant.

Source read size: 186 lines, 7005 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/sn0/kldir.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/types.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/types.h

Purpose: Defines SGI SN-specific scalar identifier types used across topology, partition, module, and hardware graph code.

Important APIs/types/functions: `cpuid_t`, `nasid_t`, `partid_t`, `moduleid_t`, and `vertex_hdl_t`.

Control flow: These typedefs are used to make SN topology and inventory code explicit about CPU, node, partition, module, and hardware graph handles.

State and persistence: No state is stored; the file standardizes type widths and signedness.

Dependencies and integration points: Depends on Linux types for `dev_t`. Included by SN architecture, KLCONFIG, launch, and kernel-vars headers.

Risks: Changing signedness or width breaks sentinel values and firmware structure layout.

Test signals: Build coverage and struct-layout checks in SN headers are sufficient.

Source read size: 25 lines, 687 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sni.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sni.h

Purpose: Defines Siemens-Nixdorf MIPS board identifiers, CPU identifiers, platform register addresses, interrupt mappings, IDPROM offsets, and board initialization declarations.

Important APIs/types/functions: `sni_brd_type`; board constants `SNI_BRD_*`; CPU constants `SNI_CPU_*`; MMIO address macros for PCIMT/PCIT/A20R registers; interrupt constants for A20R, PCIT, PCIMT, EISA, SCSI, Ethernet, power/button/temperature; IDPROM offsets; init declarations `sni_*_init`, `sni_*_irq_init`, optional `sni_eisa_root_init`, `sni_hwint`, and `sni_isa_irq_handler`.

Control flow: Platform setup identifies the board from IDPROM, selects board-specific register maps and IRQ initialization, sets hardware interrupt dispatch, and exposes EISA/ISA handlers where configured.

State and persistence: State is global board type, board MMIO registers, interrupt pending/selection registers, IDPROM contents, and selected hardware interrupt handler.

Dependencies and integration points: Depends on Linux IRQ return type and MIPS `CKSEG1ADDR`/CPU IRQ constants through includers. Integrated by SNI platform setup and interrupt code.

Risks: Several register offsets differ under `CONFIG_SNI_RM` versus other PCIMT variants. Wrong board type or endian XOR for IDPROM offsets can misread hardware and route IRQs incorrectly.

Test signals: SNI board defconfig builds, IDPROM detection, IRQ routing smoke tests, EISA root init, and platform boot on RM200/PCIT/PCIMT variants are relevant.

Source read size: 243 lines, 7439 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sni.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/socket.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/socket.h

Purpose: Wraps MIPS UAPI socket definitions and provides kernel-visible socket type enumeration values when not building with strict ABI compatibility.

Important APIs/types/functions: Includes `<uapi/asm/socket.h>`, defines `enum sock_type` values such as `SOCK_STREAM`, `SOCK_DGRAM`, `SOCK_RAW`, `SOCK_RDM`, `SOCK_SEQPACKET`, `SOCK_DCCP`, and `SOCK_PACKET`, then sets `ARCH_HAS_SOCKET_TYPES`.

Control flow: Kernel networking code can use arch-provided socket type constants matching the MIPS ABI while generic code detects `ARCH_HAS_SOCKET_TYPES`.

State and persistence: No runtime state; this is ABI constant exposure.

Dependencies and integration points: Depends on UAPI socket definitions and generic socket users.

Risks: Socket type numeric values are user ABI. Any change breaks syscall compatibility.

Test signals: Networking syscall ABI tests, MIPS userspace socket smoke tests, and compile coverage are useful.

Source read size: 41 lines, 1108 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/socket.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sparsemem.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sparsemem.h

Purpose: Defines the maximum physical memory address width for MIPS sparsemem support.

Important APIs/types/functions: `MAX_PHYSMEM_BITS` set to 48.

Control flow: Memory model code uses the constant at compile time to size sparsemem section addressing.

State and persistence: No runtime state; it constrains memory model limits.

Dependencies and integration points: Included by Linux sparsemem/mm configuration code for MIPS.

Risks: Changing the bit width changes memory hotplug/sparsemem sizing assumptions and can break high-physical-address platforms.

Test signals: MIPS sparsemem builds, boot on high-memory/NUMA systems, and memory hotplug coverage are relevant.

Source read size: 18 lines, 486 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sparsemem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/spinlock.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/spinlock.h

Purpose: Provides the MIPS queued spinlock hook and includes generic queued spinlock/read-write lock implementations.

Important APIs/types/functions: `queued_spin_unlock(struct qspinlock *lock)` when configured, the `queued_spin_unlock` macro override, and includes `asm/qspinlock.h` and `asm/qrwlock.h`.

Control flow: Unlock uses `smp_store_release` to store zero into the lock value, providing release ordering before generic queued lock code handles later acquisitions.

State and persistence: State is the `qspinlock` word embedded in caller-owned locks. The header does not allocate lock state.

Dependencies and integration points: Depends on MIPS processor barriers and generic qspinlock/qspinlock types. Integrated by all kernel spinlock users on MIPS.

Risks: Memory ordering is subtle; weakening `smp_store_release` breaks lock release semantics. Struct layout must match generic qspinlock types.

Test signals: Locking selftests, SMP stress, lockdep, qspinlock build coverage, and MIPS SMP boot under contention are relevant.

Source read size: 31 lines, 822 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/spinlock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/spinlock_types.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/spinlock_types.h

Purpose: Exposes generic queued spinlock and queued read-write lock type definitions for MIPS.

Important APIs/types/functions: Includes `asm-generic/qspinlock_types.h` and `asm-generic/qrwlock_types.h`.

Control flow: No control flow; this provides type declarations used by locking headers and structures.

State and persistence: Lock state is stored in generic lock structures defined by the included headers.

Dependencies and integration points: Integrated by MIPS locking and generic kernel synchronization code.

Risks: Type include order must remain compatible with `spinlock.h` and generic locking. ABI/layout changes affect every embedded spinlock/rwlock.

Test signals: Kernel build and lockdep/locking selftests provide coverage.

Source read size: 8 lines, 188 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/spinlock_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/spram.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/spram.h

Purpose: Declares or stubs the MIPS scratchpad RAM configuration hook.

Important APIs/types/functions: `spram_config()` extern when `CONFIG_MIPS_SPRAM` is enabled; otherwise an inline no-op `spram_config()`.

Control flow: Platform or CPU setup calls `spram_config`; SPRAM-enabled builds run the real configuration routine, while other builds compile to no operation.

State and persistence: State is CPU/platform scratchpad RAM configuration performed elsewhere. This header owns no state.

Dependencies and integration points: Depends on `CONFIG_MIPS_SPRAM` and the implementation file that provides `spram_config`.

Risks: Callers must not assume scratchpad RAM exists when the no-op stub is selected. Missing extern implementation breaks SPRAM builds.

Test signals: SPRAM-enabled defconfig builds and boot on SPRAM-capable MIPS CPUs are the relevant signals.

Source read size: 11 lines, 254 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/spram.h -->
