# Research: subset-b-000779

Grouped research for PowerPC RTAS firmware entry, RTAS flash/event/PPCI helpers, secure boot/secvar sysfs, architecture setup, and 32-bit signal handling. Each section is keyed by the exact source path for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/rtas.c -->

# sources/distributed-fs/ceph-client/arch/powerpc/kernel/rtas.c

Purpose: central PowerPC RTAS firmware interface for CHRP/pSeries style machines. It discovers RTAS device-tree properties, builds a known-function token table, serializes calls into firmware, exposes the privileged `rtas` syscall with policy filtering, handles firmware busy/error conventions, provides exported sensor/power/indicator helpers, logs RTAS last-error records, and supplies restart/poweroff/halt/timebase operations.

Important APIs/types/functions: `struct rtas_filter`, `struct rtas_function`, global `struct rtas_t rtas`, `rtas_function_token()`, `rtas_token()`, `rtas_call()`, `rtas_call_unlocked()`, `rtas_busy_delay_time()`, `rtas_busy_delay()`, `rtas_error_rc()`, `rtas_get_power_level()`, `rtas_set_power_level()`, `rtas_get_sensor()`, `rtas_set_indicator()`, `rtas_ibm_suspend_me()`, `rtas_restart()`, `rtas_power_off()`, `rtas_halt()`, `rtas_os_term()`, `rtas_activate_firmware()`, `get_pseries_errorlog()`, `SYSCALL_DEFINE1(rtas)`, `rtas_initialize()`, `early_init_dt_scan_rtas()`, `rtas_give_timebase()`, and `rtas_take_timebase()`. Global synchronization is centered on `rtas_lock` and the shared `rtas_args`; sequence-sensitive firmware calls additionally use dedicated mutexes such as `rtas_ibm_get_vpd_lock`, `rtas_ibm_get_indices_lock`, and `rtas_ibm_activate_firmware_lock`.

Control flow: early boot scans `/rtas`, records `linux,rtas-base`, `linux,rtas-entry`, `rtas-size`, detects LPAR hints, and later `rtas_initialize()` resolves function tokens from single-u32 properties. The static function table must remain name-sorted for binary search and is reverse-indexed by token through an xarray for user-supplied syscall tokens. Normal kernel callers use `rtas_function_token()` then `rtas_call()`: it verifies translation is on, checks lockdown for error injection, takes `rtas_lock`, fills the big-endian argument block, calls the assembly `enter_rtas()` trampoline, decodes return words, and logs a fetched last-error buffer when status is `-1`. `rtas_busy_delay()` implements the firmware retry protocol, using early boot polling before scheduler time and `fsleep()`/`cond_resched()` later.

State and persistence: persistent state includes the RTAS base/entry/size, function-token table, xarray reverse map, allocated user RMO buffer (`rtas_rmo_buf`), shared `rtas_data_buf`, and boot-time error-log maximum. Firmware calls can alter platform state: power levels, indicators, timebase freeze/thaw, partition suspend, firmware activation, reboot/poweroff, and RTAS OS termination. The `rtas_flash_term_hook` pointer lets the firmware flash module inject reboot-time behavior without permanently linking it into this core file.

Dependencies and integration points: integrates with Open Firmware device tree, memblock RMO allocation, tracepoints (`trace_rtas_*`), pSeries/powernv platform code, panic/reboot paths, `security_locked_down()`, RTAS error logging, `rtasd`, `rtas_flash`, PCI/EEH/hotplug/RAS helpers, and the assembly trampoline in `rtas_entry.S`. The syscall ABI expects big-endian RTAS argument words and CAP_SYS_ADMIN.

Risks: the syscall is inherently dangerous because original RTAS allowed arbitrary physical addresses; safety depends on the whitelist table, buffer-index filters, RMO bounds checks, endian-specific bans, and token reverse lookup staying correct. Integer overflow in buffer end calculations, an incorrect fixed-size assumption, or a newly added firmware function without the right lock/filter can become a memory-corruption or firmware-abuse path. RTAS calls require tight interrupt/MSR constraints; misuse in NMI/real mode or without dedicated argument storage can deadlock or corrupt shared call state. Busy-loop callers must honor retry semantics to avoid live locks or firmware deadline failures.

Test signals: build ppc64 pSeries/CHRP configs with RTAS enabled; boot under QEMU/PowerVM and confirm `/rtas` token discovery, no function-table sort warnings, and `rtas-event-scan` behavior. Exercise exported power/sensor/indicator helpers on supported firmware, `sys_rtas` allowed and blocked calls, lockdown rejection of error injection, last-error logging, reboot/poweroff hooks, suspend/migration firmware activation, and timebase handoff on SMP-capable systems.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/rtas.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/rtas_entry.S -->

# sources/distributed-fs/ceph-client/arch/powerpc/kernel/rtas_entry.S

Purpose: low-level assembly trampoline that enters RTAS firmware with MMU translation and external interrupts disabled, then restores kernel execution state after firmware returns.

Important APIs/types/functions: exported assembly symbols `enter_rtas`, 64-bit helper labels `__enter_rtas`, `rtas_return_loc`, and `rtas_restore_regs`; 32-bit path saves LR/MSR/stack state in the thread `RTAS_SP`; 64-bit path saves TOC, nonvolatile GPRs, CR/CTR/XER/DAR/DSISR, stack pointer, and MSR in PACA fields.

Control flow: on PPC32 the routine creates an interrupt frame, loads RTAS entry/base from the global `rtas` struct, builds a physical return address, writes SRR0/SRR1 with the firmware entry and real-mode MSR, and uses `rfi` to enter firmware. On return it briefly re-enters translated kernel mode with a second `rfi`, restores LR/MSR/stack, clears the per-thread RTAS stack marker, and returns to C. On PPC64 the routine saves full kernel state because 32-bit RTAS may clobber upper register halves, clears CR as a firmware workaround, stores original stack/MSR in the PACA, computes real-mode return code, enters RTAS through `RFI_TO_KERNEL`, fixes endian on return, restores SF/translation through another RFI, then reloads saved registers and returns.

State and persistence: this file does not persist application data, but it temporarily mutates PACA save slots, SRR registers, LR, MSR, CR, and stack frames. It depends on the C-side caller holding the correct RTAS serialization and passing a physical RTAS argument block in `r3`.

Dependencies and integration points: called only through `rtas.c` (`do_enter_rtas()`), and relies on offsets from `asm-offsets.h`, PACA layout, RTAS base/entry fields, exception/real-mode macros, and endian-fixup support. The C caller invalidates SRR tracking after return because firmware uses SRRs.

Risks: any offset drift, wrong MSR bit composition, missing register save, or endian mismatch can crash the kernel or return with corrupted state. RTAS may be entered during machine-check paths on pSeries, so the real-mode and RI/HV handling must remain precise. The assembly must remain nokprobe-safe and non-instrumented.

Test signals: ppc32 and ppc64 boot tests on RTAS firmware, kernel selftests or smoke paths that perform RTAS calls, suspend/reboot/poweroff exercising return paths, and stress tracing plus machine-check/stop-self scenarios to catch missing state restoration.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/rtas_entry.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/rtas_flash.c -->

# sources/distributed-fs/ceph-client/arch/powerpc/kernel/rtas_flash.c

Purpose: module implementing `/proc/powerpc/rtas/{firmware_flash,firmware_update,validate_flash,manage_flash}` for RTAS firmware image staging, validation, temporary-image management, and reboot-time flashing.

Important APIs/types/functions: `struct flash_block`, `struct flash_block_list`, `struct rtas_update_flash_t`, `struct rtas_manage_flash_t`, `struct rtas_validate_flash_t`, `flash_list_valid()`, `free_flash_list()`, `rtas_flash_write()`, `rtas_flash_release()`, `manage_flash()`, `manage_flash_write()`, `validate_flash()`, `validate_flash_write()`, `validate_flash_release()`, `rtas_flash_firmware()`, `rtas_flash_files[]`, `rtas_flash_init()`, and `rtas_flash_cleanup()`.

Control flow: writes to `firmware_flash` or `firmware_update` allocate 4 KiB-aligned blocks from `flash_block_cache`, append them to an in-memory block-list chain, and cap each write chunk to `RTAS_BLK_SIZE`. On file release, the pending list is validated; a valid image replaces the global `rtas_firmware_flash_list`, while invalid or unauthorized data is freed. `validate_flash` stores only the first 4 KiB of a candidate image, invokes `ibm,validate-flash-image` from release, and returns either status or update-result text. `manage_flash` accepts `"0"` or `"1"` to reject or commit a temporary image through `ibm,manage-flash-image`. At reboot, `rtas_flash_firmware()` checks the hook is called for `SYS_RESTART`, cancels event scanning, builds a first list header in `rtas_data_buf` below 4 GiB, rewrites virtual pointers/lengths to big-endian physical RTAS format, calls `ibm,update-flash-64-and-reboot`, and prints final failure statuses if firmware returns.

State and persistence: the staged image persists only in kernel memory until cleanup or reboot; firmware state changes happen only through validate/manage/update RTAS calls. Per-operation status fields are protected by three mutexes. `rtas_flash_term_hook` is installed during module init and removed during exit. The shared `rtas_data_buf` is protected by `rtas_data_buf_lock` during validation and flash header construction.

Dependencies and integration points: depends on RTAS tokens from `rtas.c`, the procfs API, slab usercopy cache with 4 KiB alignment, reboot path hooks, `rtas_cancel_event_scan()` from `rtasd.c`, and RTAS progress display. It assumes RTAS list headers/pointers follow firmware ABI constraints, especially the first block-list address below 4 GiB.

Risks: staging firmware in kernel memory can consume substantial RAM; partial write failures can leave pending lists until release; proc write chunking changes user-visible write counts; pointer rewrite is in-place and intentionally hard to roll back; flashing must not proceed on halt/poweroff; any mismatch in big-endian list format can corrupt firmware update flow. Authorization is inferred from missing RTAS tokens by setting a status field, so status initialization must match the proc entry's RTAS function.

Test signals: module load/unload on RTAS platforms with and without flash tokens, proc permission and read/write behavior, staging valid/short/zero firmware images, validate/manage command handling, reboot dry-run instrumentation where possible, memory-leak checks after failed writes, and confirmation that event scan is canceled before flash.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/rtas_flash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/rtas_pci.c -->

# sources/distributed-fs/ceph-client/arch/powerpc/kernel/rtas_pci.c

Purpose: RTAS-backed PCI configuration-space operations and PHB setup for PowerPC platforms that access PCI config space through firmware calls.

Important APIs/types/functions: static RTAS token variables `read_pci_config`, `write_pci_config`, `ibm_read_pci_config`, `ibm_write_pci_config`; `config_access_valid()`, `rtas_pci_dn_read_config()`, `rtas_pci_read_config()`, `rtas_pci_dn_write_config()`, `rtas_pci_write_config()`, `rtas_pci_ops`, `is_python()`, `python_countermeasures()`, `init_pci_config_tokens()`, `get_phb_buid()`, `phb_set_bus_ranges()`, and `rtas_setup_phb()`.

Control flow: platform setup calls `init_pci_config_tokens()` to cache standard and IBM RTAS config tokens. `rtas_setup_phb()` applies the Python host bridge workaround if the PHB model matches, parses `bus-range`, assigns `rtas_pci_ops`, and records BUID from the PHB resource if IBM config tokens exist. Config reads/writes validate the `pci_dn`, range, optional extended config-space flag, and EEH blocked state; then they build `rtas_config_addr()` and call either IBM BUID-aware or standard RTAS config methods. Read paths default to all ones and integrate with EEH error detection.

State and persistence: persistent state is limited to cached tokens and PHB fields (`ops`, `buid`, bus range). The Python workaround mutates bridge MMIO state by clearing `PRG_CL_RESET_VALID`.

Dependencies and integration points: integrates with the PCI core through `struct pci_ops`, Open Firmware PCI node metadata, EEH state, `pci_dn`, `pci_controller`, and RTAS token/call APIs. Python workaround depends on OF address translation and big-endian MMIO accessors.

Risks: invalid bus-range or BUID detection can break all config cycles under a PHB. EEH blocked checks must prevent config access during recovery. Python register mapping clears a hardware bit based on model-string heuristics and assumes the register window size. Extended config access is allowed only when firmware/device node advertises it.

Test signals: boot on CHRP/pSeries PCI systems, enumerate devices behind BUID and non-BUID PHBs, read/write standard and extended config offsets, simulate EEH-blocked devices, and verify Python workaround logging on matching hardware.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/rtas_pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/rtasd.c -->

# sources/distributed-fs/ceph-client/arch/powerpc/kernel/rtasd.c

Purpose: RTAS event-scan daemon support. It polls firmware for platform events, logs RTAS errors to printk/NVRAM/in-memory proc buffers, exposes `/proc/powerpc/rtas/error_log`, and optionally enables surveillance heartbeat indicators.

Important APIs/types/functions: `pSeries_log_error()`, `printk_log_rtas()`, `log_rtas_len()`, `handle_rtas_event()`, `rtas_log_read()`, `rtas_log_poll()`, `enable_surveillance()`, `do_event_scan()`, delayed work `event_scan_work`, `rtas_event_scan()`, `retrieve_nvram_error_log()`, `start_event_scan()`, `rtas_cancel_event_scan()`, `rtas_event_scan_init()`, `rtas_init()`, and boot params `surveillance=` and `rtasmsgs=`.

Control flow: `arch_initcall(rtas_event_scan_init)` checks platform and `event-scan` token, reads `rtas-event-scan-rate`, allocates a circular vmalloc log buffer, retrieves any saved NVRAM error, then schedules delayed scanning. `do_event_scan()` repeatedly calls RTAS `event-scan` with `RTAS_EVENT_SCAN_ALL_EVENTS` until no more events; ordinary events are logged via `pSeries_log_error()`, while PRRN is rate-limited/ignored by this file. The delayed work rotates across online CPUs, adjusts the initial delay after the first pass, and enables surveillance if configured. The proc reader blocks until a circular-buffer record exists, copies one fixed-size record to userspace, and clears NVRAM when it has caught up.

State and persistence: in-memory ring state is `rtas_log_buf`, `rtas_log_start`, `rtas_log_size`, and `error_log_cnt` under `rtasd_log_lock`. On PPC64, non-boot nonfatal errors are also written to NVRAM and recovered on next boot, with logging disabled after fatal errors. `full_rtas_msgs` changes printk verbosity.

Dependencies and integration points: depends on RTAS core token/call/error-log-size APIs, pSeries/CHRP machine detection, NVRAM error-log helpers, workqueues, CPU topology, procfs, and platform `ppc_md.log_error` users. `rtas_flash.c` calls `rtas_cancel_event_scan()` before firmware update.

Risks: event scanning depends on firmware rate values; rate zero disables scanning and missing properties disable the daemon. The log buffer uses fixed-size records with sequence number plus firmware-sized payload, so reader count must be at least `rtas_error_log_buffer_max`. Locking spans NVRAM/log buffer operations; fatal paths disable logging permanently. Polling too quickly is explicitly avoided because some machines misbehave.

Test signals: boot pSeries/CHRP with event-scan token, verify daemon start, proc entry creation, blocking/nonblocking reads, NVRAM recovery/clear behavior, `rtasmsgs=1` full dumps, injected RTAS events, surveillance boot param, CPU hotplug work rescheduling, and flash module cancellation.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/rtasd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/secure_boot.c -->

# sources/distributed-fs/ceph-client/arch/powerpc/kernel/secure_boot.c

Purpose: PowerPC secure-boot and trusted-boot status discovery from firmware device-tree properties.

Important APIs/types/functions: `get_ppc_fw_sb_node()`, `is_ppc_secureboot_enabled()`, `arch_get_secureboot()`, and `is_ppc_trustedboot_enabled()`.

Control flow: the helper first searches for an IBM secureboot-compatible node (`ibm,secureboot`, `ibm,secureboot-v1`, or `ibm,secureboot-v2`). Secure boot is enabled when that node has `os-secureboot-enforcing`; if absent, the root `ibm,secure-boot` property is read and values greater than one enable it. Trusted boot similarly checks `trusted-enabled` on the secureboot node, falling back to root `ibm,trusted-boot` greater than zero. Each public function logs enabled/disabled status.

State and persistence: no kernel state is stored; results are derived each call from the live device tree and returned as booleans.

Dependencies and integration points: integrates with generic Linux `arch_get_secureboot()` and PowerPC secure-boot consumers. Relies on OF node reference management and `linux/secure_boot.h` semantics.

Risks: firmware property naming/version differences directly affect security reporting. The fallback thresholds (`secure-boot > 1`, `trusted-boot > 0`) encode platform ABI assumptions; incorrect firmware values can under-report enforcement. Repeated calls log status each time.

Test signals: boot with secureboot v1/v2 nodes and legacy root properties, confirm `/sys/kernel/security` or module-signature policy consumers see expected `arch_get_secureboot()` results, and verify node reference handling with OF debug checks.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/secure_boot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/security.c -->

# sources/distributed-fs/ceph-client/arch/powerpc/kernel/security.c

Purpose: PowerPC CPU vulnerability mitigation control and reporting for Spectre v1/v2, store-forwarding/speculative store bypass, Meltdown/L1TF-like L1D exposure, branch/cache flushes, and user access/RFI/entry flush fixups.

Important APIs/types/functions: global `powerpc_security_features`, `setup_barrier_nospec()`, `setup_spectre_v2()`, CPU vulnerability show callbacks (`cpu_show_meltdown()`, `cpu_show_spectre_v1()`, `cpu_show_spectre_v2()`, `cpu_show_spec_store_bypass()`), `setup_stf_barrier()`, `arch_prctl_spec_ctrl_get()`, `setup_count_cache_flush()`, `setup_rfi_flush()`, `setup_entry_flush()`, `setup_uaccess_flush()`, `rfi_flush_enable()`, `uaccess_flush_key`, and debugfs setters/getters for mitigation toggles.

Control flow: early boot params such as `nospectre_v1`, `nospectre_v2`, `no_stf_barrier`, `spec_store_bypass_disable=`, `no_rfi_flush`, `no_entry_flush`, `no_uaccess_flush`, and `nopti` set disable flags. Setup functions combine those flags with `cpu_mitigations_off()` and firmware/CPU feature bits to patch instruction sites (`do_*_fixups()`), enable static keys, allocate fallback flush memory, and update global state booleans. Branch-cache setup selects none/software/hardware count-cache and link-stack flushes, patching context-switch and KVM guest-exit sites accordingly. Sysfs show methods summarize the resulting vulnerability state; debugfs files can toggle several mitigations at runtime.

State and persistence: mitigation state is stored in global booleans/enums and patched kernel text. Fallback L1D flush memory is allocated from memblock and installed in each PACA. `powerpc_security_features` is read-mostly and exported through debugfs for diagnostics.

Dependencies and integration points: depends on firmware security-feature discovery, CPU feature tables, text patching, PACA/cache metadata, KVM Book3S HV patch sites, debugfs, sysfs CPU vulnerability attributes, `prctl()` speculation-control reporting, and setup code calling mitigation setup after CPU/firmware discovery.

Risks: mitigations are architecture- and firmware-feature sensitive; wrong feature bits can leave systems vulnerable or impose unnecessary overhead. Runtime debugfs toggles patch live kernel text and must maintain instruction ordering. Fallback L1D flush allocation depends on correct L1D size and low bolted/RMA memory. Some mitigations cannot be fully disabled when controlled by firmware or hardware. The `unsafe` debugfs files are powerful and should remain root-only.

Test signals: boot matrix with mitigation-on/off command lines, check `/sys/devices/system/cpu/vulnerabilities/*`, debugfs toggles, static key state for uaccess flush, KVM guest-exit patch behavior, fallback flush allocation under hash/radix modes, and microbenchmarks/regression tests for context-switch and syscall paths.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/security.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/secvar-ops.c -->

# sources/distributed-fs/ceph-client/arch/powerpc/kernel/secvar-ops.c

Purpose: minimal registration point for the platform secure-variable backend used by PowerPC secure boot.

Important APIs/types/functions: global `const struct secvar_operations *secvar_ops __ro_after_init` and `set_secvar_ops()`.

Control flow: a platform backend calls `set_secvar_ops()` once during initialization. The function warns and returns `-EBUSY` if a backend is already registered; otherwise it stores the operations pointer for later users such as `secvar-sysfs.c`.

State and persistence: stores a single read-only-after-init function table pointer. No secure variables are stored here; persistence belongs to backend firmware such as PLPKS.

Dependencies and integration points: depends on `asm/secvar.h` for operation definitions and is used by pSeries PLPKS secure-variable code before sysfs exposure.

Risks: no validation is performed beyond single-registration; a backend with missing methods can crash later sysfs code. Registration order matters because `secvar-sysfs` late init requires `secvar_ops` to be set.

Test signals: build with secure variable backends, confirm first registration succeeds and duplicate registration returns `-EBUSY`, then verify sysfs initialization sees non-NULL operations.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/secvar-ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/secvar-sysfs.c -->

# sources/distributed-fs/ceph-client/arch/powerpc/kernel/secvar-sysfs.c

Purpose: exposes firmware secure variables under `/sys/firmware/secvar`, including format reporting, per-variable size/data reads, and update writes.

Important APIs/types/functions: `format_show()`, `size_show()`, `data_read()`, `update_write()`, `update_kobj_size()`, `add_var()`, `secvar_sysfs_load()`, `secvar_sysfs_load_static()`, and `secvar_sysfs_init()`. Sysfs objects include root `secvar_kobj`, `vars` kset, per-variable kobjects, `format`, `size`, binary `data`, and binary `update` attributes.

Control flow: `late_initcall(secvar_sysfs_init)` checks `secvar_ops`, creates `/sys/firmware/secvar`, publishes the backend format string, creates the `vars` kset, sizes binary attributes from `max_size()`, creates a deprecated PLPKS config symlink, and enumerates variables either dynamically with `get_next()` or statically from `var_names`. Reads first query a variable's size, allocate a buffer, fetch data with `get()`, and serve it through `memory_read_from_buffer()`. Writes pass the sysfs-provided buffer to backend `set()`.

State and persistence: sysfs kobjects persist after init; actual secure-variable data persists in firmware/backend storage. Attribute maximum sizes are copied into `data_attr.size` and `update_attr.size` once during init.

Dependencies and integration points: depends on `secvar_ops` registration, firmware kobject infrastructure, PLPKS compatibility symlink helper, sysfs binary attributes, and backend method contracts (`format`, `get`, `set`, `max_size`, optional `get_next` or `var_names`).

Risks: sysfs write buffers are page-limited; the code warns when backend max object size exceeds `PAGE_SIZE`, meaning large updates may be impossible through this interface. Variable names become kobject names and are capped only by backend enumeration buffer size. Missing backend operations are not individually checked. Init error handling drops the root kobject but may rely on kobject cleanup for partially created children.

Test signals: boot with PLPKS/secvar backend, inspect `/sys/firmware/secvar/format`, enumerate `vars`, read each `size` and `data`, perform valid and invalid `update` writes, test dynamic and static backends, and check warning behavior when max size exceeds page size.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/secvar-sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/setup-common.c -->

# sources/distributed-fs/ceph-client/arch/powerpc/kernel/setup-common.c

Purpose: common PowerPC architecture setup shared by 32-bit and 64-bit builds. It owns machine descriptor selection, reboot/poweroff/halt glue, `/proc/cpuinfo`, initrd validation, SMP CPU-map construction, legacy I/O discovery, panic notifiers, cache-coherency checks, hardware info logging, and the main `setup_arch()` sequence.

Important APIs/types/functions: globals `ppc_md`, `machine_id`, `boot_cpuid`, cache block sizes, legacy IRQ globals, `machine_shutdown()`, `machine_restart()`, `machine_power_off()`, `machine_halt()`, `arch_get_random_seed_longs()`, `cpuinfo_op`, `check_for_initrd()`, SMP state (`threads_per_core`, `cpu_to_phys_id`), `smp_setup_cpu_maps()`, `probe_machine()`, `check_legacy_ioport()`, `setup_panic()`, `ppc_printk_progress()`, `print_system_info()`, `smp_setup_pacas()`, and `setup_arch()`.

Control flow: `setup_arch()` initializes KASAN, command line, device tree, cache info, RTAS, initrd, machine descriptor, panic notifiers, power-save hooks, serial/early console, CPU maps, xmon, SMT state, memory topology, PACAs/TLB data, hardware info, init mm, stacks, MCE, secondary CPU release, memory initialization, platform-specific setup, speculative-execution mitigations, paging, and MMU contexts. SMP CPU mapping parses CPU nodes and `ibm,ppc-interrupt-server#s`/`reg`, handles boot-core renumbering, pSeries LPAR capacity, SMT thread masks, and PACA allocation. Machine probing walks linker-provided `machdep_calls` records and selects the first compatible/probing platform.

State and persistence: establishes global architecture state for the lifetime of the kernel: machine callbacks, boot CPU IDs, cache sizes, CPU possible/present/physical maps, PACAs, panic notifiers, legacy IRQ routes, and hardware description strings. It also validates/initrd roots and may register platform devices such as `pcspkr`.

Dependencies and integration points: central integration with OF device tree, memblock, RTAS initialization, platform `ppc_md` callbacks, SMP/PACA, xmon, serial, panic/fadump, KASLR reporting, cache coherency, memory topology, MMU, livepatch, MCE, and security mitigation setup.

Risks: boot-order regressions are severe because many subsystems rely on earlier setup state. CPU thread mapping assumes a uniform thread count per CPU. Machine descriptor matching must not leave stale `ppc_md` entries. Panic notifiers run under hard IRQ-disabled/fatal contexts. Legacy I/O detection depends on device-tree heuristics. Cache-coherency mismatch intentionally BUGs because DMA would be unsafe.

Test signals: ppc32/ppc64 boot tests across pSeries, powernv, CHRP, BookE, and kdump; verify `/proc/cpuinfo`, CPU hotplug capacity, initrd detection, panic/fadump notifiers, serial console, legacy keyboard/floppy detection, machine descriptor logs, stack allocation, and mitigation setup ordering.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/setup-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/setup.h -->

# sources/distributed-fs/ceph-client/arch/powerpc/kernel/setup.h

Purpose: private header sharing setup prototypes and config-dependent stubs among `setup-common.c`, `setup_32.c`, `setup_64.c`, and closely related architecture code.

Important APIs/types/functions: declarations for `initialize_cache_info()`, `irqstack_early_init()`, `setup_power_save()`, `check_smt_enabled()`, `setup_tlb_core_data()`, `exc_lvl_early_init()`, `emergency_stack_init()`, `ppc64_bolted_size()`, `spr_default_dscr`, `kvm_cma_reserve()`, and TAU temperature helpers.

Control flow: no runtime logic except inline no-op stubs selected when configs do not provide a feature. This lets the common setup path call architecture-specific hooks unconditionally.

State and persistence: declares exported setup-time state but owns none. `spr_default_dscr` preserves firmware/kexec DSCR default on PPC64.

Dependencies and integration points: ties common setup code to PPC32 power-save, PPC64 SMT/TLB/bolted-memory helpers, BookE exception stacks, VMAP/emergency stacks, KVM CMA reservation, and TAU thermal support.

Risks: incorrect config guards here cause link failures or silently skip required setup. Because common setup calls these names early, a wrong stub can become a boot-time functional bug rather than a local compile issue.

Test signals: compile matrix across PPC32, PPC64, SMP, BookE, VMAP_STACK, KVM HV, and TAU configurations; check that `setup_arch()` links and that expected hooks are non-stubbed under the right configs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/setup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/setup_32.c -->

# sources/distributed-fs/ceph-client/arch/powerpc/kernel/setup_32.c

Purpose: 32-bit PowerPC early boot and setup helpers for relocated MMU-enabled startup, cache command-line overrides, interrupt/emergency stack allocation, BookE exception stacks, power-save callback selection, and default cache-info initialization.

Important APIs/types/functions: globals `boot_cpuid_phys`, `smp_hw_index`, `DMA_MODE_READ`, `DMA_MODE_WRITE`; `machine_init()`, boot params `l2cr=` and `l3cr=`, `ppc_init()`, `irqstack_early_init()`, VMAP `emergency_stack_init()`, BookE `exc_lvl_early_init()`, `setup_power_save()`, and `initialize_cache_info()`.

Control flow: `machine_init()` runs before `start_kernel()` after relocation, enables feature keys, early ioremap/debug, patches nocache copy/memset behavior, parses the flat device tree, initializes MMU, and sets up the kdump trampoline. Later arch init clears progress display and calls platform `ppc_md.init()`. Stack helpers allocate per-CPU hardirq/softirq and BookE critical/debug/machine-check stacks from memblock. Cache command-line options directly program L2CR/L3CR on CPUs that support them. `setup_power_save()` chooses 6xx or e500 idle callbacks based on CPU features.

State and persistence: establishes exported 32-bit boot CPU/hardware indexes, DMA mode globals, early stacks, optional emergency contexts, platform init side effects, and cache controller register settings.

Dependencies and integration points: depends on flat device-tree early parsing, feature fixups/text patching, kdump, early ioremap, platform machine callbacks, BookE exception arrays, CPU feature tables, and common setup hooks.

Risks: early boot code runs with limited services; wrong patching or device-tree pointer handling prevents boot. `l2cr=`/`l3cr=` are raw privileged hardware overrides. Stack allocation must stay in reachable low memory for early exception paths. BookE hardware CPU indexing must match SMP mappings.

Test signals: PPC32 boot matrix including Book3S and BookE, kdump boot, command-line cache override smoke tests on supported hardware, interrupt stack sanity under IRQ load, and idle/power-save behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/setup_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/setup_64.c -->

# sources/distributed-fs/ceph-client/arch/powerpc/kernel/setup_64.c

Purpose: 64-bit PowerPC early setup for PACA/bootstrap CPU state, exception mode configuration, SMT selection, cache metadata, bolted-memory limits, interrupt/emergency stacks, per-CPU areas, secondary CPU release, and hardlockup defaults.

Important APIs/types/functions: globals `spinning_secondaries`, `ppc64_pft_size`, `ppc64_caches`, `spr_default_dscr`, `__per_cpu_offset`, `__percpu_first_chunk_is_paged`; `setup_tlb_core_data()`, `check_smt_enabled()`, `early_smt_enabled()`, `fixup_boot_paca()`, `configure_exceptions()`, `cpu_ready_for_interrupts()`, `record_spr_defaults()`, `early_setup()`, `early_setup_secondary()`, `panic_smp_self_stop()`, `smp_release_cpus()`, `initialize_cache_info()`, `ppc64_bolted_size()`, `irqstack_early_init()`, `exc_lvl_early_init()`, `emergency_stack_init()`, `setup_per_cpu_areas()`, `memory_block_size_bytes()`, and `disable_hardlockup_detector()`.

Control flow: `early_setup()` installs a temporary PACA before printk-safe code, enables machine checks when possible, discovers CPU features from device tree or PVR, parses early device tree memory/CPU IDs, allocates real PACAs, configures exception endian/AIL/SCV constraints, sets up KUP before feature fixups, initializes MMU and early ioremap, records DSCR, updates PACA kernel MSR, and enables dynamic ftrace for the boot CPU. Common `setup_arch()` later calls 64-bit stack/cache/SMT/percpu hooks. Secondary CPUs run `early_setup_secondary()` to initialize MMU/KUP/interrupt readiness. Stack allocation honors bolted/RMA limits so early interrupt/NMI/MCE handlers avoid faults, with pSeries MCE stacks limited below 4 GiB for RTAS argument placement.

State and persistence: initializes PACA fields, cache topology, SMT boot thread count, per-CPU offsets, emergency stack pointers, TLB core data, DSCR default, exception mode state, and secondary CPU spinloop release function pointer.

Dependencies and integration points: depends on firmware feature bits (PAPR/OPAL), pSeries and OPAL exception configuration, KVM PR/HV constraints, radix/hash MMU, memblock, NUMA early CPU nodes, CPU feature fixups, KUP, ftrace, hardlockup detector, and common setup.

Risks: PACA must be valid before stack protector/kcov/percpu code runs. Exception endian/AIL/SCV setup is constrained by hypervisor and KVM mode. Emergency stacks must be allocated where real-mode/bolted accesses cannot fault. Cache parsing includes POWER8 device-tree workarounds. Per-CPU first-chunk selection differs by MMU mode and can panic on allocation failure.

Test signals: ppc64 boot under pSeries LPAR, PowerNV/OPAL, KVM guest, radix/hash MMU, Book3E, SMT on/off command lines, kdump, secondary CPU bring-up, NMI/MCE path smoke tests, per-cpu allocator diagnostics, and hardlockup detector default behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/setup_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/signal.c -->

# sources/distributed-fs/ceph-client/arch/powerpc/kernel/signal.c

Purpose: common PowerPC signal-delivery logic shared by 32-bit and 64-bit tasks, including FPR/VSX copy helpers, minimum frame sizing, signal stack selection, syscall restart handling, delivery dispatch, notify-resume work, transactional-memory stack handling, and bad-frame logging.

Important APIs/types/functions: `copy_fpr_to_user()`, `copy_fpr_from_user()`, `copy_vsx_to_user()`, `copy_vsx_from_user()`, checkpointed TM variants, `show_unhandled_signals`, `get_min_sigframe_size()`, `get_min_sigframe_size_compat()`, `get_sigframe()`, `check_syscall_restart()`, `do_signal()`, `do_notify_resume()`, `get_tm_stackpointer()`, and `signal_fault()`.

Control flow: user-return paths call `do_notify_resume()` with thread flags; it processes uprobes, livepatch state, pending signals, and generic resume work. `do_signal()` fetches a pending signal, applies syscall restart or EINTR conversion, restores the sigmask if none is delivered, re-enables hardware breakpoints, notifies rseq, dispatches to 32-bit legacy/RT or 64-bit RT frame builders, and calls `signal_setup_done()`. `get_sigframe()` chooses altstack and alignment, using a checkpointed TM stack pointer when an active transaction is reclaimed for signal delivery. `check_syscall_restart()` handles both sc/scv calling conventions and adjusts NIP by four bytes when restarting.

State and persistence: signal delivery mutates the current thread's user register image, saved signal mask, hardware breakpoint state, FPR/VSX checkpoint state, transaction state, and thread flags. It does not persist kernel data beyond task state.

Dependencies and integration points: integrates with generic signal core, rseq, uprobes, livepatch, hardware breakpoint code, TM reclaim/recheckpoint support, `signal_32.c`, `signal_64.c`, ptrace-visible registers, and architecture syscall trap helpers.

Risks: restart logic must preserve ABI differences between sc and scv. TM stack handling is delicate: writing the signal frame to the speculative stack would corrupt rollback state, so reclaim and MSR TS clearing must be ordered with preemption disabled. Bad user frames must be logged rate-limited and terminate safely.

Test signals: signal selftests for restart/EINTR behavior, 32/64-bit delivery, altstack alignment, rseq interruption, uprobes/livepatch return work, hardware breakpoint re-enable, VSX/FPR preservation, and TM signal delivery/abort cases.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/signal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/signal.h -->

# sources/distributed-fs/ceph-client/arch/powerpc/kernel/signal.h

Purpose: private signal ABI header for PowerPC signal implementation, declaring 32/64-bit handlers and providing optimized user-copy helpers for sigsets, FPR, VSX, and transactional checkpointed state.

Important APIs/types/functions: `get_sigframe()`, `handle_signal32()`, `handle_rt_signal32()`, `handle_rt_signal64()`, `__get_user_sigset()`, `unsafe_get_user_sigset`, FPR/VSX copy declarations, `unsafe_copy_fpr_to_user()`, `unsafe_copy_vsx_to_user()`, corresponding from-user macros, TM checkpoint copy macros, and `signal_fault()`.

Control flow: the header selects helper implementations by config. With VSX, FPR/VSX helpers handle split high/low VSR layouts; with only FPU registers, direct user copies are used; without FPU support, helpers become no-ops. Unsafe macros are designed for `user_access_begin()` regions in signal frame setup/restore. On non-PPC64 builds, `handle_rt_signal64()` is a stub returning `-EFAULT`.

State and persistence: no owned state, but helpers copy between user signal frames and `task_struct.thread` FP/vector/checkpoint state.

Dependencies and integration points: tightly coupled to `signal.c`, `signal_32.c`, optional `signal_64.c`, thread-state layout, ELF register counts, VSX offset definitions, transactional-memory configs, and generic uaccess unsafe APIs.

Risks: macro mistakes are hard to type-check and can corrupt user frames. One checkpointed FPR macro uses a fixed `failed` label in one access, so call sites must have that label convention. Register count/layout definitions must match the user ABI exactly for compat tasks.

Test signals: compile matrix across VSX, FPU-only, no-FPU, TM, PPC32, PPC64, and compat configurations; signal-frame preservation tests for FP/vector/VSX/TM state; fault-injection on user frame copies.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/signal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/signal_32.c -->

# sources/distributed-fs/ceph-client/arch/powerpc/kernel/signal_32.c

Purpose: 32-bit PowerPC and 32-bit compat signal ABI implementation. It builds and restores legacy and real-time signal frames, saves/restores GPR/FPR/Altivec/VSX/SPE/TM state, implements `swapcontext`, `rt_sigreturn`, legacy `sigreturn`, and PPC32 `debug_setcontext`.

Important APIs/types/functions: `struct sigframe`, `struct rt_sigframe`, `get_min_sigframe_size_32()`, `prepare_save_user_regs()`, `__unsafe_save_user_regs()`, `prepare_save_tm_user_regs()`, `save_tm_user_regs_unsafe()`, `restore_user_regs()`, `restore_tm_user_regs()`, `handle_rt_signal32()`, `handle_signal32()`, `do_setcontext()`, `do_setcontext_tm()`, `swapcontext`, `rt_sigreturn`, `debug_setcontext`, and `sigreturn`.

Control flow: signal delivery computes a frame using `get_sigframe()`, prepares live FP/vector state, starts a user access block, writes `siginfo`/`ucontext` or legacy `sigcontext`, saves normal or TM register sets, installs a VDSO trampoline or inline `sigreturn` syscall instructions, updates LR/SP/GPR arguments, clears FP exceptions, and returns to the handler in native-endian mode. Return syscalls locate the frame relative to the current SP, restore blocked signal masks and altstack, optionally restore TM checkpoint/speculative state, set `TIF_RESTOREALL`, and force SIGSEGV on bad frames. `swapcontext` saves the old context and restores a new one, with compat size checks for VSX availability. `debug_setcontext` applies requested single-step/branch-trace state before restoring context on PPC32.

State and persistence: mutates current task register image, FP/vector/SPE/TM thread state, signal mask, altstack, debug registers, and restore flags. User-visible persistence is the exact 32-bit signal frame ABI on the user stack.

Dependencies and integration points: depends on common signal code, VDSO32 trampolines, uaccess unsafe regions, TM helpers, FP/Altivec/VSX/SPE flush/load routines, compat siginfo/sigset helpers on PPC64, syscall tables, and ptrace register layout.

Risks: signal-frame layout is ABI-critical and includes legacy gaps/padding. TM restore must not fault after setting MSR TS and must recheckpoint under preemption disable. Compat contexts may omit VSX; accepting MSR_VSX without a VSX region is rejected. Partial restore faults can corrupt registers, so some paths force SIGSEGV instead of returning `-EFAULT`. Endian bit restoration and r2/TLS preservation differ between signal and non-signal context restore.

Test signals: 32-bit native and compat signal selftests, legacy and RT handlers, VDSO and inline trampolines, `swapcontext()` with/without VSX-sized contexts, `sigreturn` bad-frame fault tests, FP/Altivec/VSX/SPE preservation, TM active/suspended delivery and return, endian-mode signal tests, and `debug_setcontext` stepping behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/signal_32.c -->
