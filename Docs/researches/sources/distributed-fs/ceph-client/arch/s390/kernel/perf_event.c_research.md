# sources/distributed-fs/ceph-client/arch/s390/kernel/perf_event.c

Purpose: supplies s390 architecture glue for the generic perf subsystem: instruction-pointer and misc flag classification, perf debug output, service-level reporting, callchain walking, and common CPUMF sysfs event formatting.

Important APIs/functions: exported perf hooks include `perf_arch_instruction_pointer()`, `perf_arch_misc_flags()`, `perf_event_print_debug()`, `perf_callchain_kernel()`, `perf_callchain_user()`, and `cpumf_events_sysfs_show()`. Internal helpers include `sie_block()`, `is_in_guest()`, `guest_is_user_mode()`, `perf_misc_flags_sf()`, `print_debug_cf()`, `print_debug_sf()`, and service-level print callbacks.

Control flow: perf sample classification first detects synthetic `pt_regs` built by `cpum_sf` using interrupt code `0x1407` and PRA interrupt parameter, then uses the embedded `perf_sf_sde_regs` guest indicator. Non-sampling-facility samples detect SIE guest execution by comparing the kernel instruction pointer with `sie_exit` and reading the guest PSW from the SIE block on the kernel stack. Debug printing queries counter and sampling facilities under local IRQ disable. The service-level initcall registers a printer that emits CPU-MF counter and sampling capabilities. Kernel callchains unwind through `unwind_for_each_frame()`, while user callchains use `arch_stack_walk_user_common()`.

State and persistence: only the static `service_level_perf` registration is retained. Debug output is generated on demand. There is no persistence beyond normal proc/sysfs/service-level reporting.

Dependencies and integration points: depends on KVM SIE stack frame layout, `sie_exit`, CPU-MF query instructions `qctri()` and `qsi()`, lowcore/stacktrace/unwind helpers, service-level infrastructure, perf sample headers, and CPUMF event attribute objects from counter/sampling/PAI files.

Risks: guest classification relies on stack layout and the SIE exit symbol; incorrect detection corrupts perf misc flags and guest IP reporting. Synthetic sampling regs must remain synchronized with `perf_cpum_sf.c`. Callchain behavior depends on reliable unwind metadata and user stack accessibility. Debug printers run with interrupts disabled and must remain bounded.

Test signals: KVM host profiling should attribute guest user/kernel samples correctly, `perf report` should show meaningful IPs for host and guest samples, `perf_event_print_debug()` should log CPUMF CF/SF status, `/proc/service_levels` should include CPU-MF lines when facilities exist, and `perf record -g` should produce kernel and user callchains.
