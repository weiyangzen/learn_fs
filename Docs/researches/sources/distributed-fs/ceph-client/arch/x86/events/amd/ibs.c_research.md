## sources/distributed-fs/ceph-client/arch/x86/events/amd/ibs.c

Purpose: AMD Instruction-Based Sampling (IBS) PMU support for fetch and op sampling, precise-event forwarding, APIC EILVT setup, NMI handling, memory data-source decoding, and power-management recovery.

Important APIs/types/state: `ibs_caps`, `struct cpu_perf_ibs`, `struct perf_ibs`, `forward_event_to_ibs()`, `perf_ibs_init()`, `perf_ibs_start/stop/add/del()`, `perf_ibs_handle_irq()`, `perf_ibs_nmi_handler()`, `perf_event_ibs_init()`, `get_ibs_caps()`, APIC setup helpers, and `amd_ibs_init()`. Two PMUs are registered as `ibs_fetch` and `ibs_op`.

Control flow: core precise CPU-cycle/uop events can be redirected to IBS op. Event init validates PMU type, grouping, config masks, filters, periods, LD latency/fetch latency/streaming-store filters, and hardware capability bits. Start programs period and enable MSRs while maintaining a four-state bit protocol (`ENABLED`, `STARTED`, `STOPPING`, `STOPPED`) to consume late NMIs. NMI handling reads valid IBS MSRs, updates counts, applies software/hardware filters, builds raw data and memory attributes, saves callchain from interrupt regs, reports overflow, and re-enables hardware unless throttled.

State/persistence: per-CPU active IBS event pointers and state bits, IBS MSRs, APIC EILVT configuration, registered PMUs, syscore PM suspend/resume hooks, and exported `ibs_caps`.

Integration points: AMD core PMU precise forwarding, generic perf PMU API, APIC/NMI infrastructure, PCI northbridge setup for family 10h EILVT, sysfs PMU formats/caps, power management, and CPU hotplug.

Risks: late NMI races are explicitly managed; changing state-bit ordering can create unhandled NMI storms or nested stop warnings. Raw samples can leak physical/kernel addresses, so privilege filtering and clearing matter. Test signals include `perf record -e ibs_fetch/.../` and `ibs_op/.../`, precise CPU-cycle forwarding, LD latency filters, exclude_user/kernel tests, raw sample privilege tests, suspend/resume, CPU hotplug, and APIC EILVT firmware fallback.
