# sources/distributed-fs/ceph-client/arch/x86/events/intel/pt.c

## Purpose

`pt.c` implements the Intel Processor Trace perf PMU named `intel_pt`. It exposes Intel PT CPUID capabilities through sysfs, validates perf event configuration, allocates and programs AUX buffers using ToPA or single-range output, starts/stops tracing through RTIT MSRs, handles PT PMIs, integrates with perf address filters, and coordinates with VMX/LBR exclusivity. The file is CPU-affine and keeps one `struct pt` context per CPU plus one global `struct pt_pmu`.

## Important APIs, Types, And Functions

The public/exported entry points are `intel_pt_validate_cap()`, `intel_pt_validate_hw_cap()`, `intel_pt_interrupt()`, `intel_pt_handle_vmx()`, `cpu_emergency_stop_pt()`, and `is_intel_pt_event()`. `pt_init()` is the `arch_initcall` that registers the perf PMU.

Important internal groups are:

- Capability/sysfs setup: `pt_caps`, `pt_cap_show()`, `pt_pmu_hw_init()`, `pt_attr_groups`.
- Event validation/configuration: `pt_event_valid()`, `pt_config_filters()`, `pt_config()`, `pt_config_start()`, `pt_config_stop()`.
- AUX buffer/ToPA management: `struct topa`, `struct topa_page`, `topa_alloc()`, `topa_insert_table()`, `topa_insert_pages()`, `pt_buffer_setup_aux()`, `pt_buffer_free_aux()`.
- Runtime pointer/accounting paths: `pt_config_buffer()`, `pt_read_offset()`, `pt_handle_status()`, `pt_update_head()`, `pt_buffer_reset_offsets()`, `pt_buffer_reset_markers()`.
- Perf callbacks: `pt_event_init()`, `pt_event_add()`, `pt_event_start()`, `pt_event_stop()`, `pt_event_del()`, `pt_event_snapshot_aux()`, `pt_event_destroy()`.

## Control Flow

Initialization rejects CPUs without `X86_FEATURE_INTEL_PT`, refuses to load if PT was already enabled at boot, reads platform timing data and CPUID leaf 20 capability bits, builds sysfs cap attributes, checks ToPA support, sets PMU capabilities, and calls `perf_pmu_register("intel_pt")`.

Event creation flows through `pt_event_init()`: type match, `pt_event_valid()` config bit/capability checks, LBR exclusivity acquisition, and address-filter context allocation. Adding an event ensures only one active PT event per CPU context. Starting an event begins a perf AUX transaction, maps `aux_head` into the ToPA/current output region, places STOP/INT markers for non-snapshot mode, programs output base/mask MSRs, writes RTIT filter/control MSRs, and sets tracing enabled unless VMX blocks it. Stopping clears NMI/pause/resume gates, disables TraceEn, reads final hardware offsets/status, updates AUX head/data size, and ends the AUX transaction.

On a PT PMI, `intel_pt_interrupt()` disables tracing, translates hardware output registers into buffer offsets, handles RTIT status/error/STOP conditions, advances ToPA regions when required, updates perf AUX accounting, ends the current AUX output, and starts another AUX output transaction if the event is still active.

## State And Persistence Behavior

Persistent runtime state is in per-CPU `pt_ctx`, global `pt_pmu`, perf event `hw` fields, and per-event AUX `struct pt_buffer`. The driver does not persist trace data itself; PT data is written by hardware into perf AUX pages and exposed through perf ring-buffer semantics. `pt_buffer` tracks ToPA tables, current entry, offsets, logical head, collected data size, snapshot/single-range mode, wrap state, and STOP/INT marker positions. `pt->output_base` and `pt->output_mask` cache MSR values to avoid redundant writes. `pause_allowed`, `resume_allowed`, and `handle_nmi` are explicit race gates between PMU callbacks and PMIs.

## Dependencies And Integration Points

The file depends on x86 CPUID/MSR helpers, Intel RTIT MSR definitions from `<asm/intel_pt.h>`, perf AUX APIs, perf address filters, CPU hot/VMX coordination hooks, KVM-exported PT capability helpers, and x86 LBR exclusivity. Userspace integration is through `/sys/bus/event_source/devices/intel_pt/{caps,format}` and perf AUX trace collection.

## Risks And Edge Cases

Risk is concentrated in hardware programming and concurrent control paths. Incorrect capability validation can cause #GP MSR writes. ToPA marker placement must not overwrite unread AUX data. Single-entry ToPA has special truncation and PMI-margin handling. Snapshot mode changes accounting and disables PMI use. VMX can clear TraceEn on systems where PT cannot trace post-VMXON, so `intel_pt_handle_vmx()` deliberately flags partial traces and suppresses writes while VMX is active. Address filters must clamp non-canonical virtual ranges safely. Memory barriers around TraceEn disable and AUX head publication are important for consumer visibility.

## Test Signals

Useful signals include successful boot registration of `intel_pt`, correct sysfs caps/format files, `perf record -e intel_pt// --per-thread` and snapshot AUX tests, address-filter acceptance/rejection tests, VMX/KVM tracing gap tests, stress with small AUX buffers to exercise STOP/INT marker handling, CPU-specific validation for unsupported MTC/CYC/PSB/PTWRITE bits, and lockdep/KASAN coverage for buffer allocation/free and PMI races.
