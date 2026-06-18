<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/perf/riscv_pmu.h -->
# sources/distributed-fs/ceph-client/include/linux/perf/riscv_pmu.h

## Purpose
Defines the RISC-V PMU integration interface for Linux perf, including per-CPU hardware event tracking, PMU callbacks, counter helpers, and SBI/legacy platform names.

## Important APIs, Types, And Functions
- Constants include `RISCV_MAX_COUNTERS`, `RISCV_OP_UNSUPP`, `RISCV_PMU_SBI_PDEV_NAME`, `RISCV_PMU_LEGACY_PDEV_NAME`, `RISCV_PMU_STOP_FLAG_RESET`, and `RISCV_PMU_CONFIG1_GUEST_EVENTS`.
- `struct cpu_hw_events` tracks enabled event count, overflow IRQ, active perf events, used hardware and firmware counter bitmaps, optional SBI snapshot virtual/physical addresses, setup flag, and shadow counter values.
- `struct riscv_pmu` embeds `struct pmu`, name, IRQ handler, counter mask, callbacks for counter read/index/width/start/stop/clear, event map/init/mapped/unmapped, CSR index, per-CPU hardware events, hlist node, and PM notifier.
- Public helpers include `riscv_pmu_start()`, `riscv_pmu_stop()`, `riscv_pmu_ctr_read_csr()`, `riscv_pmu_event_set_period()`, `riscv_pmu_ctr_get_width_mask()`, `riscv_pmu_event_update()`, `riscv_pmu_legacy_skip_init()`, `riscv_pmu_alloc()`, `riscv_pmu_get_hpm_info()`, and `riscv_pmu_get_event_info()`.

## Control Flow
RISC-V PMU drivers allocate and register a `riscv_pmu`, map perf events to hardware or firmware counters, allocate a counter index, program initial values, start/stop counters, handle overflow IRQs, and update perf counts. SBI-backed PMUs may query hardware counter width/count and event encodings and may use snapshot memory to avoid clobbering during SBI calls.

## State And Persistence
State includes the PMU object, counter mask, per-CPU `cpu_hw_events`, used-counter bitmaps, snapshot buffer address/physical address, shadow counter values, and PM notifier state. Counter values persist in CSRs or firmware-managed counters while events are active.

## Dependencies And Integration Points
Depends on perf core, ptrace, interrupts, RISC-V CSR access, optional legacy PMU and SBI PMU support, physical-address handling, and PM notifications. It integrates with platform devices named for SBI or legacy PMUs and with guest-event filtering through config1.

## Risks And Edge Cases
Risks include counter width masking errors, overlapping hardware/firmware counter allocation, SBI snapshot setup races, IRQ routing failures, unsupported operation handling, guest event exposure mistakes, legacy/SBI double initialization, and event map callbacks returning encodings unsupported by firmware.

## Test Signals
Run `perf stat` and sampling on legacy and SBI PMUs, validate counter rollover based on width, CPU hotplug and suspend/resume, overflow IRQ delivery, SBI hpm/event info queries, snapshot setup/teardown, guest event filters, and unsupported event rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/perf/riscv_pmu.h -->
