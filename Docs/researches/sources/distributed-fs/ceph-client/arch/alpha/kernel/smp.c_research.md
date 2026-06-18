# sources/distributed-fs/ceph-client/arch/alpha/kernel/smp.c

## Purpose
`smp.c` implements Alpha SMP discovery, secondary CPU startup through SRM/HWRPB console mechanisms, per-CPU bookkeeping, IPI dispatch, remote function calls, CPU stop, instruction-cache barriers, and TLB/icache shootdowns.

## Important APIs, Types, And Functions
- `cpu_data[NR_CPUS]` stores Alpha per-CPU data and is exported.
- `ipi_data[NR_CPUS]` stores pending IPI bitmasks; message types are reschedule, call-function, and CPU-stop.
- `smp_secondary_alive`, `smp_num_probed`, and `smp_num_cpus` coordinate boot and exported CPU counts.
- `smp_store_cpu_info()` initializes loops-per-jiffy and ASN state for a CPU.
- `smp_setup_percpu_timer()` initializes profiling timer fields.
- `smp_callin()` is the C entry point for secondary CPUs.
- `wait_for_txrdy()`, `send_secondary_console_msg()`, and `recv_secondary_console_msg()` marshal console/HWRPB IPC messages.
- `secondary_cpu_start()` prepares the secondary HWPCB, HWRPB restart fields, checksum, flags, and sends `START`.
- `smp_boot_one_cpu()`, `setup_smp()`, `smp_prepare_cpus()`, `__cpu_up()`, and `smp_cpus_done()` implement CPU discovery and bring-up.
- `send_ipi_message()` sets pending bits and calls `wripir()`.
- `handle_ipi()` dispatches reschedule, generic call-function, CPU-stop, and secondary console messages.
- `arch_smp_send_reschedule()`, `smp_send_stop()`, `arch_send_call_function_ipi_mask()`, and `arch_send_call_function_single_ipi()` are architecture hooks.
- `smp_imb()`, `flush_tlb_all()`, `flush_tlb_mm()`, `flush_tlb_page()`, `flush_tlb_range()`, and `flush_icache_user_page()` implement cross-CPU cache/TLB maintenance.

## Control Flow
`setup_smp()` reads HWRPB processor entries, identifies runnable CPUs by flag mask `0x1cc`, copies boot PAL revision, and sets possible/present masks. `smp_prepare_cpus()` initializes IPI state and boot CPU info; if multiple CPUs are available, `__cpu_up()` calls `smp_boot_one_cpu()`. Startup prepares a minimal HWPCB for the idle task, publishes `__smp_callin` in HWRPB restart fields, updates the HWRPB checksum, toggles CPU flags, and sends `START` to the secondary console. The secondary enters `smp_callin()`, sets itself online, initializes traps/interrupts/clockevent/MM state, notifies CPU startup, calibrates delay after boot CPU releases it, stores CPU info, signals alive, and enters idle.

IPI senders set bits in per-CPU `ipi_data`, memory-barrier around bit publication, and issue hardware IPIs. `handle_ipi()` atomically drains the bitmask and invokes scheduler, generic call-function, or halt actions. TLB and icache flush paths perform local flushes when possible, invalidate remote MM contexts for single-user address spaces, or use `smp_call_function()` for synchronized remote maintenance.

## State And Persistence
State includes exported `cpu_data`, `ipi_data` pending bits, HWRPB per-CPU flags/HWPCB/restart fields, Linux CPU masks, `smp_secondary_alive`, and per-MM context arrays. It is all runtime state. Secondary startup mutates firmware-visible HWRPB structures.

## Dependencies And Integration Points
The file depends on SRM/HWRPB layout, Alpha PAL calls (`wrmces`, `wrent`, `wripir`), trap and clock initialization, machine-vector `smp_callin`, generic SMP hotplug hooks, scheduler IPIs, generic call-function APIs, Alpha ASN/MMU context management, and TLB/cache flush helpers.

## Risks
- Secondary startup is firmware-protocol-sensitive; HWRPB flags, checksum, restart address, and console IPC ordering are critical.
- Bring-up timeouts can hang or leave CPUs stuck depending on firmware behavior.
- IPI pending bits require memory barriers and atomic exchange; missed ordering can lose work.
- TLB flush optimizations invalidate remote `mm->context[cpu]` based on `mm_users`, which must remain consistent with Alpha ASN semantics.
- Some comments and constants are legacy and hardware-specific, making changes hard to validate without real Alpha SMP hardware.

## Test Signals
- SMP boot logs show probed and activated CPU counts.
- CPU hotplug/bring-up path returns online status for each secondary.
- Scheduler reschedule IPIs and generic `smp_call_function()` work under load.
- TLB shootdown stress with multithreaded mmap/munmap/mprotect workloads.
- `smp_imb()` and executable page updates behave correctly across CPUs.
