# subset-b-000846 research

This grouped report covers the requested SPARC kernel files for `subset-b-000846`. Each source file has a separate delimited section for deterministic splitting into the required source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/kgdb_64.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/kgdb_64.c

Purpose: Provides the SPARC64 architecture glue for KGDB register marshalling, breakpoint trap handling, SMP capture callbacks, and program-counter manipulation.

Important APIs/types/functions: `pt_regs_to_gdb_regs()` copies a live trap frame into GDB register slots, including globals, outs, locals/ins read through the register window at `UREG_FP + STACK_BIAS`, `tpc`, `tnpc`, `tstate`, and `y`. `sleeping_thread_to_gdb_regs()` synthesizes a stopped task view from `thread_info`, `switch_to_pc`, and `ret_from_fork`. `gdb_regs_to_pt_regs()` writes GDB state back while preserving the current-window pointer bits in `TSTATE_CWP`. `smp_kgdb_capture_client()` flushes windows and invokes `kgdb_nmicallback()` on SMP capture interrupts. `kgdb_arch_handle_exception()`, `kgdb_trap()`, `kgdb_arch_set_pc()`, and `arch_kgdb_ops.gdb_bpt_instr` implement continue/detach/kill and the `ta 0x72` breakpoint.

Control flow: A kernel breakpoint trap enters `kgdb_trap()`, rejects user traps via `bad_trap()`, flushes register windows, disables local IRQs, and calls `kgdb_handle_exception()`. KGDB remote commands can optionally set `tpc`, always keep `tnpc` one instruction ahead, and skip over `arch_kgdb_breakpoint` when continuing from the built-in breakpoint.

State and persistence: The file mutates only transient register state and KGDB global state. It relies on stack-resident register windows and task `thread_info`; no persistent data is allocated. The main invariant is preserving `TSTATE_CWP` when importing debugger-provided `tstate`.

Dependencies and integration points: It depends on KGDB core, kdebug/context tracking, SPARC trap/register-window layout, `flushw_all()`, `bad_trap()`, and the assembly breakpoint symbol from `misctrap.S`.

Risks and test signals: Wrong stack-bias/window handling corrupts locals/ins in debugger views. Incorrect `tnpc` adjustment can re-enter breakpoints or skip instructions. Test signals include SPARC64 KGDB attach, continue with and without address arguments, sleeping task backtraces, SMP CPU capture, and traps from user mode being rejected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/kgdb_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/kprobes.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/kprobes.c

Purpose: Implements SPARC64 kprobes and kretprobes using software single-step emulation because the architecture lacks suitable hardware single-step support.

Important APIs/types/functions: Per-CPU `current_kprobe` and `kprobe_ctlblk` track the active probe, saved `tnpc`, saved PIL bits, and reentry state. `arch_prepare_kprobe()`, `arch_arm_kprobe()`, and `arch_disarm_kprobe()` copy original instructions, install `BREAKPOINT_INSTRUCTION`, and flush I-cache. `kprobe_handler()` runs pre-handlers and redirects execution to `p->ainsn.insn[0]` followed by a second breakpoint. `post_kprobe_handler()`, `resume_execution()`, `relbranch_fixup()`, and `retpc_fixup()` restore control flow after the copied instruction. `kprobe_fault_handler()` handles faults during active probes. `kprobe_trap()` bridges trap levels `0x170` and `0x171` to `notify_die()`. Kretprobe support is in `arch_prepare_kretprobe()`, `trampoline_probe_handler()`, `kretprobe_trampoline_holder()`, and `arch_init_kprobes()`.

Control flow: The first breakpoint disables preemption, resolves the probe, optionally runs `pre_handler`, masks PIL interrupts, and executes the copied instruction in the probe slot. The second breakpoint runs `post_handler`, fixes `tpc`/`tnpc` and return-PC-producing instructions, restores the saved PIL, clears or restores nested probe state, and re-enables preemption. Reentered probes single-step without invoking user handlers and increment missed counts.

State and persistence: State is per-CPU and live only during trap handling, plus permanent probe instruction slots and the registered trampoline kprobe. The code temporarily rewrites kernel text and must keep copied instructions coherent with `flushi()`.

Dependencies and integration points: It integrates Linux kprobes/kretprobes, die notifiers, exception tables, SPARC trap levels, register windows, I-cache flushing, and `__kretprobe_trampoline_handler()`.

Risks and test signals: Relative branch and `call`/`jmpl` fixups are high risk because copied instruction addresses differ from real addresses. Register-window spills during `retpc_fixup()` must be correct for `%i/%l` destinations. Tests should include probes on calls, branches, delay-slot-adjacent code, nested probes, removed probes racing with trap delivery, kretprobes, and faulting probed instructions with exception-table fixups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/kprobes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/kstack.h -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/kstack.h

Purpose: Provides SPARC kernel stack validation helpers and hardirq stack switching primitives used by diagnostics such as the NMI watchdog.

Important APIs/types/functions: `kstack_valid()` validates a stack pointer, already adjusted for `STACK_BIAS`, against the current thread stack and optional per-CPU hardirq/softirq stacks. `kstack_is_trap_frame()` checks whether a `pt_regs` pointer lies in a valid stack area and contains a `PT_REGS_MAGIC` value. `set_hardirq_stack()` switches `%sp` to the per-CPU hardirq stack unless already on it, and `restore_hardirq_stack()` restores the saved stack pointer.

Control flow: Validation first checks alignment and the thread stack bounds, then falls back to hardirq and softirq stacks if allocated. Trap-frame validation shares the same bounds logic and then checks the magic field. Hardirq switching reads the current `%sp`, compares it to the hardirq stack interval, and writes a top-of-stack value adjusted for frame size and `STACK_BIAS`.

State and persistence: The functions do not allocate state. They read `thread_info`, per-CPU `hardirq_stack`/`softirq_stack`, and directly mutate `%sp` for a bounded critical section.

Dependencies and integration points: It depends on SPARC stack-frame layout, `thread_info`, IRQ stack arrays, `pt_regs`, `sparc_stackf`, `THREAD_SIZE`, and inline assembly. `nmi.c` uses it to run pseudo-NMI work on the hardirq stack.

Risks and test signals: Bad bounds or bias math can make stack unwinding accept invalid frames or switch to an invalid stack. Useful tests include lockup watchdog interrupts, stack traces from normal/hardirq/softirq contexts, trap-frame detection across stack edges, and SMP systems with and without separate IRQ stacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/kstack.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/ktlb.S -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/ktlb.S

Purpose: Contains SPARC64 kernel ITLB/DTLB miss fast paths for kernel mappings, including TSB lookups, vmalloc/module mapping walks, OBP translation handling, and sun4v patch points.

Important APIs/types/functions: Assembly entry labels include `kvmap_itlb`, `kvmap_itlb_4v`, `kvmap_dtlb`, `kvmap_dtlb_4v`, `kvmap_dtlb_nonlinear`, `kvmap_linear_early`, `kvmap_dtlb_tsb4m_load`, `kvmap_vmemmap`, and longpath labels for real faults. Macros such as `KERN_TSB_LOOKUP_TL1`, `KERN_TSB4M_LOOKUP_TL1`, `KERN_PGTABLE_WALK`, `OBP_TRANS_LOOKUP`, `TSB_LOCK_TAG`, and `TSB_WRITE` perform the MMU-specific work.

Control flow: ITLB misses read or receive the missing virtual address, reject NULL calls, probe the kernel TSB, fall back to page-table or OBP lookup, write a TSB entry, and load the TLB. DTLB misses first distinguish linear mapping addresses from nonlinear/vmalloc/module addresses, try the 4 MB TSB for linear mappings unless debug page allocation forces base pages, and otherwise page-table walk or signal a real fault. Long paths prepare processor state and branch to `sparc64_realfault_common` or `winfix_trampoline` for higher-level handling.

State and persistence: The code writes kernel TSB entries and IMMU/DMMU data-in ASIs, and uses `.sun4v_2insn_patch` sections so hypervisor systems replace direct ASI TLB loads with sun4v load paths. It reads global MMU constants such as `kern_linear_pte_xor`, `VMALLOC_END`, and optional `VMEMMAP_BASE`.

Dependencies and integration points: It depends on SPARC64 ASIs, TSB format, page tables, OBP translation tables, sun4v patching, sparsemem vmemmap, debug pagealloc, and low-level fault/trap assembly.

Risks and test signals: This is boot-critical code; a bad branch range, wrong context assumption, or wrong patched instruction corrupts kernel address translation. Tests are SPARC64 boot on sun4u and sun4v, vmalloc/module execution and data access, NULL kernel access faults, OBP mapping access, sparsemem vmemmap access, debug_pagealloc builds, and TLB miss stress under SMP.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/ktlb.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/ldc.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/ldc.c

Purpose: Implements the Logical Domain Channel link-layer driver for sun4v logical domains, including queue management, handshake negotiation, packetized read/write modes, exported memory cookies, and hypervisor copy operations.

Important APIs/types/functions: `struct ldc_packet` defines control/data/error frames, version/RTS/RTR/RDX controls, fragments, and reliable ACK fields. `struct ldc_channel` owns queue state, sequence numbers, handshake state, mode ops, event callback, IRQ names, and an `ldc_iommu`. Exported channel APIs include `ldc_alloc()`, `ldc_bind()`, `ldc_connect()`, `ldc_disconnect()`, `ldc_unbind()`, `ldc_free()`, `ldc_state()`, `ldc_mode()`, `ldc_rx_reset()`, `ldc_write()`, `ldc_read()`, and `__ldc_print()`. Exported memory APIs include `ldc_map_sg()`, `ldc_map_single()`, `ldc_unmap()`, `ldc_copy()`, `ldc_alloc_exp_dring()`, and `ldc_free_exp_dring()`.

Control flow: `ldc_init()` reads the machine description, registers the LDOM hypervisor API, and enables allocation only when `domaining-enabled` is true. Allocation validates the mode, initializes the per-channel IOMMU map table, queues, IRQs, mode ops, and list node. `ldc_bind()` registers TX/RX queues with the hypervisor and enters `BOUND`. `ldc_connect()` starts the version/RTS/RTR/RDX handshake; RX interrupts process control frames until `LDC_HS_COMPLETE`, then report `LDC_EVENT_UP` and data-ready events. Read/write paths lock the channel, verify handshake completion, and dispatch to raw, unreliable/reliable packet, or stream mode.

State and persistence: Persistent runtime state is per-channel: queue head/tail offsets mirrored with the hypervisor, `snd_nxt`/`rcv_nxt`, `tx_acked`, `chan_state`, `hs_state`, flags for allocated/registered/reset resources, stream buffering, and IOMMU bitmap/MTE table. Mapped cookies persist until `ldc_unmap()` revokes entries through `sun4v_ldc_revoke()`.

Dependencies and integration points: It depends on sun4v hypervisor calls, machine descriptions from `mdesc.c`, Linux IRQs, spinlocks, IOMMU map-table helpers, scatterlists, page allocation, and client drivers that consume event callbacks and cookies.

Risks and test signals: The code has explicit comments about missing serialization for `ldc_channel_list`, so duplicate channel allocation races are a risk. Handshake and sequence state must tolerate resets, NACKs, and partial fragments. Cookie alignment is strict 8-byte alignment. Tests should exercise raw/unreliable/stream channels, queue full and `HV_EWOULDBLOCK` paths, reset/disconnect, bad sequence NACKs, short stream reads, scatterlist mapping/unmapping, `ldc_copy()` partial copies, and disabled-domaining boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/ldc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/led.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/led.c

Purpose: Provides a small load/user-controlled front-panel LED driver for SPARC systems through AUXIO and an optional `/proc/led` interface.

Important APIs/types/functions: `led_toggle()` reads `get_auxio()` and updates `AUXIO_LED` through `set_auxio()`. `led_blink()` toggles the LED and reschedules a global timer either by load average or a user-selected interval. With procfs enabled, `led_proc_show()`, `led_proc_open()`, and `led_proc_write()` expose state and commands: `on`, `toggle`, numeric interval seconds, `load`, and any other input as off. `led_init()` sets up the timer and proc entry; `led_exit()` removes the proc entry and deletes the timer.

Control flow: Module initialization registers `/proc/led` and arms no timer by default. Writes delete any active blink timer before changing state so manual `on`/off commands persist. Numeric or `load` commands set `led_blink_timer_timeout` and call `led_blink()` to start repeated toggles.

State and persistence: State is a global `timer_list`, timeout value, and physical AUXIO LED bit. No state persists beyond module lifetime. User writes are copied through `memdup_user_nul()` and truncated to eight bytes.

Dependencies and integration points: It depends on `asm/auxio.h`, procfs, timers, jiffies, load average `avenrun`, and module init/exit infrastructure.

Risks and test signals: Timer/proc races are mitigated with `timer_delete_sync()` on writes and exit, but command parsing is intentionally simple. Tests include proc read/write of every command, load-based blinking, module unload while blinking, AUXIO hardware access, and builds without `CONFIG_PROC_FS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/led.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/leon_kernel.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/leon_kernel.c

Purpose: Implements LEON platform IRQ, extended IRQ, timer, clockevent, and clocksource initialization for SPARC32 LEON systems.

Important APIs/types/functions: Global register pointers `leon3_irqctrl_regs` and `leon3_gptimer_regs` point to IRQMP and GPTIMER MMIO maps. `leon_get_irqmask()`, `leon_build_device_irq()`, `leon_update_virq_handling()`, `leon_unmask_irq()`, `leon_mask_irq()`, `leon_eoi_irq()`, and `leon_set_affinity()` define the LEON IRQ chip. `leon_eirq_setup()` registers an extended IRQ demux. `leon_cycles_offset()`, `leon_init_timers()`, `leon_clear_clock_irq()`, and SMP `leon_percpu_timer_ce_interrupt()` drive timers. `leon_init_IRQ()` installs LEON callbacks into `sparc_config`.

Control flow: Boot scans `/ambapp0` for system ID, IRQMP, and GPTIMER nodes, honors AMP timer ownership, selects timer index and IRQ, detects whether the timer pending bit is write-clearable, adjusts IRQ controller selection, masks boot CPU IRQs, optionally registers extended IRQ demuxing, patches SMP trap behavior, and requests the timer IRQ. The IRQ chip masks/unmasks bits in per-CPU IRQMP mask registers according to affinity.

State and persistence: Runtime state is MMIO register state, selected timer index, ACK mask, GPTIMER IRQ number, extended IRQ number, debug globals, and `sparc_config` function pointers. No disk persistence exists.

Dependencies and integration points: It integrates Open Firmware device nodes, LEON AMBA definitions, IRQ core descriptors, SPARC timer framework, SMP clockevents, cache patching through `local_ops`, and low-level IRQ mapping from `irq_map`.

Risks and test signals: Incorrect device-tree parsing or IRQMP register selection breaks all interrupts. AMP timer skipping and shared GPTIMER IRQs are board-sensitive. Tests include LEON boot, timer ticks, extended IRQ dispatch, IRQ affinity changes on SMP, level-triggered EOI handling, AMP configurations, and missing-node failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/leon_kernel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/leon_pci.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/leon_pci.c

Purpose: Provides the common LEON PCI host-bridge setup routine shared by GRPCI host drivers.

Important APIs/types/functions: `leon_pci_init()` accepts a platform device and `struct leon_pci_info`, allocates a `pci_host_bridge`, attaches I/O, memory, and bus-number resources, assigns parent/sysdata/config ops/IRQ callbacks, scans the root bus, assigns unassigned resources, and adds devices.

Control flow: GRPCI-specific probe code fills `leon_pci_info` with resource windows, config-space ops, bus range, and IRQ mapping. `leon_pci_init()` translates the I/O window so PCI I/O starts at bus address `0x1000`, creates the host bridge, calls `pci_scan_root_bus_bridge()`, then lets generic PCI claim and publish devices.

State and persistence: It owns no global state; persistent state is the allocated PCI host bridge and child PCI devices registered with the kernel.

Dependencies and integration points: It depends on generic Linux PCI host bridge APIs, LEON PCI descriptors from `asm/leon_pci.h`, `pci_common_swizzle`, and platform-device ownership.

Risks and test signals: Resource offset mistakes make I/O BARs unusable, especially because low 4 KB of PCI I/O is intentionally skipped. Test signals include GRPCI1/GRPCI2 enumeration, BAR assignment, IRQ swizzling, resource windows in `/proc/iomem`/sysfs, and allocation failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/leon_pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/leon_pci_grpci1.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/leon_pci_grpci1.c

Purpose: Implements the GRPCI1 LEON PCI host bridge driver, including config-space access, target BAR setup, shared interrupt demuxing, and PCI error handling.

Important APIs/types/functions: `struct grpci1_regs` maps APB bridge registers; `struct grpci1_priv` embeds `leon_pci_info`, register pointer, resources, IRQ maps, error mask, and AHB/PCI windows. Config helpers `grpci1_cfg_r{8,16,32}()` and `grpci1_cfg_w{8,16,32}()` select the bus in `cfg_stat`, access config space via LEON bypass loads/stores, swab values for little-endian PCI, and handle master aborts. `grpci1_map_irq()`, `grpci1_irq`, `grpci1_pci_flow_irq()`, `grpci1_err_interrupt()`, `grpci1_hw_init()`, and `grpci1_of_probe()` are the main driver pieces.

Control flow: Probe allows only one host, maps APB registers, verifies host-slot mode, BAR1 size, and byte twisting, maps PCI I/O/config windows, requests resource ranges, initializes hardware target mappings, creates virtual IRQs for INTA-D and errors, installs a LEON IRQ demux, enables selected error interrupts, and calls `leon_pci_init()` to enumerate the bus.

State and persistence: Persistent runtime state is the single global `grpci1priv`, bridge MMIO state, target BAR programming, resource claims, virtual IRQs, and PCI devices. Error policy is controlled by the optional `all_pci_errors` OF property.

Dependencies and integration points: It depends on LEON bypass MMIO, OF platform probing, `irq_of_parse_and_map()`, LEON IRQ helpers, generic PCI ops, and common LEON PCI initialization.

Risks and test signals: Single-instance global state prevents multiple GRPCI1 cores. Config abort clearing writes bridge PCI status and must not mask real errors. Tests include host-slot rejection, byte-twisting requirement, config reads of absent devices, INTx demux, PCI error injection, resource conflicts, and enumeration up to bus 15/device 15.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/leon_pci_grpci1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/leon_pci_grpci2.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/leon_pci_grpci2.c

Purpose: Implements the GRPCI2 LEON PCI host bridge driver with wider bus support, configurable target BARs, optional reset, IRQ mode handling, error/DMA interrupt demuxing, and config-space access.

Important APIs/types/functions: `struct grpci2_regs` maps control/status, DMA, BAR, AHB-master map, and optional trace registers. `struct grpci2_barcfg` describes OF-configured target BAR mapping. `struct grpci2_priv` embeds `leon_pci_info`, IRQ mode/mask/reset settings, PCI ID, virtual IRQs, windows, and six target BAR configs. `grpci2_cfg_r{8,16,32}()` and `grpci2_cfg_w{8,16,32}()` select the bus in `ctrl`, clear config status, access config space, and wait for `STS_CFGERRVALID`. `grpci2_hw_init()`, `grpci2_pci_flow_irq()`, `grpci2_err_interrupt()`, and `grpci2_of_probe()` drive bridge setup.

Control flow: Probe maps registers, checks host/master capability, parses `barcfg`, `irq_mask`, and `reset` properties, maps PCI windows, claims resources, initializes hardware, configures IRQ routing based on `irq_mode`, registers error handling, enables error/system interrupts, and hands off to `leon_pci_init()`.

State and persistence: Persistent runtime state is the single global `grpci2priv`, bridge control/status register programming, AHB-to-PCI map entries, target BAR registers, virtual IRQs, and registered PCI devices. OF properties persist as boot-time policy only.

Dependencies and integration points: It integrates OF platform data, LEON IRQ update helpers, generic PCI host ops, LEON bypass stores/loads, `of_ioremap()`, and common LEON PCI enumeration.

Risks and test signals: The config-access wait loops have no timeout, so stuck hardware can hang the kernel. The `irq_mask` parse path appears to assign `do_reset` instead of `irq_mask`, making that property suspicious. Tests should cover all IRQ modes, reset/no-reset boots, custom target BARs, config errors for absent devices, DMA/error IRQ routing, resource conflict cleanup, and bus numbers up to 255.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/leon_pci_grpci2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/leon_pmc.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/leon_pmc.c

Purpose: Installs the LEON CPU idle power-down handler, with board-specific fixups for systems that require an extra non-cacheable access around the sleep instruction.

Important APIs/types/functions: `pmc_leon_need_fixup()` compares the high half of `amba_system_id` against `pmc_leon_fixup_ids`. `pmc_leon_idle_fixup()` enables IRQs, writes `%asr19` to enter sleep, reads the IRQ controller using the LEON bypass ASI, then disables IRQs. `pmc_leon_idle()` uses only the sleep write. `leon_pmc_install()` assigns `sparc_idle` on LEON systems.

Control flow: A late initcall checks `sparc_cpu_model`, selects the fixup or normal idle callback, and logs initialization. The idle callback must temporarily enable interrupts so the CPU can wake.

State and persistence: It mutates only the global `sparc_idle` function pointer and live CPU interrupt state. Board matching depends on `amba_system_id` discovered earlier by LEON platform initialization.

Dependencies and integration points: It depends on LEON AMBA IDs, CPU model detection, IRQ controller register pointer, raw IRQ enable/disable, ASI bypass loads, and SPARC process idle infrastructure.

Risks and test signals: Running sleep with interrupts disabled can hang the CPU. The fixup path assumes IRQMP is mapped and non-cacheable through bypass ASI. Tests include idle entry/wakeup on listed and unlisted LEON systems, late init ordering after AMBA system ID discovery, and CPU hot/idle stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/leon_pmc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/leon_smp.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/leon_smp.c

Purpose: Provides SPARC32 LEON SMP bringup, cache-snooping setup, IPI routing, cross-call handling, and CPU startup synchronization.

Important APIs/types/functions: `leon_configure_cache_smp()` validates D-cache snooping and disables caches when unsupported. `leon_boot_cpus()`, `leon_boot_one_cpu()`, `leon_cpu_pre_starting()`, `leon_cpu_pre_online()`, and `leon_smp_done()` implement bringup. IPI support uses per-CPU `struct leon_ipi_work`, `leon_ipi_init()`, `leon_send_ipi()`, `leon_ipi_single()`, `leon_ipi_mask_one()`, `leon_ipi_resched()`, `leonsmp_ipi_interrupt()`, and `leon_ipi_ops`. Cross calls use global aligned `ccall_info`, `cross_call_lock`, `leon_cross_call()`, and `leon_cross_call_irq()`.

Control flow: Boot initializes IPI trap routing, enables cross-call/ticker/IPI IRQs on the boot CPU, sets ticker broadcast, and configures caches. Each secondary CPU is assigned an idle thread, gets the SRMMU context table, is woken through IRQMP `mpstatus`, signals `cpu_callin_map`, adopts `init_mm`, and waits for `smp_commenced_mask`. Runtime IPIs set per-CPU work flags and force the configured IRQ; the interrupt drains single, mask, and reschedule work.

State and persistence: Persistent runtime state includes `leon_ipi_irq`, `smp_processors_ready`, per-CPU work flags, `current_set`, CPU callin/online masks, trap table patches, and `ccall_info`. Hardware state is IRQMP mask/force/broadcast registers and cache snooping configuration.

Dependencies and integration points: It depends on LEON IRQMP/GPTIMER state initialized elsewhere, OF `/ambapp0`, SPARC trap tables, SRMMU context table, cache/TLB local ops, generic SMP call-function APIs, and SPARC32 IPI ops.

Risks and test signals: Broadcast IRQMP support is mandatory for multi-CPU operation. Cross-call serialization relies on a single global structure and busy-wait completion. Tests include multi-CPU boot, cache snoop-disabled systems, IPI reschedule/call-function stress, CPU startup timeout handling, trap table patch correctness, and freeing unused per-CPU trap tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/leon_smp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/mdesc.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/mdesc.c

Purpose: Manages sun4v machine descriptions from the hypervisor, exposing graph traversal, dynamic update notifications, CPU topology extraction, page-size discovery, and `/dev/mdesc` reads.

Important APIs/types/functions: `struct mdesc_hdr` and `struct mdesc_elem` define the hypervisor-provided node/name/data layout. `struct mdesc_handle` wraps aligned description bytes with refcounting and allocation ops. Exported traversal APIs include `mdesc_grab()`, `mdesc_release()`, `mdesc_register_notifier()`, `mdesc_update()`, `mdesc_get_node()`, `mdesc_get_node_info()`, `mdesc_node_by_name()`, `mdesc_get_property()`, `mdesc_next_arc()`, `mdesc_arc_target()`, and `mdesc_node_name()`. CPU/platform routines include `sun4v_mdesc_init()`, `mdesc_populate_present_mask()`, `mdesc_get_page_sizes()`, and `mdesc_fill_in_cpu_data()`.

Control flow: Early boot calls `sun4v_mdesc_init()`, asks the hypervisor for the size and bytes, allocates through memblock, installs `cur_mdesc`, initializes ADI, and reports platform properties. Later `mdesc_update()` rereads through kmalloc, swaps `cur_mdesc`, computes notifier remove/add events for supported node types, and retains old referenced handles on a zombie list. Traversal helpers walk the flat element table, matching node tags, property names, and arc types.

State and persistence: Persistent runtime state is `cur_mdesc`, handle refcounts, `mdesc_zombie_list`, notifier client list, `max_cpus`, and populated `cpu_data`/trap-block fields. `/dev/mdesc` open pins a handle until close, making reads stable across updates.

Dependencies and integration points: It depends on sun4v hypervisor `sun4v_mach_desc`, memblock/kmalloc, refcounts, Open Firmware string-list helpers, CPU masks/topology, trap queue sizing, ADI initialization, miscdevice registration, and LDC/virtual-device clients that register MD notifiers.

Risks and test signals: Node comparison currently supports only virtual-device-port and domain-services-port clients. Graph traversal must tolerate cycles via bounded recursion in back-node searches. Tests include boot MD parsing, `/dev/mdesc` read/seek across updates, notifier add/remove on virtual device changes, CPU topology/cache/socket IDs, page-size mask intersection, missing platform properties, and refcount/zombie cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/mdesc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/misctrap.S -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/misctrap.S

Purpose: Provides miscellaneous SPARC64 trap entry stubs for KGDB breakpoints, privileged action traps, memory-not-aligned traps, floating load/store alignment emulation, and breakpoints.

Important APIs/types/functions: Under `CONFIG_KGDB`, `arch_kgdb_breakpoint` emits `ta 0x72` and returns. `__do_privact` clears the DMMU fault-valid bit and calls `do_privact()`. `do_mna` captures DMMU fault address/status, clears fault-valid, handles higher trap levels through `winfix_mna`, or calls `mem_address_unaligned()`. `do_lddfmna` and `do_stdfmna` call `handle_lddfmna()` and `handle_stdfmna()`. `breakpoint_trap` calls `sparc_breakpoint()`.

Control flow: Each trap stub prepares `%g7` for `etrap`, branches into the common trap entry path, passes `pt_regs` at `%sp + PTREGS_OFF` plus saved fault information to C handlers, and returns through `rtrap`. The unaligned access path has an early high-trap-level branch to window-fixup handling.

State and persistence: The stubs mutate MMU fault status registers by clearing `TLB_SFSR`, use DMMU SFAR/SFSR values as arguments, and rely on trap-frame state built by `etrap`. No persistent memory is allocated.

Dependencies and integration points: It depends on SPARC64 trap entry/return assembly (`etrap`, `rtrap`, `winfix_mna`), MMU ASIs, KGDB, and C handlers for privileged action, alignment, floating memory alignment, and breakpoints.

Risks and test signals: Incorrect register handoff to C handlers misreports fault address/status. Failure to clear fault-valid can retrigger traps. Tests include KGDB breakpoint entry, unaligned user/kernel memory access, lddf/stdf alignment emulation, privileged action traps, high trap-level MNA handling, and breakpoint trap dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/misctrap.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/module.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/module.c

Purpose: Implements SPARC module loader architecture hooks for ELF symbol cleanup, relocation application, sun4v patch sections, and Spitfire I-cache handling.

Important APIs/types/functions: `module_frob_arch_sections()` finds the symbol table and converts undefined `STT_REGISTER` symbols to absolute so generic module loading ignores SPARC register pseudo-symbols. `apply_relocate_add()` handles SPARC relocations such as `R_SPARC_DISP32`, `R_SPARC_32`, `R_SPARC_UA32`, `R_SPARC_WDISP30`, `R_SPARC_WDISP22`, `R_SPARC_LO10`, `R_SPARC_HI22`, and on SPARC64 `R_SPARC_64`, `R_SPARC_UA64`, `R_SPARC_WDISP19`, and `R_SPARC_OLO10`. `do_patch_sections()` and `module_finalize()` patch `.sun4v_1insn_patch` and `.sun4v_2insn_patch` on hypervisor TLB systems.

Control flow: During module load, section frobbing normalizes register symbols before generic resolution. Relocation processing iterates each `Elf_Rela`, computes symbol plus addend, patches bytes or instruction fields, and aborts on unsupported relocation types. Finalization applies sun4v instruction substitutions and, on Spitfire, flushes register windows and invalidates I-cache tags.

State and persistence: It mutates module text/data in memory and may modify module patch sections. It does not keep module-private state after load. The relocated code persists until module unload.

Dependencies and integration points: It depends on Linux module loader/ELF structures, SPARC relocation encodings, sun4v patch helpers, `tlb_type`, Spitfire cache routines, and exported module loader hooks.

Risks and test signals: Relocation bitfield mistakes produce invalid branches or addresses. The SPARC64 BUG_ON enforces module locations under 4 GB for patched sites. Tests include loading modules with branches/calls/64-bit data/OLO10 relocations, modules containing sun4v patch sections, old SPARC register symbols, unsupported relocation rejection, and Spitfire cache coherency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/nmi.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/nmi.c

Purpose: Implements SPARC64 pseudo-NMI hardlockup watchdog support using performance counter overflow interrupts.

Important APIs/types/functions: Global `nmi_active` tracks watchdog availability and active CPUs; per-CPU `wd_enabled`, `last_irq_sum`, `alert_counter`, and `nmi_touch` track liveness. `arch_touch_nmi_watchdog()` resets touch flags. `perfctr_irq()` is the pseudo-NMI handler. `start_nmi_watchdog()`, `stop_nmi_watchdog()`, `nmi_adjust_hz()`, `nmi_init()`, `watchdog_hardlockup_enable()`, and `watchdog_hardlockup_disable()` manage watchdog lifecycle. `die_nmi()` reports or panics on lockup.

Control flow: Initialization starts counters on all CPUs, spins CPUs briefly in `check_nmi_watchdog()` to verify interrupts arrive, then registers a reboot notifier. Each perf counter interrupt clears the soft interrupt, enters NMI context, switches to hardirq stack, runs die notifiers, checks whether normal IRQ counts advanced or the watchdog was touched, increments alert counters on stalls, and reloads/enables the counter when still active.

State and persistence: Runtime state is per-CPU watchdog counters and PCR/PIC hardware programming through `pcr_ops`. `panic_on_timeout` is set by `nmi_watchdog=panic`. The watchdog is disabled permanently by setting `nmi_active` to `-1` when setup fails.

Dependencies and integration points: It integrates Linux NMI/watchdog APIs, reboot notifiers, kdebug die notifiers, SPARC perf counter operations, `kstack.h` hardirq stack switching, CPU data NMI counters, and SMP cross-CPU calls.

Risks and test signals: Because this is not a real NMI, it depends on high-priority perf interrupts and correct PCR programming. False positives are possible if IRQ accounting stops for legitimate long critical sections. Tests include boot-time watchdog self-test, `nmi_watchdog=panic`, enable/disable per CPU, `nmi_adjust_hz()`, reboot shutdown, perf counter interrupt delivery, and hard lockup injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/nmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/of_device_32.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/of_device_32.c

Purpose: Builds SPARC32 platform devices and resources from the Open Firmware tree, with translators for PCI, SBUS, AMBAPP, and default buses.

Important APIs/types/functions: Bus translators are represented by `struct of_bus` entries for PCI, SBUS, AMBAPP, and default mappings. Helpers include `of_bus_pci_match()`, `of_bus_pci_map()`, `of_bus_pci_get_flags()`, AMBAPP cell/map/flag helpers, `of_match_bus()`, `build_one_resource()`, `use_1to1_mapping()`, `build_device_resources()`, `scan_one_device()`, `scan_tree()`, and `scan_of_devices()`.

Control flow: A postcore initcall scans the root node and recursively creates platform devices. Each device inherits OF node identity, IRQs from `intr` or `interrupts` translated through `sparc_config.build_device_irq`, resources built by walking parent `ranges`, DMA masks, parent links, and platform bus type before `of_device_register()`.

State and persistence: The scan creates persistent `platform_device` objects and fills `dev_archdata.resource` and IRQ arrays. `of_resource_verbose` is set by `of_debug=1` for boot-time diagnostics.

Dependencies and integration points: It depends on OF property APIs, common address helpers from `of_device_common.c`, SPARC32 PROM IRQ formats, LEON AMBAPP support, platform bus registration, and `sparc_config` IRQ mapping callbacks.

Risks and test signals: Resource truncation to 32 bits and fixed resource arrays can misrepresent large or numerous regions. Missing `ranges` may force 1:1 mappings except for known hierarchy nodes. Tests include SPARC32 OF scanning on SBUS/PCI/LEON AMBAPP, `intr` versus `interrupts` properties, verbose resource output, devices with missing `ranges`, and registration failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/of_device_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/of_device_64.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/of_device_64.c

Purpose: Builds SPARC64 platform devices, resources, and IRQ mappings from the Open Firmware tree, with special handling for PCI, Simba, SBUS, and FHC/Central buses.

Important APIs/types/functions: `of_ioremap()`/`of_iounmap()` reserve/release resource ranges and return direct physical-address cookies as `__iomem` pointers. Bus translators include PCI, Simba, SBUS, FHC, and default entries. Resource helpers mirror SPARC32 but keep 64-bit addresses and mask hypervisor physical aliases. IRQ helpers include `apply_interrupt_map()`, `pci_irq_swizzle()`, `build_one_device_irq()`, and OF debug parsing. `scan_one_device()`, `scan_tree()`, and `scan_of_devices()` create devices.

Control flow: Postcore scanning creates a root platform device and recursively registers children. Resources are built from bus-specific address properties through parent `ranges`. IRQs are copied from `interrupts`, translated by direct node irq translators, interrupt-map properties, PCI swizzling, or ancestor translators, then assigned NUMA affinity when possible.

State and persistence: Persistent state consists of registered platform devices, resource arrays, translated IRQs, dev archdata, and optional resource/IRQ verbose flags from `of_debug=`.

Dependencies and integration points: It integrates OF property parsing, SPARC64 IRQ translator nodes, generic platform devices, PCI interrupt conventions, NUMA affinity, `tlb_type == hypervisor` address masking, and common bus helpers.

Risks and test signals: Interrupt-map parsing is sensitive to cell counts and masks; fallback PCI swizzling handles firmware gaps but can misroute unusual bridges. `of_ioremap()` only reserves regions rather than creating remapped virtual addresses. Tests include PCI with/without ranges, Simba bridges, FHC nodes, interrupt-map translation, onboard PCI controller fallback, NUMA IRQ affinity, too many IRQ/resource warnings, and hypervisor address masking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/of_device_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/of_device_common.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/of_device_common.c

Purpose: Provides shared SPARC Open Firmware platform-device helpers for IRQ/resource lookup, MMIO mapping, archdata propagation, default bus translation, and SBUS matching.

Important APIs/types/functions: `irq_of_parse_and_map()` returns precomputed platform-device IRQs. `of_address_to_resource()` copies prebuilt resources. `of_iomap()` maps a resource through `of_ioremap()`. `of_propagate_archdata()` recursively copies IOMMU, streaming cache, host controller, NUMA node, and DMA ops from a bus device to descendants. Translation helpers include `of_bus_default_count_cells()`, `of_out_of_range()`, `of_bus_default_map()`, `of_bus_default_get_flags()`, `of_bus_sbus_match()`, and `of_bus_sbus_count_cells()`.

Control flow: Architecture-specific OF scanners build platform devices and resources first. Generic users later call these helpers to retrieve IRQs, resources, and mapped MMIO from the existing platform device associated with a node. Address translation verifies a child address lies in a parent range, adds the child offset to the parent base, and returns new parent cells.

State and persistence: The file owns no persistent global state. It reads and writes already-created `platform_device` archdata and resources.

Dependencies and integration points: It depends on Linux OF/platform APIs, SPARC archdata fields, common header `of_device_common.h`, resource APIs, and architecture-specific `of_ioremap()`.

Risks and test signals: Callers get `0`, `NULL`, or `-EINVAL` when no platform device exists or the index is out of range, so probe ordering matters. Translation handles only up to two size cells. Tests include `of_iomap()` for every resource type, archdata propagation through nested buses, SBUS hierarchy matching, out-of-range ranges, and invalid indexes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/of_device_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/of_device_common.h -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/of_device_common.h

Purpose: Declares shared SPARC Open Firmware bus-translation helpers and the `struct of_bus` descriptor used by 32-bit and 64-bit OF device scanners.

Important APIs/types/functions: `of_read_addr()` folds big-endian address cells into a `u64`. Declarations cover default bus cell counting, range checks, default mapping, default flags, SBUS matching, and SBUS cell counting. `OF_MAX_ADDR_CELLS` caps translated address arrays at four cells. `struct of_bus` names a bus, address property, optional matcher, cell counter, range mapper, and resource-flag function.

Control flow: There is no runtime control flow beyond the inline `of_read_addr()` loop. Architecture-specific scanners build ordered arrays of `struct of_bus` and invoke these callbacks while walking parent ranges.

State and persistence: The header owns no state; it defines callback contracts and constants.

Dependencies and integration points: It is consumed by `of_device_common.c`, `of_device_32.c`, and `of_device_64.c`, and depends on OF device-node types and Linux resource flag conventions.

Risks and test signals: The four-cell cap must match all supported SPARC firmware address formats. `of_read_addr()` assumes cells are already CPU-endian values supplied by OF helpers. Build tests for both SPARC32 and SPARC64 OF scanners and resource translation tests exercise this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/of_device_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/pci.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/pci.c

Purpose: Implements UltraSPARC PCI controller support around Open Firmware bus scanning, config-space pokes, PBM root-bus creation, resource claiming, MSI hooks, DMA quirks, and slot naming.

Important APIs/types/functions: Globals `pci_pbm_root` and `pci_num_pbms` track PBM controllers. `pci_config_read{8,16,32}()` and `pci_config_write{8,16,32}()` perform protected physical-bypass config accesses with `pci_poke_*` fault tracking. OF scan helpers include `pci_parse_of_flags()`, `pci_parse_of_addrs()`, `of_create_pci_dev()`, `of_scan_pci_bridge()`, `pci_of_scan_bus()`, `pci_scan_one_pbm()`, and `pci_bus_register_of_sysfs()`. Other exported/arch hooks include `pci_iobar_pfn()`, `pcibus_to_node()`, `pci_domain_nr()`, `arch_setup_msi_irq()`, `arch_teardown_msi_irq()`, `ali_sound_dma_hack()`, `pci_resource_to_user()`, `pcibios_device_add()`, and slot-name init helpers.

Control flow: Controller-specific PBM code calls `pci_scan_one_pbm()`, which creates a root bus with PBM resource windows, recursively creates PCI devices from OF child nodes, scans bridges, registers `obppath` sysfs files, claims firmware-assigned resources, and adds devices. Bridge scanning parses `bus-range` and `ranges`, with Simba fallback ranges when firmware omits them. Config accesses set global poke state so low-level fault handling can suppress failed reads.

State and persistence: Persistent state includes PBM lists/indexes, PCI device/resource trees, sysfs `obppath` files, slot objects, and global poke fault flags guarded by `pci_poke_lock`. MSI setup delegates to per-PBM callbacks.

Dependencies and integration points: It depends on OF platform devices produced by `of_device_64.c`, PBM internals from `pci_impl.h`, generic PCI core, MSI descriptors, IRQ subsystem, APB/Simba bridge definitions, IOMMU archdata, NUMA, and SR-IOV hooks.

Risks and test signals: Config poke globals are volatile and serialized only by `pci_poke_lock`; fault handling must respect `pci_poke_cpu`. Firmware quirks such as duplicate OF devices, bogus bridge sizes, missing Simba ranges, and ALI DMA masks are explicitly handled. Tests include PBM scan on UltraSPARC systems, absent-device config reads, bridge resource windows, duplicate OF node suppression, VGA legacy claims, MSI setup/teardown, ALI sound DMA quirk, SR-IOV VF archdata copy, user resource addresses, and slot-name creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/pci.c -->
