# sources/distributed-fs/ceph-client/arch/powerpc/kernel/fadump.c

## Purpose

`fadump.c` implements PowerPC firmware-assisted dump support. FADump lets firmware preserve memory after a crash and boot a capture kernel without using kexec. The file discovers platform support from device tree, reserves crash-preservation memory, registers and unregisters dump regions with RTAS or OPAL platform operations, builds ELF core headers for `/proc/vmcore`, exposes sysfs/debugfs controls, and triggers firmware dump on panic or system reset paths.

## Important APIs, types, and functions

The central state object is static `struct fw_dump fw_dump`, whose platform callbacks live in `fw_dump.ops`. Public architecture functions include `early_init_dt_scan_fw_dump`, `fadump_reserve_mem`, `fadump_append_bootargs`, `is_fadump_memory_area`, `should_fadump_crash`, `is_fadump_active`, `is_fadump_reserved_mem_contiguous`, `crash_fadump`, `fadump_regs_to_elf_notes`, `fadump_update_elfcore_header`, `fadump_setup_cpu_notes_buf`, `fadump_free_cpu_notes_buf`, `fadump_cleanup`, `fadump_setup_param_area`, and `setup_fadump`.

Important static helpers calculate reservation sizes, split boot memory into firmware-copy regions, locate usable reservation memory while avoiding firmware reserved ranges, populate ELF headers and PT_LOAD segments, initialize crash headers, release preserved memory, process active dumps, and implement sysfs stores. Under `CONFIG_CMA`, `fadump_cma_init` exposes the boot-memory-sized portion of reserved dump memory to CMA when safe. Under `CONFIG_PRESERVE_FA_DUMP`, the file compiles a reduced path that preserves active dump memory for a later kernel.

## Control flow

Early device-tree scan sees root `reserved-ranges`, then `rtas` or `ibm,opal` nodes and delegates platform-specific FADump discovery. Kernel parameters `fadump=` and `fadump_reserve_mem=` set enablement, `nocma`, and legacy reservation size. `fadump_reserve_mem` runs early: if supported and enabled, it calculates boot memory size from `crashkernel=`, legacy parameter, or 5 percent of RAM with platform minimums; records boot memory regions; computes total reserve size; and either reserves all crash data on capture boot or locates and reserves a reusable dump area for normal boot.

At `subsys_initcall_sync`, `setup_fadump` creates sysfs/debugfs files, prints config, processes an active dump if present, or initializes platform memory structures and registers with firmware. On panic, `crash_fadump` wins a `crashing_cpu` cmpxchg, records registers, CPU mask, and vmcoreinfo in the firmware dump header, waits briefly for secondaries after system reset, then calls `fw_dump.ops->fadump_trigger`.

Capture-kernel processing validates the crash header magic, endianness, and layout sizes, allocates an ELF core header buffer, creates PT_NOTE entries for CPU notes and vmcoreinfo, creates PT_LOAD entries for relocated boot memory and surviving RAM excluding the permanent FADump area, lets platform code add CPU notes, and publishes `elfcorehdr_addr` for `/proc/vmcore`.

## State and persistence behavior

The main persistent state is `fw_dump`, including support flags, enabled state, active/registered state, reserved area start/size, boot memory topology, crash header address, CPU notes buffer, ELF core header buffer, and optional parameter area. Memory reservation state is persisted through memblock reservations and firmware registration. Sysfs state exposes enablement, registration, reserved memory size, hotplug readiness, release controls, and appended capture-kernel boot arguments. `reserved_mrange_info` tracks firmware reserved ranges and dynamically or statically allocated memory range arrays.

## Dependencies and integration points

The file integrates with RTAS and OPAL FADump backends via `rtas_fadump_dt_scan`, `opal_fadump_dt_scan`, and platform callbacks in `fw_dump.ops`. It depends on memblock, crash dump/vmcore infrastructure, ELF core helpers, CPU masks, panic notifier behavior through `crash_kexec_post_notifiers`, sysfs, debugfs, optional CMA, optional HugeTLB disabling in the capture kernel, and `/proc/vmcore` cleanup. It also consumes boot globals such as `boot_command_line`, `saved_command_line_len`, `memory_limit`, `ppc64_rma_size`, and `elfcorehdr_addr`.

## Risks and invariants

Reservation math is high risk: overlap with firmware reserved ranges, memory holes, `memory_limit`, CMA alignment, and firmware maximum copy sizes must be handled correctly or crash capture can corrupt live memory or fail to boot. Header compatibility checks protect against old magic, endian mismatch, and structure-size mismatch. Releasing dump memory invalidates `/proc/vmcore`; ordering around `elfcorehdr_addr = ELFCORE_ADDR_ERR`, CPU notes freeing, and firmware invalidation matters. Sysfs registration changes are mutex-protected, but crash triggering intentionally runs in panic context with minimal synchronization.

## Test signals

Validation includes boots with `fadump=on/off/nocma`, `crashkernel=`, legacy `fadump_reserve_mem=`, active dump capture boots, sysfs registration toggles, `release_mem`, `/proc/vmcore` readability, appended bootargs behavior, CMA initialization, memory hotplug expectations, and RTAS/OPAL backend coverage. Fault-injection signals include allocation failures for CPU notes or ELF core header, incompatible crash headers, too many boot memory holes, no suitable reserve range, and platform register/trigger failures.
