# subset-b-000808 research

Grouped research for PowerPC sysdev interrupt controllers, PCI host helpers, Freescale/Tundra board glue, NVRAM/RTC helpers, MPIC MSI/timer support, and XICS/XIVE build selection. Each section is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_rmu.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_rmu.c

Purpose: Implements Freescale MPC85xx/MPC86xx RapidIO RMU support for outbound/inbound mailbox messages, inbound/outbound doorbells, port-write reception, and message-unit error cleanup.

Important APIs/types/functions: Defines RMU register layouts `rio_msg_regs`, `rio_dbell_regs`, `rio_pw_regs`, descriptor/ring structures, and `struct fsl_rmu`. Main entry points are `fsl_rio_setup_rmu()`, `fsl_rio_doorbell_init()`, `fsl_rio_port_write_init()`, `fsl_rio_pw_enable()`, `fsl_rio_doorbell_send()`, `fsl_open_outb_mbox()`, `fsl_close_outb_mbox()`, `fsl_add_outb_message()`, `fsl_open_inb_mbox()`, `fsl_close_inb_mbox()`, `fsl_add_inb_buffer()`, and `fsl_get_inb_message()`. Interrupt paths are `fsl_rio_tx_handler()`, `fsl_rio_rx_handler()`, `fsl_rio_dbell_handler()`, and `fsl_rio_port_write_handler()`.

Control flow: Setup allocates `struct fsl_rmu`, derives the message-unit register window from the device tree, maps TX/RX IRQs, and attaches the handle to the RapidIO master-port private data. Mailbox open paths validate power-of-two ring sizes, allocate coherent descriptor/message rings, program enqueue/dequeue pointers, request IRQs, and enable the message unit. TX enqueue copies the user buffer to the current DMA buffer, fills a descriptor, advances the hardware enqueue pointer, and rotates the software slot. RX delivery is interrupt-driven: the IRQ callback notifies the RapidIO core, while `fsl_get_inb_message()` copies from the inbound DMA ring to a client buffer and re-enables message interrupts. Doorbell and port-write handlers parse hardware queues, dispatch matching callbacks, acknowledge status bits, and schedule deferred port-write processing via workqueue.

State and persistence: Long-lived state includes coherent TX/RX rings, per-slot physical buffers, ring indexes, interrupt numbers, global doorbell and port-write objects declared in `fsl_rio.h`, FIFO/workqueue state for port writes, and status/error counters. Register state is persistent hardware state: message mode/status registers, queue pointers, doorbell masks, port-write queue base registers, and link/error enables. Doorbell send is serialized by `fsl_rio_doorbell_lock`; port-write FIFO extraction uses `kfifo_out_spinlocked()`.

Dependencies and integration points: Depends on Linux RapidIO core callbacks/resources, Freescale RapidIO globals from `fsl_rio.h`, DMA-coherent memory, OF address/IRQ parsing, workqueues, kfifo, and big-endian MMIO helpers. It integrates with board-level RapidIO setup that supplies `rio_regs_win`, `rmu_regs_win`, `dbell`, and `pw`.

Risks: Hardware queue processing comments acknowledge that RX, doorbell, and port-write handlers process only one queued event rather than draining until empty. Several paths assume globally initialized RapidIO windows and objects. Mailbox close frees descriptor rings but not every per-slot outbound DMA buffer allocated in open. Error recovery mostly clears status without rebuilding queues. The code casts DMA addresses to `u32`, so platforms with addresses beyond 32 bits would be fragile.

Test signals: Useful signals include RapidIO enumeration on MPC85xx/MPC86xx, inbound/outbound mailbox loopback, doorbell delivery across multiple ports and resource ranges, port-write FIFO overflow and transaction-error tests, queue-full/error interrupt injection, IRQ teardown/reopen cycles, DMA leak checking, and lockdep around doorbell and port-write paths.

Source read size: 1107 lines, 29398 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_rmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_soc.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_soc.c

Purpose: Provides common Freescale SoC helpers for IMMR base discovery, system/BRG/baud clock lookup, reset-control based restart, DIU data callbacks, and ePAPR hypervisor restart/halt hooks.

Important APIs/types/functions: Exports `get_immrbase()`, `fsl_get_sys_freq()`, `get_brgfreq()`, `get_baudrate()`, and optional `diu_ops`. Internal restart support uses `setup_rstcr()` and `fsl_rstcr_restart()`. Paravirtual control is through `fsl_hv_restart()` and `fsl_hv_halt()`.

Control flow: Clock/base helpers lazily search OF nodes, cache the discovered value in static variables initialized to `-1`, and return `-1` if no usable node/property exists. `setup_rstcr()` scans `global-utilities` nodes for `fsl,has-rstcr`, maps the reset control register at offset `0xb0`, and registers a high-priority restart notifier. The restart notifier disables local IRQs and writes HRESET_REQ. Hypervisor restart/halt issue Freescale hcalls and spin forever.

State and persistence: Persistent state is cached `immrbase`, cached static clock rates in helper functions, mapped `rstcr`, exported DIU callback table, and machine restart/halt integration through notifier or platform hooks.

Dependencies and integration points: Uses OF node/property APIs, PowerPC `ppc_md`/restart infrastructure, CPM/QUICC Engine clock users, Freescale DIU framebuffer users, and Freescale hypervisor hcall wrappers.

Risks: Cached `-1` values make missing properties sticky. `setup_rstcr()` uses `of_iomap(np, 0) + 0xb0` and tests the adjusted pointer rather than the original mapping, so a failed mapping plus offset arithmetic is subtle. Clock helpers return unsigned `u32` values using `-1` as sentinel, requiring callers to know that convention.

Test signals: Boot on FSL BookE/86xx boards with valid and missing `soc` clocks, CPM/QE serial clock users, restart through RSTCR, DIU platform data consumers, and ePAPR paravirtual restart/halt paths.

Source read size: 217 lines, 4524 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_soc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_soc.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_soc.h

Purpose: Declares the public Freescale SoC helper interface shared by PowerPC platform code and drivers.

Important APIs/types/functions: Declares `get_immrbase()`, `fsl_get_sys_freq()`, conditional `get_brgfreq()`/`get_baudrate()` stubs, `enum fsl_diu_monitor_port`, `struct platform_diu_data_ops`, exported `diu_ops`, and hypervisor hooks `fsl_hv_restart()`/`fsl_hv_halt()`.

Control flow: The header has no runtime control flow. Its only logic is compile-time selection of real CPM/QE clock declarations versus inline stubs that return `-1`.

State and persistence: Defines no storage except the external `diu_ops` declaration. The callback struct describes persistent board-provided DIU operations for pixel format, gamma, monitor routing, pixel clock, validation, and bootmem release.

Dependencies and integration points: Includes `asm/mmu.h` and forwards SPI/device-node types. Used by Freescale platform setup, DIU framebuffer/platform code, CPM/QE users, and ePAPR hypervisor machine descriptors.

Risks: The inline fallback uses `u32` return type with `-1`, preserving a sentinel but inviting accidental use as a valid high clock frequency. DIU callbacks are optional global function pointers, so callers must check availability.

Test signals: Build coverage with and without `CONFIG_CPM`, `CONFIG_QUICC_ENGINE`, `CONFIG_FB_FSL_DIU`, and `CONFIG_EPAPR_PARAVIRT`; consumers should handle `-1` helper returns.

Source read size: 48 lines, 1265 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_soc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/ge/Makefile -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/ge/Makefile

Purpose: Selects the GE FPGA interrupt controller object for builds.

Important APIs/types/functions: Adds `ge_pic.o` when `CONFIG_GE_FPGA` is enabled.

Control flow: No runtime behavior; Kbuild conditionally includes the GE PIC driver.

State and persistence: No state.

Dependencies and integration points: Integrates with PowerPC board/platform Kconfig that selects `CONFIG_GE_FPGA` and with `ge_pic.c`.

Risks: Incorrect config selection omits the cascaded board PIC driver and breaks non-PCI on-board interrupt delivery on GE FPGA platforms.

Test signals: Build matrix with `CONFIG_GE_FPGA=y` and disabled, plus board boot checking that `ge_pic.o` is linked only when expected.

Source read size: 2 lines, 75 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/ge/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/ge/ge_pic.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/ge/ge_pic.c

Purpose: Implements a simple cascaded irqdomain driver for GE FPGA board interrupt controllers with 32 level-sensitive inputs.

Important APIs/types/functions: Public interfaces are `gef_pic_init()` and `gef_pic_get_irq()`. Internal elements include `gef_pic_chip`, `gef_pic_host_ops`, `gef_pic_cascade()`, mask/unmask helpers, OF xlate/map callbacks, and global `gef_pic_irq_reg_base`, `gef_pic_irq_host`, and `gef_pic_cascade_irq`.

Control flow: Initialization maps controller registers, masks CPU0/CPU1 interrupt and machine-check outputs, maps the parent cascade IRQ, creates a 32-entry linear irqdomain, and installs a chained handler. The chained handler calls `gef_pic_get_irq()` to find the highest active bit in `INTR_STATUS & CPU0_INTR_MASK`, dispatches the mapped Linux IRQ if present, and EOIs the parent. Child mask/unmask manipulates CPU0 mask bits under a raw spinlock.

State and persistence: Persistent state is the MMIO register base, irqdomain, parent cascade IRQ, and hardware mask registers. There is no per-child software cache; register reads are authoritative.

Dependencies and integration points: Depends on OF address/IRQ parsing, irqdomain, chained IRQ handling, big-endian MMIO, and GE board setup calling `gef_pic_init()`.

Risks: The driver only programs CPU0 mask registers and ignores the dual-output routing described in comments. There is no explicit error handling for failed `of_iomap()` before MMIO writes. Child interrupts have no real acknowledge operation, so devices must deassert their interrupt before unmask or level interrupts can retrigger.

Test signals: GE/SBC610 boot, interrupt delivery for each of 32 inputs, parent cascade EOI behavior, mask/unmask register checks, absent or malformed OF resources, and SMP tests confirming CPU0-only routing is intentional.

Source read size: 254 lines, 6934 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/ge/ge_pic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/ge/ge_pic.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/ge/ge_pic.h

Purpose: Declares the GE FPGA PIC setup and IRQ retrieval API for board code.

Important APIs/types/functions: Declares `gef_pic_get_irq()` and `gef_pic_init(struct device_node *)`.

Control flow: No runtime flow; this is an include guard and prototypes only.

State and persistence: No state in the header.

Dependencies and integration points: Consumed by GE platform code and implemented by `ge_pic.c`.

Risks: Minimal; callers must pass a valid device node to `gef_pic_init()` and install `gef_pic_get_irq()` only after initialization.

Test signals: Compile coverage for GE FPGA platforms and successful linkage against `ge_pic.o`.

Source read size: 9 lines, 190 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/ge/ge_pic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/grackle.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/grackle.c

Purpose: Sets up the MPC106/Grackle PCI host bridge and applies PowerMac-specific configuration quirks.

Important APIs/types/functions: Provides `setup_grackle()`, with helper `grackle_set_loop_snoop()` and config address macro `GRACKLE_CFA()`.

Control flow: `setup_grackle()` configures indirect PCI access at fixed Grackle config address/data windows. It enables all-bus reassignment on `PowerMac1,1` and turns on PICR1 loop snoop on `AAPL,PowerBook1998` by writing config register `0xa8`.

State and persistence: Persistent state is PCI host-controller config address/data mappings installed by `setup_indirect_pci()` and the hardware PICR1 loop-snoop bit.

Dependencies and integration points: Depends on indirect PCI helpers, OF machine compatibility checks, PCI reassignment flags, and Grackle host bridge platform setup.

Risks: Fixed physical config windows are platform-specific. The loop-snoop quirk is a hardware erratum workaround and must remain narrowly scoped to the affected PowerBook model.

Test signals: Old PowerMac/PowerBook boot, PCI enumeration through indirect config access, bus reassignment on PowerMac1,1, and loop-snoop register verification on PowerBook1998.

Source read size: 43 lines, 1274 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/grackle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/i8259.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/i8259.c

Purpose: Implements the legacy dual 8259 PIC irqdomain and low-level acknowledge/mask logic for PowerPC systems that expose ISA-style interrupts.

Important APIs/types/functions: Public APIs are `i8259_init()`, `i8259_irq()`, and `i8259_get_host()`. Key state includes `pci_intack`, cached masks `cached_8259`, raw spinlock `i8259_lock`, and `i8259_host`. IRQ chip callbacks are `i8259_mask_irq()`, `i8259_unmask_irq()`, and `i8259_mask_and_ack_irq()`.

Control flow: Initialization masks both PICs, programs 8086 mode/vector bases, enables the cascade on IRQ2, creates a legacy 16-IRQ domain, reserves IO resources, and optionally maps a PCI interrupt-acknowledge byte. Interrupt retrieval either reads PCI intack or polls the master/slave PICs, filters spurious IRQ7/0xff, and returns a legacy hardware IRQ number. Domain mapping marks IRQ2 no-request, uses level handling, and installs the i8259 chip.

State and persistence: Persistent state is cached master/slave mask bytes, actual PIC mask/ISR programming, optional mapped intack window, resource reservations, and the legacy irqdomain.

Dependencies and integration points: Uses x86-style I/O ports on PowerPC, OF irqdomain matching, legacy IRQ constants, PCI host bridge intack support, and platform `get_irq` code that cascades into `i8259_irq()`.

Risks: Polling is known broken on some PReP boxes, so correct intack configuration matters. All mapped IRQs are treated as level for simplicity. The resource reservations can conflict with later PCI IO resource claims, as the source comment notes.

Test signals: Legacy ISA interrupt delivery, spurious IRQ7 filtering, slave cascade IRQs 8-15, intack versus poll modes, mask/ack order, and boot on CHRP/PReP systems using i8259.

Source read size: 283 lines, 7076 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/i8259.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/indirect_pci.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/indirect_pci.c

Purpose: Provides generic indirect PCI config-space access for PowerPC host bridges with address/data config registers.

Important APIs/types/functions: Implements `__indirect_read_config()`, `indirect_read_config()`, `indirect_write_config()`, `setup_indirect_pci()`, and static `indirect_pci_ops`.

Control flow: Read/write helpers reject unsupported devices based on no-link and platform exclusion flags, compute type-0/type-1 config addressing, handle extended register bits, write the config address using big- or little-endian MMIO, and access the config data window at the offset lane. Write suppresses primary-bus writes and clears broken MRM cache-line-size writes when configured. Setup maps the address/data pages and installs the PCI ops into the controller.

State and persistence: Persistent state lives in `struct pci_controller`: `cfg_addr`, `cfg_data`, `ops`, and `indirect_type` flags. Hardware state changes occur through config cycles.

Dependencies and integration points: Depends on PowerPC PCI host bridge data, `ppc_md.pci_exclude_device`, endian MMIO helpers, and platform host setup code such as Grackle or embedded controllers.

Risks: No locking is done around shared config address/data registers, so callers must rely on PCI core serialization. Mis-set endian/type/extended flags produce silent bad config cycles. `PPC_INDIRECT_TYPE_NO_PCIE_LINK` only permits root device/function zero.

Test signals: PCI enumeration on indirect host bridges, config byte/word/dword reads and writes, type-1 access to subordinate buses, excluded-device handling, extended register offsets, and errata flags.

Source read size: 172 lines, 4486 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/indirect_pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/ipic.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/ipic.c

Purpose: Implements the Freescale Integrated Programmable Interrupt Controller driver, including irqdomain mapping, level/edge mask/ack/type operations, machine-check status helpers, and suspend/resume restore.

Important APIs/types/functions: Public APIs are `ipic_init()`, `ipic_set_default_priority()`, `ipic_get_mcp_status()`, `ipic_clear_mcp_status()`, and `ipic_get_irq()`. Important data are `primary_ipic`, `ipic_info[]`, `struct ipic`, `ipic_level_irq_chip`, `ipic_edge_irq_chip`, and saved suspend state.

Control flow: `ipic_init()` maps registers from OF, creates a 128-entry linear domain, configures spread/mix priority modes, MCP routing, IRQ0-to-MCP behavior, sets default domain, and masks internal interrupt groups. Domain mapping starts each IRQ as level-low and then `ipic_set_irq_type()` can switch external interrupt sources to falling-edge handling by programming `IPIC_SECNR`. Mask/unmask/ack operations use per-source register metadata from `ipic_info[]`. `ipic_get_irq()` reads `SIVCR`, returns zero for no pending vector, otherwise maps the hardware vector.

State and persistence: State is global and primary-only: mapped IPIC registers, irqdomain, source metadata table, raw spinlock, hardware mask/priority/sense/error registers, and optional suspend snapshot of all relevant controller registers.

Dependencies and integration points: Depends on OF address mapping, irqdomain one/two-cell translation, Freescale IPIC register constants from `asm/ipic.h`, PowerPC platform `ppc_md.get_irq`, syscore suspend/resume, and `fsl_deep_sleep()` behavior.

Risks: `ipic_info[]` is sparse; invalid hardware IRQs would index entries with zero masks unless guarded by valid DT/domain use. Only low-level and falling-edge senses are supported, with edge mode limited to external interrupts. `ipic_from_irq()` always returns `primary_ipic`, so multiple IPIC instances are not supported.

Test signals: Freescale IPIC board boot, level and external falling-edge interrupts, MCP status read/clear, priority register initialization, deep-sleep suspend/resume, malformed IRQ type requests, and irqdomain xlate/map coverage.

Source read size: 893 lines, 18942 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/ipic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/ipic.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/ipic.h

Purpose: Defines private IPIC constants, source metadata, and the controller object used by `ipic.c`.

Important APIs/types/functions: Defines `NR_IPIC_INTS`, external IRQ numbers, default priority value, SICFR/SEMSR/SERCR bit masks, `struct ipic`, and `struct ipic_info`.

Control flow: No runtime flow; the structures drive lookup logic in `ipic.c` for mask, priority, force, ack, and bit position.

State and persistence: `struct ipic` persists the MMIO register base and irqdomain. `struct ipic_info` describes immutable per-source register metadata.

Dependencies and integration points: Includes `asm/ipic.h` and is private to the IPIC sysdev implementation.

Risks: Metadata fields are tightly tied to the silicon register map. Any wrong bit or register offset would break mask/ack/sense behavior for that hardware source.

Test signals: Compile coverage and runtime validation that each documented IPIC source can be masked/unmasked/acked with the expected register bit.

Source read size: 56 lines, 1369 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/ipic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/mmio_nvram.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/mmio_nvram.c

Purpose: Registers a memory-mapped NVRAM backend with the PowerPC machine descriptor.

Important APIs/types/functions: Entry point is `mmio_nvram_init()`. Backend callbacks are `mmio_nvram_read()`, `mmio_nvram_write()`, `mmio_nvram_read_val()`, `mmio_nvram_write_val()`, and `mmio_nvram_get_size()`.

Control flow: Initialization finds a node of type or compatible `nvram`, translates its first resource, rejects zero address/length, maps it, logs the mapping, and fills `ppc_md.nvram_*` callbacks. Reads/writes clamp by current index and use `memcpy_fromio()`/`memcpy_toio()` under a spinlock. Byte callbacks return `0xff` or ignore writes past the mapped length.

State and persistence: Persistent state is `mmio_nvram_start`, `mmio_nvram_len`, spinlock, and registered `ppc_md` callback pointers. Data persistence is the underlying NVRAM hardware.

Dependencies and integration points: Uses OF address parsing, MMIO mapping, PowerPC NVRAM callback ABI, and generic NVRAM consumers.

Risks: There is no unmap path because this is boot-time machine setup. `loff_t *index` arithmetic assumes nonnegative offsets from callers. The code serializes access but does not implement hardware-specific write delays or verification.

Test signals: Device-tree NVRAM discovery, `/dev/nvram` read/write bounds checks, byte callback behavior at end of range, concurrent access, and boot without an NVRAM node.

Source read size: 145 lines, 3177 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/mmio_nvram.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/mpc5xxx_clocks.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/mpc5xxx_clocks.c

Purpose: Provides a firmware-node helper to locate MPC5xxx bus frequency properties.

Important APIs/types/functions: Exports `mpc5xxx_fwnode_get_bus_frequency()`.

Control flow: The helper first checks the supplied firmware node for `bus-frequency`; if absent, it walks parents until the property is found, releases the parent reference, and returns zero if no value exists.

State and persistence: No persistent state; all work is per-call firmware property lookup.

Dependencies and integration points: Uses generic firmware node property APIs and is exported for MPC512x/MPC52xx drivers that need IPS/IPB bus frequency.

Risks: It returns `0` on failure, so callers must treat zero as invalid. Parent traversal depends on correct firmware-node reference handling, which this function does with `fwnode_handle_put()` on early return.

Test signals: Drivers probing with local and inherited `bus-frequency`, absent property cases, and non-OF fwnode compatibility.

Source read size: 36 lines, 854 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/mpc5xxx_clocks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/mpic.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/mpic.c

Purpose: Implements the OpenPIC/MPIC interrupt controller driver for PowerPC, covering MMIO/DCR register access, irqdomain mapping, masking, EOI, IRQ type/affinity, IPIs, timers, cascaded secondary MPICs, Freescale extensions, U3/U4 HyperTransport workarounds, and suspend/resume save/restore.

Important APIs/types/functions: Exports `mpic_subsys`, `mpic_alloc()`, `mpic_assign_isu()`, `mpic_init()`, `mpic_unmask_irq()`, `mpic_mask_irq()`, `mpic_end_irq()`, `mpic_set_irq_type()`, `mpic_set_vector()`, `mpic_set_affinity()`, `mpic_irq_set_priority()`, `mpic_setup_this_cpu()`, `mpic_teardown_this_cpu()`, `mpic_cpu_get_priority()`, `mpic_cpu_set_priority()`, `mpic_get_one_irq()`, `mpic_get_irq()`, `mpic_get_coreint_irq()`, `mpic_get_mcirq()`, `mpic_request_ipis()`, `smp_mpic_message_pass()`, `smp_mpic_probe()`, `smp_mpic_setup_cpu()`, `mpic_reset_core()`, and `fsl_mpic_primary_get_version()`.

Control flow: Allocation finds or takes an OF node, infers flags and physical address, maps global/timer/per-CPU/ISU registers, computes reserved vectors for timers/IPIs/spurious, handles protected sources, resets hardware unless disabled, creates the irqdomain, and sets the default domain for primary MPICs. Initialization programs processor priority, timer vectors, IPI vectors, optional HT/MSI workarounds, source vector/priority/destination registers, spurious vector, passthrough disable, secondary cascade handler, and FSL error interrupt setup. Domain mapping separates IPIs, timer interrupts, error interrupts, protected/out-of-range sources, and normal sources; normal sources are initialized lazily when `MPIC_NO_RESET` is set. Runtime IRQ flow reads INTACK/EPR/MCACK, maps vectors to Linux IRQs, masks/unmasks by toggling VECPRI mask bits with polling, and EOIs through the current CPU EOI register.

State and persistence: Global state includes linked list `mpics`, `mpic_primary`, `mpic_lock`, per-instance register banks, flags, hardware register set, vector reservations, protected bitmap, irqdomain, chip templates, MSI bitmap, HT fixups, ISU geometry, and optional PM save data. Per-CPU priority and destination registers are hardware state. Suspend stores per-source vecpri/destination and resumes them, including HT fixup data.

Dependencies and integration points: Integrates with OF interrupt parsing, irqdomain, generic IRQ chips/handlers, SMP message IPIs, PowerPC `ppc_md.get_irq`, FSL MPIC error interrupt helpers in `mpic.h`, MPIC MSI helpers, syscore PM, PCI HT capability scanning, and DCR/MMIO endian accessors.

Risks: This is central interrupt routing code with subtle hardware variations. Miscomputed vector ranges can collide with IPIs/timers/spurious/error vectors. Mask/unmask loops can time out. U3/U4 HT fixups hard-code config-space behavior and Apple quirks. Several init failure paths intentionally leak mappings/objects. The driver supports only one primary MPIC for many exported helpers.

Test signals: Boot on OpenPIC, Freescale MPIC, secondary cascaded MPIC, and U3/U4 platforms; IRQ type and affinity changes; SMP IPI delivery; timer vector mapping; protected-source rejection; coreint/EPR path on BookE; suspend/resume; MSI allocation; and stress with spurious/protected vectors.

Source read size: 2022 lines, 52309 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/mpic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/mpic.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/mpic.h

Purpose: Declares internal MPIC adjunct interfaces for MSI and Freescale error-interrupt support.

Important APIs/types/functions: Declares `mpic_msi_reserve_hwirq()`, `mpic_msi_init_allocator()`, `mpic_u3msi_init()`, `mpic_pasemi_msi_init()`, core chip helpers `mpic_set_irq_type()`, `mpic_set_vector()`, `mpic_set_affinity()`, `mpic_reset_core()`, and FSL error helpers `mpic_map_error_int()`, `mpic_err_int_init()`, `mpic_setup_error_int()`, with stubs under disabled configs.

Control flow: Compile-time conditionals select real declarations or no-op/error-returning static inlines.

State and persistence: No state, but function declarations operate on persistent `struct mpic` state, MSI bitmaps, and FSL error vector arrays.

Dependencies and integration points: Included by `mpic.c`, `mpic_msi.c`, `mpic_u3msi.c`, and FSL error interrupt implementations.

Risks: Stub return values such as `-1` for unsupported MSI paths drive fallback behavior, so callers must handle them. FSL helper availability depends on `CONFIG_FSL_SOC`.

Test signals: Build coverage across `CONFIG_PCI_MSI`, `CONFIG_PPC_PASEMI`, and `CONFIG_FSL_SOC`.

Source read size: 60 lines, 1637 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/mpic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/mpic_msgr.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/mpic_msgr.c

Purpose: Provides a platform driver and exported API for Freescale MPIC message registers used as inter-device or inter-core message sources.

Important APIs/types/functions: Exports `mpic_msgr_get()`, `mpic_msgr_put()`, `mpic_msgr_enable()`, and `mpic_msgr_disable()`. Driver entry points include `mpic_msgr_probe()` and `mpic_msgr_init()`. Internal helpers count alias-defined blocks and derive block ordering.

Control flow: On first probe the driver counts `mpic-msgr-blockN` aliases to size the global register-pointer array. Each block maps its register resource, resolves its alias index, reads `mpic-msgr-receive-mask`, allocates four `struct mpic_msgr` objects, parses IRQs for receive-capable registers, disables each register, and stores it in the global array. Clients reserve a register with `mpic_msgr_get()`, enable/disable through MER bits, and release via `mpic_msgr_put()`.

State and persistence: Persistent state includes global `mpic_msgrs`, `mpic_msgr_count`, global allocation lock, per-message-register MMIO base/MER pointer, IRQ number, in-use flag, register number, and per-register lock.

Dependencies and integration points: Depends on OF aliases, platform devices, MPIC message-register bindings, irq parsing, big-endian MMIO, and `asm/mpic_msgr.h` client structures.

Risks: `mpic_msgr_get()` initializes `msgr` to `ERR_PTR(-EBUSY)` but unconditionally assigns `mpic_msgrs[reg_num]`; if a sparse slot was never probed, callers can receive NULL. Probe failures after partial allocation do not clean up earlier registers. Alias ordering is mandatory.

Test signals: Device-tree alias order tests, receive-mask/IRQ parsing, concurrent get/put, MER bit enable/disable verification, sparse/missing alias behavior, and client interrupt delivery.

Source read size: 285 lines, 6943 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/mpic_msgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/mpic_msi.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/mpic_msi.c

Purpose: Initializes and maintains the MPIC MSI hardware interrupt bitmap allocator.

Important APIs/types/functions: Provides `mpic_msi_reserve_hwirq()` and `mpic_msi_init_allocator()`, plus U3-specific reserve helper `mpic_msi_reserve_u3_hwirqs()` when HT IRQ support is enabled.

Control flow: Allocator init creates an MSI bitmap sized to MPIC sources, reserves device-tree-specified unavailable ranges, and if no DT ranges exist on U3/U4 hardware, reserves known non-MSI source ranges and every hwirq already referenced by OF interrupts. Runtime reservation marks MPIC hwirqs unavailable when normal IRQs are mapped.

State and persistence: Operates on `mpic->msi_bitmap`, which persists reserved/free hardware source state for MSI allocation.

Dependencies and integration points: Depends on `msi_bitmap.c`, MPIC irqdomain xlate ops, OF IRQ scanning, PCI MSI config, and U3/U4 MPIC setup.

Risks: U3 fallback reservation is heuristic and scans all OF nodes; incorrect reservation can allocate an MSI source already used by a wired interrupt. If DT `msi-available-ranges` is malformed, MSI allocator setup fails.

Test signals: MSI allocation with valid DT ranges, missing-range U3 fallback, reservation of wired interrupts, normal IRQ mapping reserving hwirqs, and failure cleanup.

Source read size: 99 lines, 2352 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/mpic_msi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/mpic_timer.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/mpic_timer.c

Purpose: Implements an exported allocator/control API for Freescale MPIC global timers, including long-duration cascaded timer pairs.

Important APIs/types/functions: Exports `mpic_request_timer()`, `mpic_start_timer()`, `mpic_stop_timer()`, `mpic_get_remain_time()`, and `mpic_free_timer()`. Important types are `timer_regs`, `cascade_priv`, `timer_group_priv`, and `struct mpic_timer` from `asm/mpic_timer.h`.

Control flow: Subsys init scans `fsl,mpic-global-timer` nodes and initializes each timer group by mapping timer registers and TCR, deriving frequency, parsing available timer IRQ ranges, setting idle bits, applying clock divider, and adding the group to a global list. Requests convert seconds to ticks, pick an idle single timer or cascade pair, program base/current counts stopped, request the timer IRQ, and return a handle. Start clears `TIMER_STOP`; stop sets it and clears current counts; free stops, frees IRQ, clears cascade mode if used, and marks timers idle.

State and persistence: Persistent state is `timer_group_list`, per-group MMIO/TCR mappings, timer frequency, idle bitmap, per-timer IRQ/number/dev/cascade handle, and cascade TCR bits. Hardware counter/base/count registers hold live timer state.

Dependencies and integration points: Depends on OF resources/IRQs, MPIC global timer hardware, `fsl,mpic` clock-frequency, syscore resume, exported timer clients, and IRQF_TRIGGER_LOW timer interrupts.

Risks: Time arguments are `time64_t` seconds converted directly to ticks; precision is coarse and overflow is rejected. Cascade allocation consumes adjacent timers and must correctly restore TCR bits on free. `mpic_request_timer()` calls `mpic_free_timer()` on `request_irq()` failure even though IRQ was not registered, so failure paths rely on `free_irq()` tolerance through that helper.

Test signals: Timer request/start/stop/free, remaining-time reads, cascade long-duration allocation, available-ranges parsing, frequency/divider correctness, IRQ firing, resume reinitialization, and concurrent timer allocation.

Source read size: 560 lines, 12761 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/mpic_timer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/mpic_u3msi.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/mpic_u3msi.c

Purpose: Provides legacy U3/U4 PowerMac MPIC MSI setup using HyperTransport MSI mapping or U4 bridge magic addresses.

Important APIs/types/functions: Entry point is `mpic_u3msi_init()`. MSI hooks are `u3msi_setup_msi_irqs()` and `u3msi_teardown_msi_irqs()`. IRQ chip is `mpic_u3msi_chip`; address helpers are `find_ht_magic_addr()` and `find_u4_magic_addr()`.

Control flow: Init creates the MPIC MSI allocator, stores the global MPIC pointer, and installs MSI setup/teardown callbacks on every PCI host bridge. Setup verifies a usable magic MSI address, allocates one MPIC hwirq per MSI descriptor, creates an irqdomain mapping, attaches the MSI descriptor, overrides the chip/type, writes the MSI address/data, and leaves MPIC/pci MSI mask handling to the chip callbacks. Teardown clears descriptors, disposes mappings, zeros descriptor IRQs, and frees hwirqs.

State and persistence: Uses global `msi_mpic`, MPIC MSI bitmap allocations, per-MSI Linux IRQ mappings, and PCI device MSI messages. Hardware address selection persists in device MSI capability/programming.

Dependencies and integration points: Depends on MPIC core, `msi_bitmap`, PCI MSI descriptor iteration, HT MSI mapping capability, U4 PCIe bridge compatibility strings, and global `hose_list`.

Risks: The implementation is explicitly U3/U4-specific and relies on magic bridge addresses. MSI-X is marked untested. `u3msi_setup_msi_irqs()` increments a local `hwirq` after writing each message even though each loop allocates a fresh hwirq, which is harmless locally but confusing. Partial setup failure can leave prior descriptors allocated until teardown.

Test signals: U3/U4 PowerMac MSI-capable PCI devices, MSI mask/unmask order, teardown after partial allocation, MSI-X smoke tests if used, and hwirq reservation collision checks.

Source read size: 196 lines, 5180 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/mpic_u3msi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/msi_bitmap.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/msi_bitmap.c

Purpose: Implements a generic bitmap allocator for PowerPC MSI hardware interrupt numbers, including device-tree available-range reservation and optional selftests.

Important APIs/types/functions: Exports `msi_bitmap_alloc_hwirqs()`, `msi_bitmap_free_hwirqs()`, `msi_bitmap_reserve_hwirq()`, `msi_bitmap_reserve_dt_hwirqs()`, `msi_bitmap_alloc()`, and `msi_bitmap_free()`.

Control flow: Allocation finds a naturally aligned zero area matching the requested vector count, marks it allocated under a spinlock, and returns the offset. Free clears a range. DT reservation defaults all bits reserved, then releases only ranges listed in `msi-available-ranges`. Allocator setup uses slab allocation after slab init or memblock before slab is available; free releases only slab-backed bitmaps.

State and persistence: `struct msi_bitmap` persists bitmap pointer, IRQ count, OF node reference, spinlock, and allocation origin flag. Bitmap bits represent allocated/reserved hwirqs.

Dependencies and integration points: Used by MPIC MSI and other PowerPC MSI controllers. Depends on bitmap APIs, OF property parsing, memblock early allocation, kmemleak annotation, and optional `CONFIG_MSI_BITMAP_SELFTEST`.

Risks: `msi_bitmap_reserve_hwirq()` uses `bitmap_allocate_region()` without checking failure; invalid hwirqs can warn or misbehave. `msi_bitmap_free_hwirqs()` trusts caller ranges. DT available ranges are interpreted as exact free hwirq ranges, so malformed or incomplete bindings can starve MSI allocation.

Test signals: Built-in selftests cover allocation, exhaustion, alignment, free/reuse, null OF node, and fake `msi-available-ranges`. Additional runtime signals are multi-vector MSI allocation and early-boot allocator use before slab.

Source read size: 273 lines, 7447 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/msi_bitmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/of_rtc.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/of_rtc.c

Purpose: Instantiates legacy MMIO RTC platform devices from device-tree compatible strings.

Important APIs/types/functions: Provides `of_instantiate_rtc()` and static mapping table from `ds1743-nvram` to platform device name `rtc-ds1742`.

Control flow: Iterates each table entry and compatible node, allocates a resource, translates the first address range, logs the device, and registers a simple platform device with that resource.

State and persistence: No global state. Registered platform devices and allocated resources persist for the device lifetime.

Dependencies and integration points: Depends on OF compatible/address APIs and platform bus registration for RTC drivers.

Risks: If address translation fails after resource allocation, the resource is leaked. Device registration return value is not checked. The table is narrow and only covers DS1743-as-DS1742.

Test signals: Device-tree node instantiation, resource translation failure paths, platform driver binding to `rtc-ds1742`, and boot without matching RTC nodes.

Source read size: 59 lines, 1395 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/of_rtc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/rtc_cmos_setup.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/rtc_cmos_setup.c

Purpose: Registers a PC-style `rtc_cmos` platform device on PowerPC systems with a compatible CMOS RTC node.

Important APIs/types/functions: Main function is initcall `add_rtc()`.

Control flow: Finds compatible `pnpPNP,b00`, translates its IO resource, verifies it matches hard-coded `RTC_PORT(0)`, optionally adds fixed IRQ 8 when an i8259-compatible interrupt controller is present, and registers `rtc_cmos`.

State and persistence: No global state; the platform device and resources persist after registration.

Dependencies and integration points: Depends on OF address parsing, `asm/mc146818rtc.h` port constants, i8259/CHRP compatible nodes, platform bus, and the generic `rtc_cmos` driver.

Risks: Hard-coded IRQ 8 is correct only for the legacy i8259 numbering assumption described in the comments. If firmware reports a different RTC IO base, the driver refuses to instantiate.

Test signals: CHRP/PReP boot with CMOS RTC, missing interrupt controller node, IO base mismatch, and `rtc_cmos` driver binding.

Source read size: 70 lines, 1645 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/rtc_cmos_setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/tsi108_dev.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/tsi108_dev.c

Purpose: Provides Tundra TSI108/109 bridge common device setup, especially CSR base discovery and Ethernet platform-device creation from OF nodes.

Important APIs/types/functions: Exports `get_csrbase()` and `get_vir_csrbase()`. Initcall `tsi108_eth_of_init()` creates `tsi-ethernet` platform devices and fills `hw_info`.

Control flow: CSR helpers lazily find the `tsi-bridge` resource and map CSR space. Ethernet init scans `network` nodes compatible with `tsi108-ethernet`, translates MAC resources/IRQs, registers a platform device, extracts MAC address, MDIO and PHY phandles/resources, PHY id, IRQ number, and optional `txc-rxc-delay-disable` workaround flag, then attaches platform data.

State and persistence: Persistent state is cached physical CSR base, mappings returned by `get_vir_csrbase()`, and registered Ethernet platform devices with copied hardware info.

Dependencies and integration points: Depends on OF address/IRQ/net helpers, TSI108 register definitions, platform bus, legacy `tsi-ethernet` driver, and PHY/MDIO phandles.

Risks: `get_vir_csrbase()` maps CSR space on every call and returns a truncated `u32` virtual address. Ethernet registration passes only one resource even though it constructs an IRQ resource separately, relying on platform data for IRQ. Missing `mdio-handle`/`phy-handle` properties are not defensively checked before dereference.

Test signals: TSI108 board boot, Ethernet platform device creation, MAC/PHY/MDIO property parsing, workaround property behavior, and leak/error-path testing for missing phandles.

Source read size: 153 lines, 3596 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/tsi108_dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/tsi108_pci.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/tsi108_pci.c

Purpose: Implements TSI108 PCI host bridge config access and a cascaded PCI INTx interrupt router.

Important APIs/types/functions: Provides `tsi108_setup_pci()`, `tsi108_direct_read_config()`, `tsi108_direct_write_config()`, `tsi108_clear_pci_error()`, `tsi108_clear_pci_cfg_error()`, `tsi108_pci_int_init()`, and `tsi108_irq_cascade()`. Static router helpers include `get_pci_source()`, `tsi108_pci_int_mask()`, and `tsi108_pci_int_unmask()`.

Control flow: PCI setup maps the config window, allocates a PCI controller, sets bus range and direct config ops, logs the bridge, and processes OF ranges. Config reads use inline asm with exception-table fixup so absent devices return all ones; writes directly update little-endian config data. Error cleanup clears PB and PCI/X error status after failed config reads. Interrupt init creates a legacy irqdomain and enables the PCI block interrupt source. Cascade handling reads TSI108 PCI interrupt status, round-robins active INTA-D bits, disables the block source, dispatches the selected IRQ, then EOIs the parent.

State and persistence: Global state includes config virtual/physical base, CSR virtual base, PCI IRQ domain, static round-robin mask in `get_pci_source()`, and hardware IRP config/enable/status registers.

Dependencies and integration points: Depends on TSI108 CSR accessors, PowerPC PCI host bridge code, OF ranges, generic IRQ domain/chained IRQ, MPIC parent interrupt, and legacy IRQ numbering constants from `tsi108_irq.h`.

Risks: Several virtual addresses are stored in `u32`, which is unsafe on wider address builds. `pci_irq_host_map()` tests Linux virq values 1..4 and then configures fixed legacy IRQs instead of using the provided virq directly, which is unusual and tightly coupled to legacy numbering. Cascade disables PCI block interrupts until child unmask reenables them.

Test signals: PCI enumeration including absent-device reads, PB/PCI error clearing, INT A-D routing, chained parent IRQ behavior, OF bus ranges/ranges parsing, and 32-bit address assumptions.

Source read size: 426 lines, 10707 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/tsi108_pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/udbg_memcons.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/udbg_memcons.c

Purpose: Provides a memory-backed early debug console for PowerPC udbg output and polling input.

Important APIs/types/functions: Defines `struct memcons`, global `memcons`, `memcons_putc()`, `memcons_getc_poll()`, `memcons_getc()`, and `udbg_init_memcons()`.

Control flow: Initialization installs udbg callbacks. Output writes one byte at `output_pos`, issues a write memory barrier, and advances circularly. Input polling checks the current input byte, advances circularly or wraps to start on NUL, clears consumed bytes, barriers, and returns `-1` when empty. Blocking get spins with `cpu_relax()` until input appears.

State and persistence: Persistent static buffers are sized by `CONFIG_PPC_MEMCONS_OUTPUT_SIZE` and `CONFIG_PPC_MEMCONS_INPUT_SIZE`. Global `memcons` exposes buffer starts/positions/ends for external inspection/injection.

Dependencies and integration points: Depends on PowerPC udbg callback globals, memory barriers, and early debug users that can inspect or populate the buffers.

Risks: There is no locking; this is early/debug infrastructure and concurrent writers/readers can race. The output ring overwrites old data. Input emptiness relies on zero-filled/zero-cleared bytes.

Test signals: Early boot debug output, wraparound behavior, injected input consumption, and visibility of `memcons` from debugger or simulator.

Source read size: 100 lines, 2205 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/udbg_memcons.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xics/Kconfig -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xics/Kconfig

Purpose: Defines internal Kconfig symbols for the legacy XICS interrupt controller stack.

Important APIs/types/functions: Symbols are `PPC_XICS`, `PPC_ICP_NATIVE`, `PPC_ICP_HV`, `PPC_ICS_RTAS`, and `PPC_ICS_NATIVE`. `PPC_XICS` selects `PPC_SMP_MUXED_IPI` and `HARDIRQS_SW_RESEND`.

Control flow: No runtime behavior; platform Kconfig selects the relevant ICP/ICS backends.

State and persistence: No state.

Dependencies and integration points: Controls compilation of `xics-common.o`, ICP backends, and ICS backends through the sibling Makefile.

Risks: These are `def_bool n` internal symbols; missing platform selects produce no XICS implementation even if the hardware exists.

Test signals: Build coverage for pseries/PowerNV native, hypervisor, RTAS, and native source-controller combinations.

Source read size: 17 lines, 250 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xics/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xics/Makefile -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xics/Makefile

Purpose: Selects XICS common code and backend objects for PowerPC builds.

Important APIs/types/functions: Always builds `xics-common.o` in the directory; conditionally builds `icp-native.o`, `icp-hv.o`, `ics-rtas.o`, `ics-native.o`, and PowerNV `ics-opal.o`/`icp-opal.o`.

Control flow: No runtime behavior; object inclusion follows Kconfig symbols.

State and persistence: No state.

Dependencies and integration points: Ties `PPC_XICS` backend selections to object files used by pseries and PowerNV interrupt setup.

Risks: `xics-common.o` depends on exactly one usable ICP and usually one ICS being registered at runtime; build selection must match firmware/hardware.

Test signals: Link/build tests for LPAR HV, native XICS, RTAS ICS, native ICS, and PowerNV OPAL fallback combinations.

Source read size: 8 lines, 281 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xics/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xics/icp-hv.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xics/icp-hv.c

Purpose: Implements the XICS Interrupt Presentation Controller backend using pSeries hypervisor hcalls.

Important APIs/types/functions: Entry point is `icp_hv_init()`. Backend operations are `icp_hv_get_irq()`, `icp_hv_eoi()`, `icp_hv_set_cpu_priority()`, `icp_hv_teardown_cpu()`, `icp_hv_flush_ipi()`, and SMP `icp_hv_cause_ipi()`/`icp_hv_ipi_action()`. Low-level helpers wrap `H_XIRR`, `H_CPPR`, `H_EOI`, and `H_IPI`.

Control flow: Init checks for an XICP OF node and installs `icp_hv_ops`. Interrupt retrieval calls `H_XIRR` with the current CPPR top, maps the returned vector, pushes CPPR for mapped interrupts, masks and EOIs unknown vectors, and returns zero for spurious. EOI pops CPPR and calls `H_EOI`. IPI send writes MFRR with `H_IPI`; IPI handler clears it to `0xff` and demuxes SMP messages.

State and persistence: Persistent state is the global `icp_ops` pointer and per-CPU XICS CPPR stack maintained by common code. Hypervisor-maintained CPPR/XIRR/MFRR state is mutated through hcalls.

Dependencies and integration points: Depends on pSeries hypervisor calls, XICS common domain/CPPR helpers, OF XICP nodes, SMP IPI demux, and firmware feature selection in `xics_init()`.

Risks: Hcall failures warn but leave the kernel with limited recovery; `icp_hv_set_xirr()` falls back to setting CPPR after bad EOI. Correct CPPR stack pairing between get_irq/retrigger/EOI is critical.

Test signals: LPAR pseries boot, external interrupt delivery, IPI send/clear, CPU teardown/kexec, unknown vector masking, and hcall failure injection if available.

Source read size: 181 lines, 3840 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xics/icp-hv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xics/icp-native.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xics/icp-native.c

Purpose: Implements the native MMIO XICS Interrupt Presentation Controller backend.

Important APIs/types/functions: Entry point is `icp_native_init()`. Important functions are `icp_native_get_irq()`, exported `icp_native_eoi()`, `icp_native_set_cpu_priority()`, `icp_native_teardown_cpu()`, `icp_native_flush_ipi()`, `icp_native_flush_interrupt()`, exported `xics_wake_cpu()`, and SMP `icp_native_cause_ipi()`/`icp_native_ipi_action()`.

Control flow: Init scans `ibm,ppc-xicp` or `PowerPC-External-Interrupt-Presentation` nodes, maps each ICP MMIO range to a Linux CPU by hard CPU id, reserves memory, and records KVM XICS physical addresses. Runtime `get_irq` first consumes KVM-latched XICS interrupts, then reads XIRR, maps the vector, pushes CPPR, or masks/EOIs unknown vectors. EOI writes popped CPPR plus hwirq to XIRR. IPIs set QIRR/MFRR and use KVM host IPI latches.

State and persistence: State is `icp_native_regs[NR_CPUS]`, global `icp_ops`, KVM XICS physical-address registration, per-CPU CPPR stack, and hardware XIRR/QIRR registers.

Dependencies and integration points: Depends on OF address/range parsing, hard CPU id mapping, KVM PowerPC XICS latch hooks, SMP IPI demux, XICS common code, and memory resource reservation.

Risks: Source comments call out the assumption that interrupt server numbers match hard CPU numbers. Failed `request_mem_region()` leaks the allocated resource-name string. Offline interrupt flushing must correctly distinguish IPIs from external interrupts or it disables unknown vectors.

Test signals: Native XICS bare-metal boot, CPU hotplug/offline interrupt flushing, KVM host IPI latch behavior, MMIO mapping for every present CPU, and unknown-vector handling.

Source read size: 325 lines, 7101 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xics/icp-native.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xics/icp-opal.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xics/icp-opal.c

Purpose: Implements an OPAL-backed XICS ICP fallback for PowerNV systems.

Important APIs/types/functions: Entry point is `icp_opal_init()`. Backend operations are `icp_opal_get_irq()`, `icp_opal_eoi()`, `icp_opal_set_cpu_priority()`, `icp_opal_teardown_cpu()`, `icp_opal_flush_ipi()`, and SMP `icp_opal_cause_ipi()`/`icp_opal_ipi_action()` plus `icp_opal_flush_interrupt()`.

Control flow: Init checks for `ibm,opal-intc` and installs `icp_opal_ops`. Interrupt retrieval first handles KVM-latched interrupts, then calls `opal_int_get_xirr()`, maps/pushes CPPR or masks/EOIs unknown vectors. EOI calls `opal_int_eoi()` and forces external IRQ replay when OPAL reports more pending work. Priority setting maps requests at or above default priority to lowest priority because OPAL XIVE cannot represent the XICS "IPIs only" priority.

State and persistence: Persistent state is global `icp_ops`, per-CPU CPPR stack, OPAL CPPR/MFRR/XIRR state, and KVM host IPI latches.

Dependencies and integration points: Depends on OPAL interrupt calls, PowerNV firmware feature/nodes, XICS common code, KVM PowerPC hooks, and force-external-replay machinery.

Risks: Priority semantics are approximate on OPAL XIVE, as the source comment warns. OPAL errors during get_xirr return no interrupt without detailed recovery. Replay behavior is required to avoid losing pending interrupts after EOI.

Test signals: PowerNV XICS fallback boot, OPAL interrupt delivery, IPI delivery/clear, offline CPU flush loop, CPPR priority behavior during CPU hotplug, and forced replay on OPAL EOI positive return.

Source read size: 202 lines, 4441 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xics/icp-opal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xics/ics-native.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xics/ics-native.c

Purpose: Implements a native MMIO XICS Interrupt Source Controller backend for `openpower,xics-sources`.

Important APIs/types/functions: Entry point is `ics_native_init()`. Main callbacks are `ics_native_startup()`, `ics_native_mask_irq()`, `ics_native_unmask_irq()`, `ics_native_set_affinity()`, `ics_native_check()`, `ics_native_mask_unknown()`, `ics_native_get_server()`, and `ics_native_host_match()`. Private state is `struct ics_native`.

Control flow: Init patches the irq chip EOI from `icp_ops`, scans compatible nodes, maps each source controller, reads `interrupt-ranges`, records base/count, and registers the first ICS with common XICS. Unmask computes a target server with `xics_get_irq_server()` and writes server/priority into the XIVE word. Mask writes priority `0xff`. Startup also unmasks PCI MSI at the generic MSI layer when present.

State and persistence: Persistent state includes mapped XIVE table base, OF node reference, interrupt base/count, registered `struct ics`, and XIVE register contents for server/priority.

Dependencies and integration points: Depends on XICS common ICP EOI, OF address and `interrupt-ranges`, PCI MSI mask helpers, irq affinity, and big-endian MMIO.

Risks: Only one interrupt range is supported; extra ranges are warned and ignored. Only one global ICS can be registered by common code, so multiple source controllers are limited. Out-of-range operations silently return in mask/unmask but fail in check/affinity.

Test signals: Native OpenPOWER XICS source delivery, interrupt-range parsing, PCI MSI startup unmask, affinity changes, unknown-vector masking, and multiple-source-controller DT behavior.

Source read size: 254 lines, 6156 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xics/ics-native.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xics/ics-opal.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xics/ics-opal.c

Purpose: Implements an OPAL-managed XICS Interrupt Source Controller backend.

Important APIs/types/functions: Entry point is `ics_opal_init()`. IRQ callbacks are `ics_opal_startup()`, `ics_opal_mask_irq()`, `ics_opal_unmask_irq()`, and `ics_opal_set_affinity()`. Source-controller callbacks are `ics_opal_check()`, `ics_opal_mask_unknown()`, `ics_opal_get_server()`, and `ics_opal_host_match()`.

Control flow: Init checks OPAL firmware, patches EOI from `icp_ops`, and registers a single global ICS. Unmask chooses an XICS server, mangles it by left-shifting for OPAL link encoding, and calls `opal_set_xive()` with default priority. Mask sets priority to `0xff`. Affinity reads the existing XIVE priority, computes a new server, and writes it back. Check and get_server call `opal_get_xive()`.

State and persistence: Persistent state is the global `ics_hal` struct and OPAL XIVE server/priority state for each hardware IRQ.

Dependencies and integration points: Depends on OPAL firmware calls, XICS common affinity/type/retrigger helpers, ICP EOI callback, and PowerNV firmware feature detection.

Risks: `ics_opal_host_match()` matches all nodes, so this backend claims broad interrupt-parent space once registered. Server mangling currently assumes no link. OPAL call failures are logged but often only return failure to generic IRQ code.

Test signals: PowerNV OPAL XICS interrupt delivery, affinity migration, mask/unmask, unknown-vector mask, OPAL get/set error handling, and MSI/device interrupts using OPAL XIVE state.

Source read size: 221 lines, 5178 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xics/ics-opal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xics/ics-rtas.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xics/ics-rtas.c

Purpose: Implements the RTAS-backed XICS Interrupt Source Controller backend for pSeries-style firmware.

Important APIs/types/functions: Entry point is `ics_rtas_init()`. IRQ chip callbacks are `ics_rtas_startup()`, `ics_rtas_mask_irq()`, `ics_rtas_unmask_irq()`, and `ics_rtas_set_affinity()`. Source-controller callbacks include `ics_rtas_check()`, `ics_rtas_mask_unknown()`, `ics_rtas_get_server()`, and `ics_rtas_host_match()`.

Control flow: Init obtains RTAS tokens for `ibm,get-xive`, `ibm,set-xive`, `ibm,int-on`, and `ibm,int-off`, patches EOI from `icp_ops`, and registers the global ICS if required tokens exist. Unmask sets server/default priority with RTAS, then enables the interrupt. Mask disables the interrupt and sets priority `0xff`. Affinity gets current XIVE, computes a target server, and updates only the server while preserving priority. Check probes firmware awareness with `ibm,get-xive`.

State and persistence: Persistent state is RTAS token integers, global `ics_rtas`, and firmware-maintained XIVE server/priority/on-off state.

Dependencies and integration points: Depends on RTAS services, XICS common type/retrigger/affinity helpers, ICP EOI callback, and OF host matching that excludes legacy `chrp,iic`.

Risks: `ibm_int_on/off` tokens are not checked for unknown service even though used. RTAS calls can fail at runtime and only log errors. Host matching intentionally matches almost everything except legacy i8259, which must stay compatible with pseries device-tree conventions.

Test signals: pSeries RTAS XICS boot, interrupt mask/unmask and affinity calls, missing RTAS token fallback, legacy i8259 exclusion, unknown interrupt masking, and CPU hotplug migration.

Source read size: 225 lines, 5538 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xics/ics-rtas.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xics/xics-common.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xics/xics-common.c

Purpose: Provides common XICS interrupt-controller orchestration across ICP presentation backends and ICS source-controller backends.

Important APIs/types/functions: Defines global `icp_ops`, `xics_host`, default server variables, per-CPU `xics_cppr`, and registered `xics_ics`. Public functions include `xics_init()`, `xics_register_ics()`, `xics_setup_cpu()`, `xics_teardown_cpu()`, `xics_kexec_teardown_cpu()`, `xics_update_irq_servers()`, `xics_set_cpu_giq()`, `xics_smp_probe()`, `xics_migrate_irqs_away()`, `xics_get_irq_server()`, `xics_set_irq_type()`, `xics_retrigger()`, and `xics_mask_unknown_vec()`.

Control flow: `xics_init()` selects an ICP backend in hypervisor/native/OPAL order, installs `ppc_md.get_irq`, patches IPI EOI, selects an ICS backend in RTAS/OPAL/native order, reads interrupt-server size, updates default servers, creates the XICS irqdomain, and sets up the boot CPU. Domain mapping installs a percpu IPI chip for `XICS_IPI` and delegates normal source validation/chip data to the registered ICS. SMP setup maps/request IPIs and installs `smp_ops->cause_ipi`. CPU teardown lowers priority, flushes IPIs, and adjusts global interrupt queue membership. CPU hotplug migration masks local external delivery, leaves the GIQ, walks mapped IRQs, and resets single-server interrupts to all CPUs.

State and persistence: Persistent state includes selected backend operation table, source-controller object, irqdomain, default server/distribution server IDs, interrupt-server bit width, per-CPU CPPR stacks, IPI chip patched with backend EOI, and firmware GIQ membership.

Dependencies and integration points: Depends on XICS ICP/ICS backends, OF CPU and interrupt nodes, RTAS indicators, irqdomain hierarchy, SMP IPI framework, generic IRQ descriptors, PowerPC firmware features, and `ppc_md.get_irq`.

Risks: Common code assumes one global ICS. CPPR push/pop pairing is fragile, especially with retrigger and CPU teardown. `xics_get_irq_server()` implements only all-CPU or single-CPU delivery. Hotplug migration iterates all IRQ descriptors with interrupts disabled and relies on backend `get_server()` correctness.

Test signals: pSeries and PowerNV boot across ICP/ICS combinations, IPIs, IRQ type setting and resend, CPU hotplug/offline migration, kexec teardown, unknown-vector masking, hierarchy-domain allocation, and affinity changes with all-cpus versus single-cpu masks.

Source read size: 544 lines, 13374 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xics/xics-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xive/Kconfig -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xive/Kconfig

Purpose: Defines build symbols for the newer PowerPC XIVE interrupt controller stack.

Important APIs/types/functions: Symbols are `PPC_XIVE`, `PPC_XIVE_NATIVE`, and `PPC_XIVE_SPAPR`. `PPC_XIVE` selects muxed SMP IPIs and software hardirq resend; native depends on PowerNV; native and sPAPR select common XIVE.

Control flow: No runtime behavior; symbols control compilation of XIVE common/native/sPAPR objects.

State and persistence: No state.

Dependencies and integration points: Used by the xive Makefile and platform Kconfig for PowerNV and pseries XIVE support.

Risks: Missing selection omits interrupt-controller support. The native dependency on `PPC_POWERNV` must stay aligned with platform firmware capabilities.

Test signals: Build coverage for PowerNV native XIVE, sPAPR XIVE, and disabled XIVE configurations.

Source read size: 14 lines, 227 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xive/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xive/Makefile -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xive/Makefile

Purpose: Selects XIVE object files for PowerPC builds.

Important APIs/types/functions: Always builds `common.o`; conditionally builds `native.o` for `CONFIG_PPC_XIVE_NATIVE` and `spapr.o` for `CONFIG_PPC_XIVE_SPAPR`.

Control flow: No runtime flow; Kbuild object selection only.

State and persistence: No state.

Dependencies and integration points: Connects XIVE Kconfig symbols to the common, native PowerNV, and sPAPR backend implementations.

Risks: Common code is always included when this directory is entered, so platform Makefile/Kconfig selection must only enter the directory when XIVE support is intended.

Test signals: Link/build tests for native-only, sPAPR-only, both-enabled, and XIVE-disabled platform configurations.

Source read size: 5 lines, 144 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xive/Makefile -->
