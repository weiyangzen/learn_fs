# Research Report: subset-b-000758

This grouped report covers the PA-RISC kernel files assigned to `subset-b-000758`. Each file section is bounded by the required reconciliation markers and is intended to be split into the source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/firmware.c -->
# sources/distributed-fs/ceph-client/arch/parisc/kernel/firmware.c

## Purpose

`firmware.c` is the PA-RISC Processor Dependent Code (PDC) access layer. It serializes firmware calls, hides 32-bit versus 64-bit firmware calling width, provides wrappers for model, memory, device, PCI, stable storage, TOD, reset, console IODC, and PAT services, and exports selected helpers to drivers. The file is central to boot-time discovery, runtime firmware services, panic paths, and legacy console I/O.

## Important APIs, Types, And Functions

The shared state is `pdc_lock`, `pdc_result[]`, and `pdc_result2[]`. Almost every wrapper holds `pdc_lock` while calling `mem_pdc_call()` and while consuming the static buffers. On 64-bit kernels `parisc_narrow_firmware` tracks whether MEM_PDC must be called through `real32_call()` or `real64_call()`.

Width conversion is handled by `set_firmware_width_unlocked()`, `set_firmware_width()`, `convert_to_wide()`, and `f_extend()`. These are required because narrow firmware returns 32-bit values that may need widening or sign extension into kernel addresses.

Discovery and model wrappers include `pdc_system_map_find_mods()`, `pdc_system_map_find_addrs()`, `pdc_model_info()`, `pdc_model_sysmodel()`, `pdc_model_versions()`, `pdc_model_cpuid()`, `pdc_model_capabilities()`, `pdc_cache_info()`, `pdc_spaceid_bits()`, `pdc_btlb_info()`, `pdc_mem_map_hpa()`, and `pdc_mem_mem_table()`.

Device and platform wrappers include `pdc_iodc_read()`, `pdc_lan_station_id()`, `pdc_get_initiator()`, `pdc_pci_irt_size()`, `pdc_pci_irt()`, `pdc_tod_read()`, `pdc_tod_set()`, `pdc_soft_power_info()`, `pdc_soft_power_button()`, `pdc_soft_power_button_panic()`, `pdc_io_reset()`, and `pdc_io_reset_devices()`.

Persistent firmware state APIs include `pdc_stable_read()`, `pdc_stable_write()`, `pdc_stable_get_size()`, `pdc_stable_verify_contents()`, and `pdc_stable_initialize()`. PAT-only 64-bit APIs include `pdc_pat_cell_get_number()`, `pdc_pat_cell_module()`, `pdc_pat_cell_info()`, `pdc_pat_cpu_get_number()`, `pdc_pat_get_irt_size()`, `pdc_pat_get_irt()`, `pdc_pat_pd_get_addr_map()`, `pdc_pat_pd_get_pdc_revisions()`, `pdc_pat_pd_get_platform_counter()`, PAT PCI config helpers, and PAT memory PDT helpers.

Low-level call marshalling is done by `real32_call()` and, for 64-bit builds, `real64_call()`. They populate architecture-specific real-mode stack overlays before entering assembly helpers.

## Control Flow

Normal wrappers follow a common pattern: acquire `pdc_lock`, prepare an aligned physical-address argument or copy caller input into `pdc_result2`, call `mem_pdc_call()` or `real32_call()`, optionally widen returned words, copy results out to caller buffers, release the lock, and return the PDC status. Some functions intentionally preset result words before calls so unsupported firmware leaves deterministic output.

The firmware-width path starts narrow on 64-bit kernels, calls `PDC_MODEL_CAPABILITIES`, and clears `parisc_narrow_firmware` when the result reports wide firmware. All later `mem_pdc_call()` invocations route through the selected real-mode call.

`pdc_iodc_print()` is a special console path. It uses a locked static page-aligned buffer, translates the first newline it emits to CRLF, and calls the boot console IODC entry through `real32_call()` regardless of OS width. `pdc_iodc_getc()` similarly uses the keyboard IODC entry if present.

Reset and emergency paths deliberately diverge from the ordinary model. `pdc_emergency_unlock()` drops the lock during stack dumping if firmware access is needed. `pdc_soft_power_button_panic()` uses `spin_trylock_irqsave()` to avoid deadlock during panic notification.

## State And Persistence Behavior

Most state is transient and protected by `pdc_lock`, but the file can read and write persistent firmware-backed stable storage through the `pdc_stable_*` API and can alter power-button policy through `pdc_soft_power_button()`. `pdc_stable_initialize()` is destructive by design. `parisc_narrow_firmware` is boot-initialized and marked `__ro_after_init`, so width selection becomes a stable global after initialization.

## Dependencies And Integration Points

This file integrates with page-zero firmware fields (`PAGE0`), real-mode assembly call helpers, PA-RISC PDC/PAT headers, boot CPU data, platform inventory, interrupt routing, SCSI and network drivers, STI console code, power management, panic notifiers, and memory-error/PDT handling. Several symbols are exported for modules or drivers, including address validation, IODC reads, LAN station IDs, stable storage, TOD, and STI calls.

## Risks

The main correctness risk is misuse of the static result buffers outside `pdc_lock`; a new wrapper that copies results after unlocking can race. Narrow-firmware widening is another high-risk area because missed `convert_to_wide()` or `f_extend()` calls can truncate firmware addresses on 64-bit kernels. Several wrappers trust caller-provided counts and PDC-reported byte counts, so buffer sizing must match the firmware contract. Panic and HPMC contexts are sensitive to lock recursion. Real-mode call marshalling has fixed argument counts and depends on external assembly stack layout.

## Test Signals

Useful signals are successful boot on narrow and wide firmware machines, correct `setup_pdc()` detection, stable `/proc/cpuinfo` and model names, device discovery through PAT and SYSTEM_MAP, functioning early IODC console output/input, successful stable-storage read/write utilities, working TOD read/set, PCI interrupt routing table discovery, and absence of lockdep or panic-path deadlocks around PDC calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/firmware.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/ftrace.c -->
# sources/distributed-fs/ceph-client/arch/parisc/kernel/ftrace.c

## Purpose

`ftrace.c` implements PA-RISC function tracing support. It provides the runtime trampoline invoked from compiler-generated patchable call sites, dynamic ftrace patching, optional function-graph return hooking, and the kprobes-on-ftrace bridge.

## Important APIs, Types, And Functions

`ftrace_func` stores the active trace callback installed by `ftrace_update_ftrace_func()`. `ftrace_function_trampoline()` calls the current function tracer with `self_addr`, `parent`, `function_trace_op`, and ftrace register state.

When `CONFIG_FUNCTION_GRAPH_TRACER` is enabled, `ftrace_graph_enable` is a static key toggled by `ftrace_enable_ftrace_graph_caller()` and `ftrace_disable_ftrace_graph_caller()`. `prepare_ftrace_return()` replaces the saved return pointer with `parisc_return_to_handler` after `function_graph_enter()` accepts the edge.

Dynamic ftrace entry points include `ftrace_call_adjust()`, `ftrace_make_call()`, and `ftrace_make_nop()`. The make-call path builds PA-RISC instruction templates, checks that the patch region is still all NOPs using `copy_from_kernel_nofault()`, and patches text with `__patch_text_multiple()`. On 64-bit, it handles an unaligned callsite variant and dereferences function descriptors before embedding the target address.

With `CONFIG_KPROBES_ON_FTRACE`, `kprobe_ftrace_handler()` maps ftrace hits into kprobe pre/post handling, and `arch_prepare_kprobe_ftrace()` marks the optimized kprobe instruction slot as unused.

## Control Flow

At runtime a patched callsite branches into a trampoline sequence that reaches `ftrace_function_trampoline()`. The trampoline invokes the active ftrace callback first. If graph tracing is enabled, it locates the caller return pointer on the stack using the original stack pointer and `RP_OFFSET`; it only modifies the return slot if the saved value matches `parent`.

For dynamic enablement, ftrace computes the adjusted callsite address as the last instruction in the patchable function area. `ftrace_make_call()` chooses a 32-bit or 64-bit trampoline template, verifies the reserved instructions are NOPs, and writes the trampoline. `ftrace_make_nop()` restores the callsite and preceding reserved instructions to `INSN_NOP`.

The kprobe bridge prevents recursion with `ftrace_test_recursion_trylock()`, looks up a kprobe at `ip`, sets per-CPU current kprobe state, runs pre handlers, advances `iaoq`, optionally runs post handlers, and clears state before unlocking recursion.

## State And Persistence Behavior

State is runtime-only: patched kernel text, `ftrace_func`, the graph static key, and per-CPU kprobe state. No persistent storage is used. Text patches persist until ftrace or kprobe infrastructure reverses them.

## Dependencies And Integration Points

The file depends on the generic ftrace, function graph, kprobes, jump label, user nofault copy, PA-RISC assembly offsets, function descriptors, and text patching APIs. It integrates with compiler-generated patchable function entries and the architecture's return-pointer stack frame layout.

## Risks

Instruction template size and placement are critical; an incorrect `FTRACE_PATCHABLE_FUNCTION_SIZE`, unaligned 64-bit case, or wrong descriptor dereference can corrupt executable text. The return-hook sanity check prevents some stack corruption, but it depends on `org_sp_gr3` and `RP_OFFSET` matching entry assembly. Kprobe-on-ftrace must preserve `iaoq` ordering and avoid recursion leaks.

## Test Signals

Signals include enabling and disabling function tracing through tracefs, running function graph tracing, loading modules with ftrace callsites, verifying no `-EINVAL` from non-NOP patch regions, using kprobes optimized through ftrace, and checking that trace callbacks receive correct parent/self addresses on both 32-bit and 64-bit kernels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/ftrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/hardware.c -->
# sources/distributed-fs/ceph-client/arch/parisc/kernel/hardware.c

## Purpose

`hardware.c` is a boot-time PA-RISC hardware identification database. It maps firmware hardware IDs to human-readable device names and maps CPU hversion model bits to PA-RISC CPU type enums and ISA version strings.

## Important APIs, Types, And Functions

`hp_hardware_list[] __initdata` is a large table of `struct hp_hardware` entries. Each row keys on `hw_type`, `hversion`, `sversion`, and hardware revision to name processors, bus adapters, direct I/O devices, DMA devices, FIO devices, memory controllers, management controllers, and miscellaneous platform devices.

`hp_cpu_type_mask_list[] __initdata` maps masked hversion model values to `enum cpu_type`. `cpu_name_version[][]` maps each `enum cpu_type` to a CPU marketing name and architecture version string.

`parisc_hardware_description()` searches `hp_hardware_list` for an exact hardware ID match and returns a fallback generic name for unknown processors, some direct devices, and memory. `parisc_get_cpu_type()` interprets the `PDC_MODEL_INFO` hversion by shifting to model bits, applying mask rows in order, and panicking if no CPU type is known.

## Control Flow

Device registration code calls `parisc_hardware_description()` during boot after firmware inventory has produced `struct parisc_device_id` values. The function performs a linear scan until the `HPHW_FAULTY` sentinel. If no exact row matches, it switches on `hw_type` for generic fallbacks and otherwise reports `unknown device`.

CPU setup calls `parisc_get_cpu_type()` with the hversion returned by firmware. The function linearly scans mask rows and returns the first matching CPU type. The table order matters for overlapping masks, as seen in the dense PCX/PCXU/PCXW ranges.

## State And Persistence Behavior

The hardware and CPU mask tables are `__initdata`, so they are intended to be discarded after initialization. The exported `cpu_name_version` table remains available for later CPU reporting. There is no persistent state or runtime mutation.

## Dependencies And Integration Points

The file depends on `asm/hardware.h` for `struct hp_hardware`, `struct parisc_device_id`, hardware type constants, and `enum cpu_type`. It is used by PA-RISC bus/device registration and CPU initialization paths to turn firmware identifiers into operator-readable descriptions and CPU feature classes.

## Risks

The table is manually curated and exact-match driven. Missing rows cause generic names, while wrong rows can mislabel hardware and confuse driver diagnostics. The CPU mask table affects CPU feature selection; a bad mask or wrong row order can select the wrong architecture class or panic on valid machines. Because the main database is `__initdata`, no late code should retain pointers into returned table strings unless the string storage remains valid for the caller's lifetime.

## Test Signals

Useful signals are boot logs showing accurate model and device descriptions, correct `/proc/cpuinfo` CPU family/version output, successful boot across representative PA1.1 and PA2.0 systems, and no panic from `parisc_get_cpu_type()` on supported hversions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/hardware.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/head.S -->
# sources/distributed-fs/ceph-client/arch/parisc/kernel/head.S

## Purpose

`head.S` is the PA-RISC kernel entry path. It handles the transition from firmware/loader state into the virtual-memory kernel, builds initial mappings, validates CPU capabilities, configures PDC and interrupt vectors, and provides the SMP slave entry path.

## Important APIs, Types, And Labels

`boot_args` stores four 32-bit bootloader arguments. `parisc_kernel_start` is the primary entry point. `common_stext` contains setup shared by the monarch CPU and SMP slave CPUs. `aligned_rfi` performs the final return-from-interruption transition into virtual mode. `smp_slave_stext` is the firmware rendezvous entry for secondary CPUs. `stext_pdc_ret`, `stext_pdc_btlb_ret`, and `smp_callin_rtn` are local return labels for firmware calls and failure traps.

The code imports `init_task`, `init_stack`, `fault_vector_20`, `fault_vector_11`, `start_parisc`, `smp_callin`, and `smp_init_current_idle_task`. It writes page-zero rendezvous fields such as `MEM_RENDEZ` and uses page table symbols including `swapper_pg_dir`, `pmd0`, `pg0`, and `_end`.

## Control Flow

Entry clears kernel space registers, zeros BSS, saves boot arguments, and on PA2.0-configured kernels verifies that the CPU supports the required wide control-register behavior. If the CPU check fails, it prints an IODC panic message and loops.

The boot CPU initializes early page tables covering the initial kernel physical range, sets kernel and user root pointers, initializes `cr30` with `init_task`, sets the physical stack, and on 64-bit function-tracing builds initializes the `_mcount` function descriptor GP field. SMP builds install `smp_slave_stext` in page-zero rendezvous fields; non-SMP clears them.

`common_stext` optionally switches to wide mode, calls PDC to set default wide PSW on 64-bit, clears block TLBs on 32-bit PA1.1, clears user space registers and protection registers, loads the global pointer, selects the correct fault vector, installs the IVA in `cr14`, prepares the IIA queues and IPSW, converts the stack to virtual, and executes `rfi` into `start_parisc` or `smp_callin`.

`smp_slave_stext` initializes secondary CPU space registers, enables wide mode early on 64-bit, installs the idle task and stack provided by the monarch, points at `swapper_pg_dir`, loads `smp_callin`, and branches through `common_stext`.

## State And Persistence Behavior

The file initializes persistent machine-wide boot state: zeroed BSS, saved `boot_args`, early page tables, root pointers, IVA, page-zero SMP rendezvous addresses, task pointer in `cr30`, and initial PSW defaults. It does not use filesystem persistence.

## Dependencies And Integration Points

It is tightly coupled to linker symbols, assembly offsets, PDC page-zero layout, PSW/control-register definitions, fault-vector assembly, SMP CPU bring-up, and the C entry points `start_parisc()` and `smp_callin()`.

## Risks

Ordering is critical. Installing IVA too early can break HPMC behavior, switching to virtual addresses before page tables are valid can trap, and incorrect stack or `cr30` setup breaks exception handling. 64-bit wide-mode setup depends on firmware quirks such as the PCX-W2 bug workaround. SMP rendezvous uses physical addresses and assumes the slave entry is below 4 GB in the stored high word case.

## Test Signals

Signals include reaching `start_parisc()` on boot, correct saved boot arguments, successful PA1.1 and PA2.0 fault vector installation, secondary CPU bring-up through `smp_callin`, no early RFI traps, and successful boot with `CONFIG_64BIT`, `CONFIG_SMP`, `CONFIG_HOTPLUG_CPU`, and `CONFIG_FUNCTION_TRACER` combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/head.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/hpmc.S -->
# sources/distributed-fs/ceph-client/arch/parisc/kernel/hpmc.S

## Purpose

`hpmc.S` implements the PA-RISC High Priority Machine Check handler. It tries to collect firmware PIM data, reset I/O, reinitialize enough console IODC state, and return into the normal trap-save path with an HPMC code so C code can dump registers and memory.

## Important APIs, Types, And Labels

The file allocates `hpmc_iodc_buf`, `hpmc_raddr`, and exported `hpmc_pim_data`. `os_hpmc` is the handler entry point. Labels `os_hpmc_1` through `os_hpmc_6` sequence PDC calls and failure reset handling.

It imports `toc_stack` as the emergency stack and `intr_save` as the normal low-level trap-save path. It uses PDC constants for `PDC_PIM`, `PDC_IO`, `PDC_IODC`, IODC `ENTRY_INIT_MOD_DEV`, and `PDC_BROADCAST_RESET`.

## Control Flow

On entry, `os_hpmc` saves the PDCE_PROC address from `arg0`, invalidates the handler checksum by incrementing a word under IVA to prevent nested HPMCs, switches to the TOC stack, and uses `rfi` to turn on the Q bit and turn off the M bit as required by many PDC calls.

The handler calls `PDC_PIM_HPMC` to copy HPMC PIM data into `hpmc_pim_data`, then calls `PDC_IO` to reset I/O. It loads console IODC into `hpmc_iodc_buf` with `PDC_IODC_READ`, calls the IODC init entry for the boot console using page-zero HPA/SPA/path fields, restores kernel page table root pointers, clears space registers, converts the stack to virtual, clears Q, sets trap code 1, and branches to `intr_save`.

If a required PDC or IODC step fails, the handler calls `PDC_BROADCAST_RESET`; if that returns, it writes a reset command to the broadcast I/O address and loops.

## State And Persistence Behavior

The handler writes the global PIM buffer and modifies low-level processor state: PSW bits, root pointers, space registers, stack pointer, and trap code. It deliberately invalidates the HPMC checksum to avoid reentry. No filesystem persistence is involved.

## Dependencies And Integration Points

It depends on firmware PDCE_PROC entry semantics, page-zero console fields, the TOC stack, `swapper_pg_dir`, and the trap entry code in `intr_save`. The C trap handler later consumes the saved state and `hpmc_pim_data`.

## Risks

The handler runs when hardware or firmware state may already be compromised. It has no normal C stack, uses physical addresses for early operations, and cannot rely on most kernel services. Multiprocessor synchronization is explicitly marked as missing. Failure in PDC_PIM or console IODC paths falls back to reset, so changes must preserve minimalism and firmware calling conventions.

## Test Signals

Signals are difficult to automate. Useful evidence includes successful HPMC injection or emulator-assisted machine-check tests that reach the C trap dump, valid PIM data in `hpmc_pim_data`, console output after HPMC, and reset fallback when forced PDC/IODC failures occur.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/hpmc.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/inventory.c -->
# sources/distributed-fs/ceph-client/arch/parisc/kernel/inventory.c

## Purpose

`inventory.c` discovers PA-RISC firmware type, physical memory ranges, and platform devices. It supports three inventory families: PAT, SYSTEM_MAP, and older Snake/PDC_MEM_MAP machines.

## Important APIs, Types, And Functions

Global firmware classification is stored in `pdc_type __ro_after_init`. PAT systems also fill `parisc_cell_num`, `parisc_cell_loc`, and `parisc_pat_pdc_cap`.

`setup_pdc()` probes firmware type. It tries `pdc_system_map_find_mods()`, then 64-bit PAT `pdc_pat_cell_get_number()`, then legacy bus-ID matching through `pdc_model_info()`. Unsupported types panic.

Memory setup helpers include `set_pmem_entry()`, `pagezero_memconfig()`, 64-bit `pat_memconfig()`, and `sprockets_memconfig()`. Device inventory helpers include `pat_query_module()`, `pat_inventory()`, `legacy_create_device()`, `snake_inventory()`, `add_system_map_addresses()`, and `system_map_inventory()`.

Public init entry points are `do_memory_inventory()` and `do_device_inventory()`.

## Control Flow

`setup_pdc()` determines which later paths run. `do_memory_inventory()` switches on `pdc_type`: PAT uses PAT address maps, SYSTEM_MAP uses the newer PDC memory table with page-zero fallback, and Snake uses page-zero memory. It validates that at least one range exists and that the first starts at PFN 0, otherwise it warns and falls back to page zero.

`do_device_inventory()` initializes the PA-RISC bus and switches on `pdc_type`. PAT inventory loops over cell modules and calls `pat_query_module()` until firmware stops returning modules. SYSTEM_MAP inventory scans module indices up to 255, allocates and registers `parisc_device` objects, then appends additional addresses when reported. Snake inventory synthesizes module paths over legacy module/function ranges and uses `PDC_MEM_MAP_HPA`.

For QEMU with firmware config sysfs enabled, the device inventory reads a SeaBIOS-provided base from `PAGE0->pad0` and registers a `fw_cfg` platform device if present.

## State And Persistence Behavior

The file populates global memory range tables (`pmem_ranges`, `npmem_ranges`), registers `parisc_device` objects, initializes the PA bus, and sets TLB serialization policy on some 64-bit SMP machines. These are boot-time state changes that persist for the running kernel.

## Dependencies And Integration Points

It depends heavily on PDC wrappers from `firmware.c`, PAT definitions, memory zone globals, PA device allocation and registration, central bus walking, platform devices, QEMU `fw_cfg`, and TLB flush policy.

## Risks

Firmware return data is diverse and hardware-specific. Range alignment errors intentionally panic in `set_pmem_entry()`. PAT address-map filtering can exclude memory if usage/type checks are wrong. SYSTEM_MAP scanning has fixed bounds and ignores nonterminal transient errors. Legacy Snake probing can register incomplete device sets if module path assumptions change. Device registration must handle allocation failures without leaking partially initialized firmware objects.

## Test Signals

Signals include boot logs showing correct PDC type, nonzero and correctly bounded memory ranges, expected devices in "Found devices" output, QEMU `fw_cfg` platform-device registration when available, no fallback warnings on known-good firmware, and correct behavior across PAT, SYSTEM_MAP, and legacy Snake machines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/inventory.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/irq.c -->
# sources/distributed-fs/ceph-client/arch/parisc/kernel/irq.c

## Purpose

`irq.c` implements PA-RISC external interrupt masking, CPU IRQ chips, transaction interrupt allocation, `/proc/interrupts` formatting, optional IRQ stacks, stack-overflow checks, and the main CPU interrupt dispatch routine.

## Important APIs, Types, And Functions

`cpu_eiem` is the global external interrupt enable mask, and per-CPU `local_ack_eiem` suppresses an interrupt while it is acknowledged and in service. `EIEM_MASK()` converts a virtual IRQ number to the big-endian EIEM bit.

The `cpu_interrupt_type` irq chip provides `cpu_mask_irq()`, `cpu_unmask_irq()`, `cpu_ack_irq()`, and `cpu_eoi_irq()`. SMP affinity validation is handled by `cpu_check_affinity()`.

Transaction helpers include `cpu_claim_irq()`, `txn_claim_irq()`, `txn_alloc_irq()`, `txn_affinity_addr()`, `txn_alloc_addr()`, and `txn_alloc_data()`. They map Linux virtual IRQs to processor transaction addresses and EIRR data bits for I/O devices.

`show_interrupts()` and `arch_show_interrupts()` format normal and architecture-specific interrupt/trap counters. `do_cpu_irq_mask()` is called from entry assembly to dispatch external interrupts. `init_IRQ()` initializes the CPU IRQ range and enables timer/IPI masks.

With `CONFIG_IRQSTACKS`, `union irq_stack_union`, `execute_on_irq_stack()`, and `do_softirq_own_stack()` provide separate IRQ/softirq stacks.

## Control Flow

Masking clears a bit in `cpu_eiem`; unmasking sets it and sends NOP IPIs so other CPUs refresh EIEM. Ack clears the bit from the local per-CPU ack mask, writes the effective EIEM, and clears the pending EIRR bit through control register 23. EOI restores the local mask bit and re-enables the effective EIEM.

`do_cpu_irq_mask()` saves current irq regs, disables local IRQs, enters RCU irq context, reads pending EIRR masked by both global and local masks, converts the highest pending bit to a virtual IRQ, filters spurious IRQs, optionally redirects per-CPU SMP interrupts to their affine CPU, checks stack usage, and calls `generic_handle_irq()` either directly or on the IRQ stack. Before return it restores EIEM when no interrupt was handled or after masked-out paths.

`init_IRQ()` clears all pending external interrupts, claims CPU IRQs, installs timer and optional IPI handlers, initializes `cpu_eiem`, and writes EIEM.

## State And Persistence Behavior

Runtime state includes the global EIEM mask, per-CPU ack masks, per-CPU interrupt statistics, IRQ stack locks and usage counters, the `sysctl_panic_on_stackoverflow` knob, and IRQ descriptor chip/handler assignments. No persistent storage is used.

## Dependencies And Integration Points

The file integrates with generic IRQ descriptors, timer and IPI handlers, SMP CPU data transaction addresses, GSC I/O writes for interrupt redirection, PA-RISC control registers, entry assembly, RCU irq accounting, and stack debugging.

## Risks

EIEM/EIRR bit numbering is big-endian and easy to get wrong. `cpu_eiem` is a volatile global manipulated without an explicit spinlock in some paths, relying on interrupt context and architecture expectations. Affinity redirection must avoid losing per-CPU interrupts. IRQ stack locking uses low-level ldcw semantics; mistakes can recurse or corrupt stacks. Stack-overflow panic logic mutates a sysctl flag to prevent repeated panics.

## Test Signals

Signals include timer ticks, IPI delivery, working device interrupts, sane `/proc/interrupts` output, IRQ affinity changes, transaction IRQ allocation for GSC/PCI/MSI users, stack usage counters under debug configs, and no lost interrupts during mask/unmask storms on SMP.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/jump_label.c -->
# sources/distributed-fs/ceph-client/arch/parisc/kernel/jump_label.c

## Purpose

`jump_label.c` implements PA-RISC static-key patching. It transforms reserved NOP sites into PA1.1 `b,n` branches to static-key targets, or back into NOPs.

## Important APIs, Types, And Functions

`reassemble_17()` encodes a signed 17-bit branch displacement into PA-RISC instruction bit layout. `arch_jump_label_transform()` is the architecture hook called by generic jump-label code with a `struct jump_entry` and `enum jump_label_type`.

## Control Flow

The transform obtains the patch address from `jump_entry_code()`. For `JUMP_LABEL_JMP`, it computes `target - addr - 8`, verifies the signed 17-bit branch range, encodes a `b,n` instruction (`0xe8000002` plus the reassembled displacement), and calls `patch_text()`. For the non-jump state it patches `INSN_NOP`.

## State And Persistence Behavior

The only state mutation is kernel text patching at static-key sites. Patches persist until the static key toggles again. There is no separate data persistence.

## Dependencies And Integration Points

The file depends on generic jump labels, PA-RISC alternative/text patching, instruction constants, and the assumption that static-key branch targets are within the 17-bit displacement range.

## Risks

The range check is fatal through `BUG_ON()`. Code layout changes that put jump-label targets outside range will crash when transforming. The displacement subtracts 8 for PA-RISC branch semantics, so off-by-one-instruction errors would redirect control flow.

## Test Signals

Signals include toggling static keys under tracing or branch-heavy kernel features, verifying patched instruction bytes with ftrace/jump-label debug tooling, and booting kernels where jump-label sites are spread across sections without range failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/jump_label.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/kexec.c -->
# sources/distributed-fs/ceph-client/arch/parisc/kernel/kexec.c

## Purpose

`kexec.c` implements the PA-RISC machine-dependent kexec handoff. It stops secondary CPUs, maps the relocation code, copies the relocation stub, passes architecture-specific boot parameters, flushes caches/TLBs, disables interrupts, and jumps to the new kernel.

## Important APIs, Types, And Functions

External relocation symbols are `relocate_new_kernel()`, `relocate_new_kernel_size`, and offsets for initrd, cmdline, and free-memory fields. `machine_shutdown()` stops SMP CPUs. `machine_kexec()` performs the final handoff. `machine_kexec_prepare()` logs image metadata through `kexec_image_info()`. Cleanup and crash-shutdown hooks are present but empty.

## Control Flow

`machine_shutdown()` sends stop requests to secondary CPUs and waits until only one CPU remains online. `machine_kexec()` maps the image control code page at `FIX_TEXT_KEXEC`, flushes caches, prepares either a direct function pointer or a 64-bit function descriptor pointing at the fixed mapping, copies the relocation code into that mapping, writes command line, initrd, and free-memory values into relocation-code data slots, flushes caches and TLBs again, disables local IRQs, and calls the relocation stub with the page-masked image head, image start, and physical control page.

`machine_kexec_prepare()` currently only emits debug information for the image and segments.

## State And Persistence Behavior

The file mutates fixmap state, writes into the control code page, stops CPUs, flushes caches and TLBs, disables local interrupts, and transfers execution. It does not persist state across the new kernel except through the relocation stub arguments and patched relocation-code data slots.

## Dependencies And Integration Points

It depends on generic kexec `struct kimage`, PA-RISC fixmap definitions, cache/TLB flushing, function descriptor semantics, `PAGE0->mem_free`, SMP stop handling, and the assembly relocation routine.

## Risks

The relocation code must fit and be executable at `FIX_TEXT_KEXEC`. Offsets into the relocation code must match the assembly layout exactly. Secondary CPUs must be stopped before the handoff to avoid memory corruption. Incorrect function descriptor setup on 64-bit will branch to the wrong address. Cache/TLB flush ordering is critical before executing freshly copied code.

## Test Signals

Signals include successful `kexec -l` and `kexec -e`, correct cmdline/initrd visibility in the second kernel, no secondary CPU activity during handoff, debug segment logs when enabled, and successful operation on 32-bit and 64-bit builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/kexec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/kexec_file.c -->
# sources/distributed-fs/ceph-client/arch/parisc/kernel/kexec_file.c

## Purpose

`kexec_file.c` provides `kexec_file_load` support for PA-RISC ELF kernels. It loads an ELF vmlinux image, converts segment addresses to physical addresses, adds optional initrd and command-line buffers, and registers the loader in the architecture loader list.

## Important APIs, Types, And Functions

`elf_load()` is the loader implementation used by `kexec_elf_ops`. It uses generic helpers `kexec_build_elf_info()`, `kexec_elf_load()`, and `kexec_add_buffer()`. `kexec_file_loaders[]` advertises `kexec_elf_ops` as the supported file loader.

## Control Flow

`elf_load()` builds ELF metadata from the kernel buffer, asks the generic ELF loader to place loadable segments, sets `image->start` to the physical entry address, and converts each segment `mem` value with `__pa()`. If an initrd is supplied, it appends it as a page-aligned buffer and records `image->arch.initrd_start` and `image->arch.initrd_end`. If a command line is supplied, it adds an aligned buffer below the kernel load address but above `PAGE0->mem_free + PAGE_SIZE`, then records `image->arch.cmdline`.

The function returns `NULL` regardless of success or failure; the generic kexec file loader tracks errors through the `ret` path before `out`.

## State And Persistence Behavior

The file mutates `struct kimage`: `start`, segment physical addresses, and PA-RISC arch fields for initrd and command line. No persistent storage is used.

## Dependencies And Integration Points

It depends on generic ELF kexec support, libfdt/of headers included for common kexec-file infrastructure, page alignment, physical-address conversion, and page-zero free-memory boundaries. The values it fills are consumed later by `machine_kexec()`.

## Risks

Address conversion must match what `machine_kexec()` and the relocation stub expect. The command-line placement constraints assume `PAGE0->mem_free` is a safe lower bound and `kernel_load_addr` is a safe upper bound. Returning `NULL` means reviewers must inspect generic API expectations carefully when changing error handling.

## Test Signals

Signals include `kexec_file_load` accepting valid PA-RISC ELF kernels, rejecting malformed ELFs through generic helpers, preserving initrd and command-line addresses into the second kernel, and no segment-address mismatch in `machine_kexec()` debug output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/kexec_file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/kgdb.c -->
# sources/distributed-fs/ceph-client/arch/parisc/kernel/kgdb.c

## Purpose

`kgdb.c` implements PA-RISC architecture support for KGDB. It registers a die notifier, converts register state to and from GDB layout, patches breakpoints, adjusts the PA-RISC instruction address queues, and handles continue/single-step commands.

## Important APIs, Types, And Functions

`arch_kgdb_ops` defines the PA-RISC breakpoint instruction bytes. `kgdb_arch_init()` and `kgdb_arch_exit()` register and unregister `kgdb_notifier`. `pt_regs_to_gdb_regs()`, `gdb_regs_to_pt_regs()`, and `sleeping_thread_to_gdb_regs()` translate between `struct pt_regs` and `struct parisc_gdb_regs`.

Breakpoint APIs are `kgdb_arch_set_breakpoint()` and `kgdb_arch_remove_breakpoint()`, using `copy_from_kernel_nofault()` and `__patch_text()`. `kgdb_arch_set_pc()` and `step_instruction_queue()` update `iaoq[0]` and `iaoq[1]`. `kgdb_arch_handle_exception()` handles GDB remote commands.

## Control Flow

The die notifier disables local IRQs around `kgdb_handle_exception()`. Register export zeros the GDB register buffer, copies GPRs/FPRs, segment registers, SAR/IIR/ISR/IOR/IPSW/CR27, and front/back instruction queues. Import writes the same fields back.

For sleeping threads, the code temporarily substitutes `ksp` and `kpc` into `gr[30]` and `iaoq[0]`, exports registers, then restores the original values.

On continue, detach, or kill commands, the handler clears KGDB current thread/single-step state, optionally sets PC from an address, and steps past compiled break instructions. On single-step, it sets `kgdb_single_step`, optionally sets PC, manipulates control register 0 for break-step behavior, sets `PSW_R`, and returns handled.

## State And Persistence Behavior

State is runtime debug state: notifier registration, patched breakpoint instructions, KGDB global current-thread/single-step flags, and modified `pt_regs`. No persistent storage is used.

## Dependencies And Integration Points

The file depends on generic KGDB, die notifiers, PA-RISC trap constants, text patching, cache flushing, and the architecture's dual instruction queue model. It integrates with compiled breakpoints and GDB remote protocol command parsing.

## Risks

Incorrect register mapping can make remote debugging misleading or destructive. PA-RISC uses front/back instruction queues, so setting only one PC word would be wrong. Breakpoint patching must preserve original instructions exactly and must be safe under nofault reads. Single-step depends on PSW and control-register behavior that is architecture-specific.

## Test Signals

Signals include connecting KGDB, reading and writing registers, setting and removing breakpoints, continuing past compiled break instructions, single-stepping over normal and breakpoint traps, and inspecting sleeping tasks with correct stack and PC values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/kgdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/kprobes.c -->
# sources/distributed-fs/ceph-client/arch/parisc/kernel/kprobes.c

## Purpose

`kprobes.c` implements PA-RISC kprobes and kretprobes. It patches probe sites with break instructions, executes copied instructions from slots, handles single-step completion, manages reentrant probes, and installs a kretprobe trampoline.

## Important APIs, Types, And Functions

Per-CPU state is `current_kprobe` and `kprobe_ctlblk`. Probe lifecycle hooks are `arch_prepare_kprobe()`, `arch_remove_kprobe()`, `arch_arm_kprobe()`, and `arch_disarm_kprobe()`. Runtime handlers are `parisc_kprobe_break_handler()` and `parisc_kprobe_ss_handler()`.

Reentry helpers include `save_previous_kprobe()`, `restore_previous_kprobe()`, `set_current_kprobe()`, and `setup_singlestep()`. Kretprobe support is provided by `__kretprobe_trampoline()`, `trampoline_probe_handler()`, `arch_kretprobe_fixup_return()`, `arch_prepare_kretprobe()`, `arch_trampoline_kprobe()`, and `arch_init_kprobes()`.

## Control Flow

Preparing a kprobe rejects unaligned addresses, allocates an instruction slot, saves the original opcode, copies it into slot word 0, places `PARISC_KPROBES_BREAK_INSN2` in slot word 1, and flushes the slot. Arming patches the original address with `PARISC_KPROBES_BREAK_INSN`; disarming restores the original opcode.

On the first break, `parisc_kprobe_break_handler()` disables preemption, looks up a kprobe at `iaoq[0]`, handles reentry by saving prior state and single-stepping without user handlers, or sets the current probe and runs the pre-handler. If the pre-handler returns zero or is absent, it redirects execution to the copied instruction slot and marks single-step status; otherwise it clears state and re-enables preemption.

On the second break from the instruction slot, `parisc_kprobe_ss_handler()` verifies the PC is the slot's second instruction, restores previous state for reentry, runs post-handler if present, then reconstructs `iaoq` for branch or non-branch instructions before clearing current kprobe.

For return probes, `arch_prepare_kretprobe()` saves the original return address from `gr[2]` and replaces it with the trampoline address. The trampoline kprobe handler calls the generic kretprobe trampoline handler and consumes the probe.

## State And Persistence Behavior

Runtime state includes patched text, allocated instruction slots, per-CPU kprobe control blocks, saved `iaoq` values, missed-count increments, and modified return addresses for kretprobes. No persistent storage is used.

## Dependencies And Integration Points

The file depends on generic kprobes, text patching, instruction-slot allocation, cache flushing, PA-RISC break instruction constants, function descriptor dereferencing for the trampoline, and `pt_regs` instruction queues.

## Risks

Branch queue reconstruction is subtle; absolute branch instructions use the already computed back queue, while other instructions need sequential queue restoration. Preemption must remain disabled across active probe handling. Reentrant probes intentionally skip user handlers and increment missed counts. Incorrect trampoline descriptor handling would break kretprobes on 64-bit.

## Test Signals

Signals include installing/removing kprobes on aligned function instructions, rejecting unaligned addresses, pre/post handlers receiving correct regs, kretprobes reporting returns, nested probe missed counts increasing, and successful probes on branch and non-branch instructions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/kprobes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/module.c -->
# sources/distributed-fs/ceph-client/arch/parisc/kernel/module.c

## Purpose

`module.c` implements PA-RISC ELF module relocation, per-section PLT stub reservation, GOT and function-descriptor allocation, module unwind registration, alternative patching, ftrace callsite relocation, and function-descriptor dereferencing for loaded modules.

## Important APIs, Types, And Functions

Instruction encoding helpers include `reassemble_14()`, `reassemble_16a()`, `reassemble_17()`, `reassemble_21()`, and `reassemble_22()`. Relocation safety uses `RELOC_REACHABLE()` and `CHECK_RELOC()`.

`struct got_entry` and `struct stub_entry` vary by 32-bit versus 64-bit builds. Section-level metadata is allocated in `module_frob_arch_sections()` and freed in `module_arch_freeing_init()` or `module_finalize()`. `arch_mod_section_prepend()` tells the module loader how many bytes of stubs to reserve before each code section.

64-bit helpers include `get_got()`, `get_fdesc()`, and `dereference_module_function_descriptor()`. `get_stub()` creates 32-bit direct stubs or 64-bit GOT, millicode, and direct branch stubs.

Relocation is performed by the 32-bit or 64-bit implementation of `apply_relocate_add()`. Finalization uses `register_unwind_table()`, `deregister_unwind_table()`, `module_finalize()`, and `module_arch_cleanup()`.

## Control Flow

Before layout, `module_frob_arch_sections()` scans relocation sections, counts GOT entries, function descriptors, and branch stubs, records `.PARISC.unwind`, reserves stubs for target sections, and appends GOT and fdesc storage to `MOD_TEXT`.

During relocation, the code walks each `Elf_Rela`, finds the target location and symbol, computes `dot`, symbol value, and addend, and switches on relocation type. 32-bit relocations handle direct 32-bit values, DIR21L/DIR14R, DP-relative values, PCREL17F/22F with out-of-range stubs, PCREL32, SEGREL32, and SECREL32. 64-bit relocations handle LTOFF GOT offsets, PCREL22F with local direct reach checks or external stubs, PCREL32/64, DIR64, SEGREL32/SECREL32, and FPTR64 function descriptors.

`get_stub()` lazily initializes each section's stub area immediately before the section, aligns it, consumes one reserved entry, writes instruction sequences, and returns the stub address. `get_got()` and `get_fdesc()` deduplicate entries and enforce maximum counts.

`module_finalize()` registers unwind data, compacts allocated symbol tables by removing `.L` local labels, checks GOT overflow, applies alternatives, and relocates ftrace callsite sections when dynamic ftrace is enabled. Cleanup deregisters unwind data.

## State And Persistence Behavior

The file mutates loaded module memory: code/data relocation targets, per-section prepended stub areas, GOT entries, function descriptors, unwind registration, symbol table contents, and alternative/ftrace patch sites. State persists for the lifetime of the loaded module and is cleaned during module unload.

## Dependencies And Integration Points

It depends on generic module loader layout callbacks, ELF relocation definitions for PA-RISC, unwind tables, alternatives, dynamic ftrace, function descriptor semantics, module memory classes, and architecture section metadata stored in `mod->arch`.

## Risks

Relocation encoding is high risk because PA-RISC immediate fields are non-contiguous and branch offsets are PC-relative with instruction-queue semantics. Stub count estimation must match actual stub consumption or `BUG_ON()` fires. GOT has a hard `MAX_GOTS` limit. The SEGREL32 behavior is intentionally ABI-nonstandard for unwind entries, so changing it can break unwinding. Symbol-table compaction mutates loaded metadata and must preserve references expected by generic module code.

## Test Signals

Signals include loading modules with large text sections and far calls, XFS/IPV6-style modules that require per-section stubs, 64-bit modules with external function descriptors, unwind backtraces through module code, alternatives applying inside modules, dynamic ftrace over module callsites, and clean unload without stale unwind registrations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/module.c -->
