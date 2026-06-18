<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/vpa-dtl.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/perf/vpa-dtl.c

Purpose: exposes PowerVM shared-processor Dispatch Trace Log data as a perf AUX-output PMU named `vpa_dtl`, allowing userspace perf tooling to collect raw DTL entries for cede, preempt, fault, or all dispatch-log events.

Important APIs/types/functions: defines event IDs `DTL_CEDE`, `DTL_PREEMPT`, `DTL_FAULT`, and `DTL_ALL`; `struct vpa_dtl` tracks the per-CPU DTL buffer and last index; `struct vpa_pmu_buf` tracks AUX buffer mapping, size, head, and boot timebase metadata; `vpa_dtl_event_init()`, `vpa_dtl_event_add()`, `vpa_dtl_event_del()`, `vpa_dtl_setup_aux()`, and `vpa_dtl_free_aux()` implement the PMU; `vpa_dtl_hrtimer_handle()` polls because hardware does not interrupt on overflow.

Control flow: initialization registers the PMU only on SPLPAR L1 hosts. Event init requires perfmon capability, sampling mode, no branch stack, a valid DTL mask, exclusive `dtl_access_lock` ownership, and a kmem-cache DTL buffer. Add registers the buffer with the hypervisor, clears `lppaca.dtl_idx`, enables the selected DTL mask, and starts a pinned hrtimer. Each timer tick copies new wrapped/non-wrapped DTL entries into the perf AUX area, prepending boot timebase/frequency once. Delete stops the timer, unregisters the DTL buffer, frees memory, and clears the enable mask.

State and persistence: per-CPU `vpa_dtl_cpu` stores active hypervisor buffers; per-CPU `vpa_pmu_ctx` stores output handles; `dtl_global_refc` and `dtl_global_lock` serialize PMU ownership against other DTL readers. AUX-private `vpa_pmu_buf` persists for the mmaped AUX area and tracks ring position and boot-time metadata. Hypervisor-visible state is the registered DTL buffer and lppaca enable/index fields.

Dependencies and integration: depends on `CONFIG_PPC_SPLPAR`, `asm/dtl.h`, `register_dtl()`, `unregister_dtl()`, `lppaca_of()`, `dtl_cache`, `dtl_access_lock`, perf AUX APIs, hrtimers, timebase helpers, and PowerVM firmware feature detection. It integrates with perf record/report/script via raw AUX records rather than normal samples.

Risks and test signals: lock/refcount error paths can leak `dtl_access_lock` or allocated buffers; AUX head accounting and wrap handling can truncate entries; event init allocates before add, so destroy callbacks are important; only L1 shared-processor hosts should load it. Test on SPLPAR L1 with `perf record -e vpa_dtl/dtl_all/ -m,aux`, small AUX buffers, high dispatch churn, concurrent `/proc/powerpc/vcpudispatch_stats`, invalid masks, counting-mode rejection, and event teardown under failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/vpa-dtl.c -->
