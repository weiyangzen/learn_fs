<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/qcom-cpufreq-hw.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/qcom-cpufreq-hw.c

## Purpose

Drives Qualcomm CPUFreq HW/EPSS blocks that expose memory-mapped frequency domains, hardware LUTs, performance-state registers, optional interconnect/OPP scaling, CPU clocks, and LMh hardware throttling notifications.

## APIs, Types, And Functions

`struct qcom_cpufreq_soc_data` defines register offsets and LUT stride per hardware variant. `struct qcom_cpufreq_data` holds a domain MMIO base, throttle IRQ/work state, policy pointer, CCF `clk_hw`, and per-core DCVS flag. Key functions are `qcom_cpufreq_hw_read_lut()`, `qcom_cpufreq_hw_target_index()`, `qcom_cpufreq_hw_fast_switch()`, `qcom_lmh_dcvs_notify()`, `qcom_cpufreq_hw_cpu_init()`, and platform probe/remove.

## Control Flow

Platform probe gets `xo` and `alternate` clocks, checks CPU0 ICC paths, maps all frequency-domain resources, registers a CCF clock per domain, publishes an OF onecell clock provider, and registers cpufreq at postcore init. CPU policy init parses `qcom,freq-domain`, verifies hardware enable, detects per-core DCVS, builds related CPU mask, reads the LUT into dynamic OPP and cpufreq entries, and initializes optional LMh IRQ. Targeting writes a table index to the performance-state register, mirroring per-core offsets when required, and updates bandwidth through OPP if ICC scaling is enabled.

## State And Persistence

Persistent hardware state is MMIO performance state, DCVS control, current vote/domain state, and interrupt status. Software state includes domain array, dynamic OPPs, allocated frequency table, throttle work, IRQ affinity, and registered CPU clocks. CPU exit removes dynamic OPPs, OF OPP tables, LMh IRQ, and the table.

## Dependencies And Integration Points

Depends on platform resources, OF `qcom,freq-domain`, common clock, OPP, interconnect paths, IRQ handling, workqueues, architecture thermal pressure updates, and cpufreq cooling/boost/energy-model integration.

## Risks And Test Signals

The global `icc_scaling_enabled` is shared across policies and follows CPU0/LUT parsing assumptions. LMh IRQ flow alternates interrupt and polling and must avoid re-enabling during teardown. Test signals include LUT-derived OPP count, boost marking, performance-state MMIO writes, per-core DCVS writes, CPU clock rate reads, ICC bandwidth updates, LMh thermal pressure updates, and clean online/offline IRQ affinity changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/qcom-cpufreq-hw.c -->
