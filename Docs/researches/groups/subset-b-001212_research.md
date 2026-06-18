# subset-b-001212 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-riscv-sbi.c -->
# sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-riscv-sbi.c

## Purpose

`cpuidle-riscv-sbi.c` is the RISC-V SBI HSM cpuidle backend. It converts CPU idle-state device-tree nodes into per-HART `cpuidle_driver` instances, maps each state to an SBI suspend parameter, and optionally models hierarchical CPU power domains through genpd when SBI OSI-style topology data is present.

## Important APIs, Types, And Functions

The central per-CPU state is `struct sbi_cpuidle_data`, holding the parsed SBI states and optional attached PM-domain device. `struct sbi_domain_state` carries a selected domain-level suspend parameter from genpd `power_off`. `sbi_cpuidle_enter_state()` calls `riscv_sbi_hart_suspend()` directly, while `sbi_enter_domain_idle_state()` and `sbi_enter_s2idle_domain_idle_state()` wrap runtime PM/genpd and CPU PM around domain-aware suspend. `sbi_dt_parse_state_node()`, `sbi_cpuidle_dt_init_states()`, `sbi_cpuidle_init_cpu()`, `sbi_pd_init()`, and `sbi_genpd_probe()` perform DT parsing and registration.

## Control Flow

`arch_initcall()` registers a synthetic `sbi-cpuidle` platform device only if SBI HSM is supported. Probe first detects whether all CPU nodes provide named `power-domains`, then builds `/cpus/power-domains` providers, initializes each present CPU's driver, and installs CPU hotplug callbacks if any CPU was attached to a PM domain. For each CPU, state 0 is architectural WFI, DT states start at index 1, and the deepest state is replaced by the domain-aware enter callback when OSI topology is attached.

## State And Persistence Behavior

Per-CPU parsed state arrays are devm-managed. Runtime PM references keep attached CPU PM-domain devices active while CPUs are online. Domain state is intentionally cleared after idle exit and CPU hotplug down so stale genpd choices cannot leak into the next suspend attempt.

## Dependencies And Integration Points

It depends on RISC-V SBI HSM, RISC-V suspend validation, DT idle-state bindings, genpd, CPU PM, runtime PM, CPU hotplug, cpuidle cooling, and the cpuidle core. The `riscv,sbi-suspend-param` property is the firmware ABI.

## Risks And Test Signals

Risks include invalid SBI suspend parameters, partial CPU topology causing OSI mode to be disabled, failure unwinds that unregister per-CPU drivers, and genpd provider cleanup leaving stale domains. Test by booting RISC-V DTs with and without `/cpus/power-domains`, checking cpuidle states and cooling registration, CPU hotplugging, entering s2idle, and tracing SBI suspend parameters selected for CPU and domain states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-riscv-sbi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-tegra.c -->
# sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-tegra.c

## Purpose

`cpuidle-tegra.c` implements ARM cpuidle states for Tegra20, Tegra30, Tegra114, and Tegra124. It exposes C1 WFI, C7 CPU-core power gating, and CC6 CPU-cluster power gating where the SoC and power-management firmware support them.

## Important APIs, Types, And Functions

`tegra_idle_driver` defines the cpuidle states. `tegra_cpuidle_enter()` is the common enter callback and adjusts Tegra30 CPU0 C7 requests into C1 or CC6 when necessary. Deep states use `tegra_cpuidle_state_enter()`, which disables FIQs, marks LP2 entry, calls CPU PM and context tracking, and dispatches to `tegra_cpuidle_c7_enter()` or `tegra_cpuidle_cc6_enter()`. CC6 coordination uses `tegra_cpuidle_coupled_barrier()`, `tegra_idle_barrier`, and `tegra_abort_flag`.

## Control Flow

Probe waits for PMC suspend mode, disables states according to DT/PM_SLEEP/SoC limitations, applies Tegra114-style C7 latency and s2idle setup where applicable, and registers the driver with coupled CPUs. CC6 requires secondary CPUs to park, CPU0 to wait for rail-off readiness, entry to LP2, and then unpark of secondaries on exit. C7 may call trusted firmware `prepare_idle` before `cpu_suspend()`.

## State And Persistence Behavior

State selection is mostly static after probe, but `tegra_cpuidle_pcie_irqs_in_use()` can disable CC6 on Tegra20 if PCIe IRQ loss risk is detected. Coupled barrier and abort flag are transient global synchronization state. Hardware flow controller, PMC, CPU clocks, reset, and GIC coupling hold persistent power state.

## Dependencies And Integration Points

It integrates with Tegra PMC, PM, flow controller, fuse/chip ID, trusted foundations firmware, ARM `cpu_suspend`, CPU PM, local FIQ control, coupled cpuidle, and PCIe workaround users through an exported symbol.

## Risks And Test Signals

Risks include secondary CPU parking timeouts, lost SGIs during GIC shutdown, incorrect state disabling by SoC ID or suspend mode, and CC6/PCIe interrupt loss. Test by booting all supported Tegra SoCs, inspecting state availability, exercising CPU hotplug-like parking paths, running suspend/resume and s2idle, using PCIe on Tegra20, and tracing failed deep-state entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-tegra.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-ux500.c -->
# sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-ux500.c

## Purpose

`cpuidle-ux500.c` is the ST-Ericsson DB8500/ux500 ARM cpuidle driver. It registers a normal ARM WFI state plus `ApIdle`, a retention state entered only when all online CPUs are idle and PRCMU can safely manage GIC decoupling and wakeups.

## Important APIs, Types, And Functions

`ux500_idle_driver` defines state 0 as `ARM_CPUIDLE_WFI_STATE` and state 1 as `ApIdle`. `ux500_enter_idle()` uses the global `master` atomic and `master_lock` spinlock to select a last-man-in CPU. PRCMU calls include `prcmu_gic_decouple()`, `prcmu_is_cpu_in_wfi()`, `prcmu_copy_gic_settings()`, `prcmu_gic_pending_irq()`, `prcmu_pending_irq()`, and `prcmu_set_power_state()`.

## Control Flow

Probe enables ARM, RTC, and ABB wakeups through PRCMU and registers cpuidle. At idle entry each CPU increments `master`; if it is the last online CPU it attempts to become master, decouples GIC, verifies the peer CPU is already in WFI, copies interrupt state, checks no interrupts are pending, and requests `PRCMU_AP_IDLE`. All CPUs then execute WFI; on failure the master recouples GIC manually.

## State And Persistence Behavior

The driver maintains only global coordination state. Actual retention and GIC coupling state is PRCMU-managed. `master` is decremented on every exit, and `recouple` ensures manual recovery when the PRCMU did not take ownership.

## Dependencies And Integration Points

It depends on the dbx500 PRCMU MFD interface, ARM cpuidle WFI helpers, SMP CPU count/state, spinlocks, atomics, and the platform device named `db8500-cpuidle`.

## Risks And Test Signals

Risks include deadlocks or missed unlocks around `master_lock`, incorrect peer-WFI detection, interrupt races between GIC and PRCMU checks, and wakeup-source misconfiguration. Test with SMP idle workloads, RTC/ABB/ARM wakeups, forced pending interrupts during entry, and cpuidle statistics showing `ApIdle` use only when both CPUs can idle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-ux500.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-zynq.c -->
# sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-zynq.c

## Purpose

`cpuidle-zynq.c` is a minimal Xilinx Zynq cpuidle platform driver. It advertises two states: standard ARM WFI and a nominal `RAM_SR` state intended to combine WFI with DDR self refresh.

## Important APIs, Types, And Functions

`zynq_idle_driver` contains the two states and uses `zynq_enter_idle()` for `RAM_SR`. The enter routine currently only calls `cpu_do_idle()` and returns the selected index; comments mark where DDR self-refresh programming would belong.

## Control Flow

The builtin platform driver binds to `cpuidle-zynq`, logs startup from `zynq_cpuidle_probe()`, and calls `cpuidle_register()`. State 0 is the ARM cpuidle WFI macro. State 1 has low exit latency, long target residency, and no timer-stop or RCU-idle flags.

## State And Persistence Behavior

There is no driver-private dynamic state, no suspend/resume path, and no explicit hardware register persistence. The only persistent state is the registered cpuidle driver and its counters in the core.

## Dependencies And Integration Points

It depends on the ARM cpuidle helper macros, `cpu_do_idle()`, platform driver registration, and the cpuidle core. Integration is via the platform device name rather than OF match data in this file.

## Risks And Test Signals

The principal risk is that `RAM_SR` does not implement RAM self refresh despite its name, so it may mislead power validation. Test by checking state registration, verifying actual DDR/self-refresh hardware behavior externally, comparing residency counters, and ensuring no timer or interrupt behavior is assumed beyond WFI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-zynq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle.c -->
# sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle.c

## Purpose

`cpuidle.c` is the cpuidle core: it owns per-CPU cpuidle devices, dispatches governor-selected idle states, records residency statistics, handles suspend-to-idle entry, and manages device registration, enablement, sysfs creation, and idle-handler installation.

## Important APIs, Types, And Functions

Global state includes per-CPU `cpuidle_devices` and `cpuidle_dev`, `cpuidle_lock`, `cpuidle_detected_devices`, `enabled_devices`, `off`, and `initialized`. Public APIs include `cpuidle_select()`, `cpuidle_enter()`, `cpuidle_enter_state()`, `cpuidle_reflect()`, `cpuidle_use_deepest_state()`, `cpuidle_register_device()`, `cpuidle_unregister_device()`, `cpuidle_register()`, `cpuidle_unregister()`, `cpuidle_pause()`, and `cpuidle_resume()`.

## Control Flow

Registration installs a driver, initializes each per-CPU device, creates CPU sysfs, enables governor state, and installs the idle handler when at least one device is enabled. Idle entry writes the next hrtimer, routes coupled states through coupled machinery, switches to broadcast timers when local timers stop, leaves the MM if requested, enters RCU idle/context tracking as needed, calls the driver's state callback, restores IRQ/tick state, and updates usage, time, rejected, above, and below counters.

## State And Persistence Behavior

Per-device `states_usage`, last residency, next hrtimer, polling limit, forced latency limit, and registration flags persist across idle entries. The module parameter `off` disables cpuidle at boot, while `param_governor` is declared here for governor selection. Sysfs user disables are recorded in state usage.

## Dependencies And Integration Points

It integrates with governors, tick/nohz and broadcast timers, hrtimers, scheduler idle state, RCU/context tracking, CPU hotplug-style registration, suspend-to-idle, PM QoS, sysfs, module ownership, tracepoints, and optional coupled idle support.

## Risks And Test Signals

Risks include IRQ state leaks from drivers, incorrect RCU-idle flags, stale scheduler idle-state pointers, racey governor switches, and bad accounting when enter callbacks reject states. Test by toggling governors and per-state sysfs disables, enabling s2idle, running timer-stop states, validating tracepoints, checking residency counters, and exercising driver register/unregister error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle.h -->
# sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle.h

## Purpose

`cpuidle.h` is the private header for the cpuidle implementation. It exposes shared globals and internal helpers across the core, driver registration, governor, sysfs, poll-state, and optional coupled-idle files.

## Important APIs, Types, And Functions

It declares `param_governor`, `cpuidle_curr_governor`, `cpuidle_prev_governor`, `cpuidle_governors`, `cpuidle_detected_devices`, `cpuidle_lock`, and `cpuidle_driver_lock`. It also declares core helpers such as `cpuidle_enter_state()`, idle-handler install/uninstall, governor lookup/switching, and sysfs add/remove functions. Under `CONFIG_ARCH_NEEDS_CPU_IDLE_COUPLED`, it declares coupled-idle validation, registration, unregister, and entry functions; otherwise it provides stubs.

## Control Flow

There is no runtime control flow in the header, but the inline coupled stubs are important: non-coupled builds always report states as not coupled and return failure if the coupled entry path is accidentally requested.

## State And Persistence Behavior

The header does not allocate state itself; it defines the internal visibility boundary for persistent core lists, locks, governor pointers, and coupled-idle behavior.

## Dependencies And Integration Points

It depends on the public cpuidle types and is included by cpuidle core, driver, governor, sysfs, and architecture/platform idle code using private interfaces.

## Risks And Test Signals

Risks include leaking internal APIs outside `drivers/cpuidle`, mismatched coupled stubs masking build-time assumptions, and lock-order changes affecting all users. Test signals are compile coverage across coupled and non-coupled configurations, governor switching, sysfs registration, and coupled platform boot tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/driver.c -->
# sources/distributed-fs/ceph-client/drivers/cpuidle/driver.c

## Purpose

`driver.c` manages registration and lookup of cpuidle drivers. It supports both a single global driver and per-CPU drivers under `CONFIG_CPU_IDLE_MULTIPLE_DRIVERS`, normalizes driver state latency/residency fields, and configures tick broadcast support for states that stop local timers.

## Important APIs, Types, And Functions

The file owns `cpuidle_driver_lock`, plus either per-CPU `cpuidle_drivers` or global `cpuidle_curr_driver`. Key functions are `cpuidle_register_driver()`, `cpuidle_unregister_driver()`, `cpuidle_get_driver()`, `cpuidle_get_cpu_driver()`, and `cpuidle_driver_state_disabled()`. Internal helpers include `__cpuidle_driver_init()`, `__cpuidle_set_driver()`, `__cpuidle_unset_driver()`, and `cpuidle_setup_broadcast_timer()`.

## Control Flow

Registering validates the driver and coupled states, rejects disabled cpuidle, fills the default cpumask, converts microsecond and nanosecond latency/residency fields both ways, warns if exit latency exceeds target residency, assigns the driver, enables broadcast timers on all CPUs in the driver's mask when needed, and may switch to a driver-requested governor. Unregistering disables broadcast and restores the previous governor if it had been overridden.

## State And Persistence Behavior

Driver assignment persists globally or per CPU. `drv->bctimer` is set during initialization and cleared at unregister. `cpuidle_driver_state_disabled()` modifies per-device disable bits when devices exist, or marks the driver state unusable before cpumask registration.

## Dependencies And Integration Points

It integrates with tick broadcast, cpumasks, CPU iteration, cpuidle governors, lock-protected driver/device state, and optional multiple-driver support.

## Risks And Test Signals

Risks include driver assignment conflicts, incorrect broadcast enablement on timer-stop states, governor override not restoring, and latency unit conversion mistakes. Test by registering multiple drivers in supported configs, checking broadcast timer setup, toggling driver-disabled states, and verifying governor changes on driver probe/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/driver.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/dt_idle_genpd.c -->
# sources/distributed-fs/ceph-client/drivers/cpuidle/dt_idle_genpd.c

## Purpose

`dt_idle_genpd.c` provides reusable helpers for cpuidle drivers that model CPU idle topology with generic PM domains. It parses domain idle states, allocates `generic_pm_domain` objects, wires parent/child domain topology, and attaches CPU devices to named domains.

## Important APIs, Types, And Functions

`dt_idle_pd_alloc()` allocates a PM domain, names it from the DT node, parses genpd idle states with `of_genpd_parse_idle_states()`, and stores driver-specific state data via a caller-provided parser. `dt_idle_pd_free()` frees state data and the domain. `dt_idle_pd_init_topology()` and `dt_idle_pd_remove_topology()` add/remove subdomains from child `power-domains` links. `dt_idle_attach_cpu()` and `dt_idle_detach_cpu()` bind CPUs to named PM domains.

## Control Flow

Allocation parses each domain-idle-state node, allocates a `u32` data payload per state, and stores it in `genpd_power_state.data`. Topology init scans children under a CPU power-domain container, finds nodes with parent domains, and calls genpd add-subdomain APIs. CPU attachment marks the attached PM-domain device IRQ-safe, runtime-resumes it if the CPU is online, and marks it as a syscore device.

## State And Persistence Behavior

Domain state arrays and per-state data persist until `dt_idle_pd_free()`. Attached CPU devices hold runtime PM references while online. The code does not own provider registration; callers must call genpd provider APIs and cleanup consistently.

## Dependencies And Integration Points

It depends on OF genpd parsing, generic PM domains, runtime PM, CPU devices, DT `power-domains` links, and cpuidle platform drivers such as RISC-V SBI.

## Risks And Test Signals

Risks include memory leaks on partial parse failure, mismatched topology add/remove ordering, CPU devices left attached, and bad parser callbacks accepting invalid firmware states. Test by injecting malformed domain idle states, validating genpd topology, CPU hotplugging, and checking runtime PM references after driver teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/dt_idle_genpd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/dt_idle_genpd.h -->
# sources/distributed-fs/ceph-client/drivers/cpuidle/dt_idle_genpd.h

## Purpose

`dt_idle_genpd.h` is the public local interface for cpuidle DT/genpd helpers. It lets cpuidle platform drivers use CPU PM-domain topology when `CONFIG_DT_IDLE_GENPD` is enabled while compiling clean stubs otherwise.

## Important APIs, Types, And Functions

The enabled declarations cover `dt_idle_pd_free()`, `dt_idle_pd_alloc()`, `dt_idle_pd_init_topology()`, `dt_idle_pd_remove_topology()`, `dt_idle_attach_cpu()`, and `dt_idle_detach_cpu()`. Disabled builds return success or NULL-style no-op values and free nothing.

## Control Flow

There is no direct runtime flow beyond the inline stubs. The header shapes caller behavior: drivers can call these helpers unconditionally and interpret NULL/0 results when the feature is not compiled in.

## State And Persistence Behavior

The header does not allocate state. It controls whether PM-domain state can exist at all for a given build.

## Dependencies And Integration Points

It forward-declares `device_node` and `generic_pm_domain` and integrates with DT idle drivers that support hierarchical CPU idle state selection.

## Risks And Test Signals

Risks include callers failing to handle NULL from disabled stubs, assuming topology exists on non-genpd builds, and missing compile coverage for both branches. Test with `CONFIG_DT_IDLE_GENPD=y` and disabled builds, plus platform probe paths using all helper calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/dt_idle_genpd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/dt_idle_states.c -->
# sources/distributed-fs/ceph-client/drivers/cpuidle/dt_idle_states.c

## Purpose

`dt_idle_states.c` parses CPU idle-state device-tree bindings into cpuidle driver state entries. It provides a common implementation for architecture drivers that describe idle states as CPU phandles.

## Important APIs, Types, And Functions

The exported entry point is `dt_init_idle_driver()`. `init_state_node()` fills a `cpuidle_state` with the matched enter function, s2idle callback, latency, target residency, flags, name, and description. `idle_state_valid()` verifies that every CPU in the driver's cpumask references the same idle-state phandle at each index.

## Control Flow

The parser selects the first CPU in the driver cpumask, walks its indexed idle-state phandles, matches each node against the caller's `of_device_id` table, skips disabled state nodes, verifies uniformity across CPUs, and initializes `drv->states` from `start_idx`. It stops on the first missing phandle and sets `drv->state_count` to the final index.

## State And Persistence Behavior

The function writes persistent cpuidle state fields in the caller's driver. It does not retain DT node references beyond parsing. Latency comes from `wakeup-latency-us` or falls back to entry plus exit latency.

## Dependencies And Integration Points

It depends on OF CPU node helpers, cpumasks, cpuidle state flags, and firmware binding properties including `min-residency-us`, `idle-state-name`, and `local-timer-stop`.

## Risks And Test Signals

Risks include firmware phandle mismatches across CPUs, state array overflow, missing latency/residency properties, and drivers passing wrong match-data enter callbacks. Test with valid and malformed DT idle-state sets, disabled nodes, heterogeneous CPU masks, and state counts near `CPUIDLE_STATE_MAX`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/dt_idle_states.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/dt_idle_states.h -->
# sources/distributed-fs/ceph-client/drivers/cpuidle/dt_idle_states.h

## Purpose

`dt_idle_states.h` declares the DT idle-state parser used by cpuidle platform drivers.

## Important APIs, Types, And Functions

The sole API is `dt_init_idle_driver(struct cpuidle_driver *drv, const struct of_device_id *matches, unsigned int start_idx)`. The `matches` table supplies compatible strings and enter callbacks through `.data`; `start_idx` allows drivers to reserve index 0 for architectural WFI or polling states.

## Control Flow

The header has no control flow. It defines the dependency contract between cpuidle drivers and the parser implementation.

## State And Persistence Behavior

The parser called through this declaration mutates the provided driver; the header owns no state.

## Dependencies And Integration Points

It depends on `struct cpuidle_driver` and `struct of_device_id` being visible to callers. It is used by RISC-V SBI and similar DT-based idle drivers.

## Risks And Test Signals

Risks are mostly build-interface issues: missing include dependencies, signature drift, or callers misunderstanding the return value as total states instead of parsed DT states. Test through compile coverage and DT idle driver probes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/dt_idle_states.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/governor.c -->
# sources/distributed-fs/ceph-client/drivers/cpuidle/governor.c

## Purpose

`governor.c` manages cpuidle governor registration, selection, and latency constraint lookup. Governors decide which idle state the core should enter on each idle loop iteration.

## Important APIs, Types, And Functions

It owns `param_governor`, `cpuidle_governors`, `cpuidle_curr_governor`, and `cpuidle_prev_governor`. `cpuidle_register_governor()` adds a governor and may switch to it based on boot parameter and rating. `cpuidle_find_governor()` performs case-insensitive lookup. `cpuidle_switch_governor()` disables all detected devices under the old governor, switches the pointer, re-enables devices, and reinstalls the idle handler. `cpuidle_governor_latency_req()` combines per-CPU device PM QoS, global CPU latency, and wakeup-latency QoS.

## Control Flow

Governors register during postcore init. Registration under `cpuidle_lock` rejects duplicate names, appends to the list, and switches if no governor exists, if the boot parameter names it, or if it has a higher rating than the current non-forced governor. Switching pauses idle entry by uninstalling the handler before reconfiguring devices.

## State And Persistence Behavior

The governor list and current/previous governor pointers persist for the kernel lifetime. Device governor state is reset through each governor's enable/disable hooks during switches.

## Dependencies And Integration Points

It integrates with cpuidle device lists, sysfs governor writes, PM QoS, CPU devices, and boot/module parameters.

## Risks And Test Signals

Risks include switching with devices enabled, rating/boot-parameter precedence mistakes, and latency constraint unit errors. Test by listing and changing governors in sysfs, booting with `cpuidle.governor`, setting PM QoS latency constraints, and validating device enable hooks run.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/governor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/governors/Makefile -->
# sources/distributed-fs/ceph-client/drivers/cpuidle/governors/Makefile

## Purpose

This Makefile selects which cpuidle governor objects are built from Kconfig symbols.

## Important APIs, Types, And Functions

It maps `CONFIG_CPU_IDLE_GOV_LADDER` to `ladder.o`, `CONFIG_CPU_IDLE_GOV_MENU` to `menu.o`, `CONFIG_CPU_IDLE_GOV_TEO` to `teo.o`, and `CONFIG_CPU_IDLE_GOV_HALTPOLL` to `haltpoll.o`.

## Control Flow

There is no runtime flow. Build-time object inclusion determines which governors can register at postcore init and appear in `/sys/devices/system/cpu/cpuidle/available_governors`.

## State And Persistence Behavior

The Makefile owns no runtime state, but missing object inclusion means no persistent governor registration for that algorithm.

## Dependencies And Integration Points

It integrates Kconfig choices with the cpuidle governor registration source files under `drivers/cpuidle/governors`.

## Risks And Test Signals

Risks include Kconfig symbols not matching object names or adding a governor without updating the Makefile. Test by building each governor configuration and checking available governors at boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/governors/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/governors/gov.h -->
# sources/distributed-fs/ceph-client/drivers/cpuidle/governors/gov.h

## Purpose

`gov.h` defines constants shared by cpuidle governors that reason about short residencies and safe timer ranges.

## Important APIs, Types, And Functions

`RESIDENCY_THRESHOLD_NS` is 15 microseconds and is used to decide when checking the closest timer is worth the overhead. `SAFE_TIMER_RANGE_NS` is two scheduler tick periods and marks a range where the nearest timer is close enough that extra selection adjustment is unnecessary.

## Control Flow

There is no executable control flow. `menu` and `teo` include these thresholds in their selection heuristics.

## State And Persistence Behavior

The constants are compile-time only and store no state.

## Dependencies And Integration Points

It depends on `NSEC_PER_USEC` and `TICK_NSEC` definitions from included kernel headers in the consuming files.

## Risks And Test Signals

Risks are heuristic regressions: changing thresholds can alter tick-stopping behavior and shallow/deep state selection. Test through idle microbenchmarks, timer-heavy workloads, and power/latency comparisons for menu and TEO.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/governors/gov.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/governors/haltpoll.c -->
# sources/distributed-fs/ceph-client/drivers/cpuidle/governors/haltpoll.c

## Purpose

`haltpoll.c` implements a guest-oriented cpuidle governor that alternates between polling and halt-style idle to reduce wakeup latency in virtualized environments where short sleeps are common.

## Important APIs, Types, And Functions

Module parameters control polling behavior: `guest_halt_poll_ns`, `guest_halt_poll_shrink`, `guest_halt_poll_grow`, `guest_halt_poll_grow_start`, and `guest_halt_poll_allow_shrink`. `haltpoll_select()` chooses state 0 polling or state 1 halt based on latency constraints, previous state, and poll timeout. `adjust_poll_limit()` grows or shrinks `dev->poll_limit_ns`. `haltpoll_reflect()` records the actual state and adjusts the poll limit after halt.

## Control Flow

At postcore init the governor registers only when `kvm_para_available()` is true. Selection returns polling for strict latency, alternates halt after a timed-out poll, and otherwise keeps the tick running while polling. Reflection grows the poll window if halt residency was below the global cap and shrinks it if sleeps exceed the cap.

## State And Persistence Behavior

Persistent per-CPU state is stored in generic `cpuidle_device` fields: `last_state_idx`, `poll_limit_ns`, `poll_time_limit`, and `last_residency_ns`. Module parameters can be changed at runtime through sysfs/module interfaces.

## Dependencies And Integration Points

It integrates with KVM paravirtual detection, cpuidle poll state behavior, scheduler tick control, power tracepoints, and governor registration.

## Risks And Test Signals

Risks include wasting CPU by over-polling, never growing from zero under unexpected wake patterns, and assuming state 1 is a useful halt state. Test in KVM guests with latency-sensitive workloads, module parameter changes, poll timeout tracing, and CPU utilization/power measurements.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/governors/haltpoll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/governors/ladder.c -->
# sources/distributed-fs/ceph-client/drivers/cpuidle/governors/ladder.c

## Purpose

`ladder.c` implements the legacy cpuidle ladder governor. It promotes or demotes one state at a time based on the previous residency and fixed promotion/demotion counters.

## Important APIs, Types, And Functions

Per-CPU `struct ladder_device` holds `struct ladder_device_state` entries with promotion/demotion thresholds and counters. `ladder_enable_device()` initializes thresholds from state exit latencies and sets the initial state. `ladder_select_state()` enforces latency constraints and updates promotion/demotion counters. `ladder_reflect()` records the actual entered state.

## Control Flow

Selection starts from `dev->last_state_idx`, treats polling state 0 specially, and immediately returns state 0 when latency requirement is zero. If the last adjusted residency exceeds the promotion threshold for enough consecutive selections and the next state fits the latency constraint, it promotes. If the state is disabled, violates latency, or under-runs the demotion threshold, it demotes.

## State And Persistence Behavior

The governor persists per-CPU counters across idle entries and resets them when devices are enabled. The governor rating is raised from 10 to 25 when nohz is disabled, making ladder preferable for periodic tick systems.

## Dependencies And Integration Points

It depends on cpuidle device residency accounting, PM QoS latency, tick nohz status, and governor registration.

## Risks And Test Signals

Risks include slow adaptation to workload changes, poor choices with tickless idle, and state index assumptions when state 0 is polling. Test with nohz on/off, PM QoS constraints, state disables, and workloads alternating short and long idle intervals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/governors/ladder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/governors/menu.c -->
# sources/distributed-fs/ceph-client/drivers/cpuidle/governors/menu.c

## Purpose

`menu.c` implements the menu governor, which predicts idle duration from the next timer event and recent interval history, then selects the deepest state satisfying latency and target-residency constraints.

## Important APIs, Types, And Functions

Per-CPU `struct menu_device` stores correction factors, recent intervals, next timer duration, bucket, and pending-update flags. `menu_select()` performs state selection, `menu_reflect()` defers update work, `menu_update()` adjusts prediction factors after wakeup, and `get_typical_interval()` detects repeating wakeup patterns with variance and outlier handling.

## Control Flow

Selection first updates prior metrics if needed. It computes a typical interval from the last eight samples, optionally obtains nohz sleep length and next tick delta, applies a bucketed correction factor, honors latency constraints, and scans enabled states in order. It may retain the tick for polling or short predicted idle, and corrects the selected state downward if the tick will arrive before the selected state's target residency.

## State And Persistence Behavior

Correction factors start at unity on enable and decay with measured wakeups. Interval history persists per CPU. `next_timer_ns` and `bucket` are saved so `menu_update()` can compare measured residency to the prediction.

## Dependencies And Integration Points

It depends on tick/nohz sleep length APIs, cpuidle accounting, PM QoS latency, scheduler tick wakeup detection, and shared governor thresholds in `gov.h`.

## Risks And Test Signals

Risks include bad predictions with irregular interrupts, shallow-state lock-in when the tick is stopped, fallback to polling under tight latency, and arithmetic corner cases in variance/factor updates. Test with periodic timers, interrupt-heavy workloads, nohz enabled/disabled, PM QoS constraints, and residency/miss counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/governors/menu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/governors/teo.c -->
# sources/distributed-fs/ceph-client/drivers/cpuidle/governors/teo.c

## Purpose

`teo.c` implements the timer-events-oriented cpuidle governor. It emphasizes timer wakeup patterns, using per-state bins of timer "hits" and non-timer "intercepts" to select states and decide whether to stop the scheduler tick.

## Important APIs, Types, And Functions

Per-CPU `struct teo_cpu` stores sleep length, `state_bins`, totals, tick intercepts, short-idle metrics, and tick wakeup state. `teo_update()` decays and updates metrics after each wakeup. `teo_select()` chooses the next state. `teo_find_shallower_state()` caps selections by expected duration. `teo_reflect()` records the entered state and tick wakeup flag.

## Control Flow

On selection, TEO updates metrics for the previous state, finds the deepest enabled state and the latency-constrained state, examines shallower intercept totals to detect early wakeup dominance, applies latency constraints, and avoids reading nohz sleep length when a shallow choice is already clear. If needed, it gets the next timer duration, adjusts for stopped ticks, caps by target residency, and may keep the tick running for short selected states.

## State And Persistence Behavior

Metrics decay by shifting and grow by `PULSE`, so recent behavior dominates while old history persists for smoothing. `sleep_length_ns` is saved to classify the next wakeup. `last_state_idx` is reset after update to avoid duplicate accounting.

## Dependencies And Integration Points

It integrates with tick/nohz, scheduler clock residency, cpuidle accounting, PM QoS latency, and shared thresholds in `gov.h`.

## Risks And Test Signals

Risks include misclassifying timer versus non-timer wakeups, over-stopping or under-stopping the tick, and biased bins when target residencies are close. Test with timer-dominated and interrupt-dominated workloads, nohz-stopped scenarios, PM QoS constraints, polling state timeouts, and deep-state residency counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/governors/teo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/poll_state.c -->
# sources/distributed-fs/ceph-client/drivers/cpuidle/poll_state.c

## Purpose

`poll_state.c` supplies the generic cpuidle polling state used by drivers that want a state 0 busy-wait option.

## Important APIs, Types, And Functions

`cpuidle_poll_state_init()` fills `drv->states[0]` with name `POLL`, zero latency/residency, power usage `-1`, `CPUIDLE_FLAG_POLLING`, and the `poll_idle()` enter callback. `poll_idle()` enables interrupts, marks the current task polling, loops on `need_resched()`, calls `cpu_relax()`, and stops after `cpuidle_poll_time()` expires.

## Control Flow

On entry the function records local time, clears `poll_time_limit`, enables IRQs, and uses `current_set_polling_and_test()` to avoid polling when reschedule is already pending. It checks elapsed time every `POLL_IDLE_RELAX_COUNT` relax operations, sets `poll_time_limit` when the limit is reached, disables IRQs, clears polling, and returns the state index.

## State And Persistence Behavior

The function updates `dev->poll_time_limit`; governors use that as feedback. The cached poll duration lives in `dev->poll_limit_ns` and is computed by the cpuidle core.

## Dependencies And Integration Points

It depends on scheduler polling flags, local clock, IRQ flag helpers, `cpu_relax()`, cpuidle driver state layout, and governor feedback fields.

## Risks And Test Signals

Risks include excessive CPU burn, incorrect IRQ state on exit, and stale poll limits after state disables. Test with haltpoll/menu/teo polling use, reschedule latency measurements, sysfs state disable changes, and tracepoints showing poll timeout behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/poll_state.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/cpuidle/sysfs.c

## Purpose

`sysfs.c` exposes cpuidle global controls and per-CPU/per-state statistics through sysfs. It provides governor selection, current driver reporting, per-state counters, user disable toggles, and optional s2idle counters.

## Important APIs, Types, And Functions

Global attributes are `available_governors`, `current_driver`, `current_governor`, and read-only governor fallback. Per-device objects use `struct cpuidle_device_kobj`; per-state objects use `struct cpuidle_state_kobj`. Exported helpers include `cpuidle_add_interface()`, `cpuidle_add_sysfs()`, `cpuidle_add_device_sysfs()`, and their remove counterparts. State attributes expose name, desc, latency, residency, power, usage, rejected, time, disable, above, below, default_status, and s2idle usage/time when available.

## Control Flow

The global CPU root gets a `cpuidle` group. Each CPU gets a `cpuidle` kobject, then state subdirectories and optionally a driver subdirectory for multiple-driver builds. Writes to `current_governor` call `cpuidle_switch_governor()`. Writes to state `disable` require `CAP_SYS_ADMIN`, set or clear the user disable bit, and reset the device poll-time cache.

## State And Persistence Behavior

Kobjects include completions so removal waits for release. Sysfs disable persists in `state_usage.disable` until changed or the device is reinitialized. Time values are reported in microseconds from nanosecond accounting.

## Dependencies And Integration Points

It integrates with CPU subsystem devices, kobjects, sysfs ops, cpuidle locks, governor lists, driver locks, capabilities, and optional suspend/multiple-driver configs.

## Risks And Test Signals

Risks include kobject lifetime leaks, lock inversions during governor changes, exposing writable state to unprivileged users, and stale driver pointers in multiple-driver sysfs. Test by CPU online/offline, switching governors from sysfs, toggling state disables, removing drivers, and checking no kobject warnings appear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/crypto/Kconfig

## Purpose

`drivers/crypto/Kconfig` is the top-level hardware crypto configuration menu. It gates all hardware crypto devices under `CRYPTO_HW`, sources vendor submenus, and declares many platform accelerator options and their crypto API dependencies.

## Important APIs, Types, And Functions

This file is declarative Kconfig. It defines `menuconfig CRYPTO_HW`, sources `drivers/crypto/allwinner/Kconfig`, and includes options for PadLock, s390 protected keys, Talitos, OMAP, Atmel, CCP, QCE, Rockchip, Tegra, Xilinx, Safexcel, CCREE, TI, and other drivers. Each config selects needed crypto primitives such as `CRYPTO_SKCIPHER`, `CRYPTO_HASH`, `CRYPTO_ENGINE`, `CRYPTO_AES`, `CRYPTO_SHA*`, `HW_RANDOM`, or fallback libraries.

## Control Flow

Build configuration flows from enabling `CRYPTO_HW`; if disabled, the submenu and all nested hardware drivers are skipped. Selected options then control Makefile object inclusion and compile-time feature branches in individual drivers.

## State And Persistence Behavior

Kconfig has no runtime state, but selected symbols persist in `.config` and determine which modules, algorithms, debug features, RNG providers, and fallback dependencies exist in the kernel image.

## Dependencies And Integration Points

It integrates architecture symbols, platform dependencies, crypto API algorithm selections, hwrng, debugfs-dependent debug options, and sourced vendor Kconfig files.

## Risks And Test Signals

Risks include missing `select` dependencies causing link or runtime algorithm failures, overly broad defaults, impossible dependency combinations, and vendor submenu omissions. Test with randconfig/allmodconfig, architecture-specific builds, and verifying requested algorithms register when each driver is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/Makefile -->
# sources/distributed-fs/ceph-client/drivers/crypto/Makefile

## Purpose

`drivers/crypto/Makefile` maps hardware crypto Kconfig symbols to object files and vendor subdirectories.

## Important APIs, Types, And Functions

It includes direct objects such as `geode-aes.o`, `hifn_795x.o`, `mxs-dcp.o`, `padlock-aes.o`, `qcom-rng.o`, `s5p-sss.o`, `sa2ul.o`, and `talitos.o`, plus subdirectories such as `allwinner/`, `ccp/`, `caam/`, `marvell/`, `qce/`, `rockchip/`, `tegra/`, `virtio/`, `intel/`, `xilinx/`, and others. It also composes `omap-aes-driver-objs` from `omap-aes.o` and `omap-aes-gcm.o`.

## Control Flow

There is no runtime flow. Kbuild uses the `obj-$(CONFIG_...)` assignments to include built-in objects or modules. Some directories are always visited with `obj-y` because their own Kconfig/Makefiles decide which children build.

## State And Persistence Behavior

The Makefile owns no runtime state; it controls the build graph that determines module names and linked objects.

## Dependencies And Integration Points

It integrates top-level crypto Kconfig symbols with individual driver source directories and compound object definitions.

## Risks And Test Signals

Risks include stale object names, missing new driver directories, incorrect always-built subdirectories, and compound object ordering problems such as the explicit Atmel I2C init ordering note. Test with allmodconfig, allyesconfig, and targeted module builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/allwinner/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/crypto/allwinner/Kconfig

## Purpose

`drivers/crypto/allwinner/Kconfig` declares the Allwinner crypto accelerator family and feature options for the sun4i Security System, sun8i Crypto Engine, and sun8i Security System.

## Important APIs, Types, And Functions

`CRYPTO_DEV_ALLWINNER` gates the submenu and defaults to yes on `ARCH_SUNXI`. `CRYPTO_DEV_SUN4I_SS` selects MD5, SHA1, AES, DES library, RNG, and skcipher support. Optional symbols enable sun4i PRNG and debugfs stats. `CRYPTO_DEV_SUN8I_CE` selects skcipher, crypto engine, ECB/CBC, AES, DES, and RNG; optional symbols add debug stats, hash, PRNG, and TRNG. `CRYPTO_DEV_SUN8I_SS` similarly controls the A80/A83T security system.

## Control Flow

Kconfig selection determines which subdirectories build and which optional source files are included. Feature booleans also guard code paths for PRNG, TRNG, hash registration, and debug statistics.

## State And Persistence Behavior

Selections persist in kernel configuration and decide runtime algorithm availability, module names, and debugfs/hwrng exposure.

## Dependencies And Integration Points

It depends on `ARCH_SUNXI` or `COMPILE_TEST`, PM, and crypto framework symbols. It integrates with the Allwinner Makefile and per-driver Makefiles.

## Risks And Test Signals

Risks include missing primitive selections, optional features enabled without matching source support, and dependencies that block compile-test coverage. Test with Allwinner defconfigs, compile-test builds, optional debug/hash/RNG combinations, and crypto self-tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/allwinner/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/allwinner/Makefile -->
# sources/distributed-fs/ceph-client/drivers/crypto/allwinner/Makefile

## Purpose

This Makefile dispatches enabled Allwinner crypto drivers to their implementation subdirectories.

## Important APIs, Types, And Functions

It maps `CONFIG_CRYPTO_DEV_SUN4I_SS` to `sun4i-ss/`, `CONFIG_CRYPTO_DEV_SUN8I_CE` to `sun8i-ce/`, and `CONFIG_CRYPTO_DEV_SUN8I_SS` to `sun8i-ss/`.

## Control Flow

There is no runtime control flow. Kbuild descends only into selected driver directories.

## State And Persistence Behavior

It owns no runtime state; build outputs persist as built-in objects or modules selected by Kconfig.

## Dependencies And Integration Points

It connects `drivers/crypto/allwinner/Kconfig` symbols to the subdirectory Makefiles that assemble each driver.

## Risks And Test Signals

Risks include forgotten subdirectory wiring for a new Allwinner driver or symbol drift after renames. Test by enabling each Allwinner driver independently and confirming the expected module objects are built.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/allwinner/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun4i-ss/Makefile -->
# sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun4i-ss/Makefile

## Purpose

The sun4i Security System Makefile assembles the `sun4i-ss` driver module or built-in object from its core, hash, cipher, and optional PRNG sources.

## Important APIs, Types, And Functions

It creates `sun4i-ss.o` when `CONFIG_CRYPTO_DEV_SUN4I_SS` is enabled. The base object list is `sun4i-ss-core.o`, `sun4i-ss-hash.o`, and `sun4i-ss-cipher.o`. `sun4i-ss-prng.o` is appended when `CONFIG_CRYPTO_DEV_SUN4I_SS_PRNG` is enabled.

## Control Flow

There is no runtime flow, but source composition determines which algorithm templates have implementations available at link time.

## State And Persistence Behavior

No runtime state is owned here. Build-time symbol selections persist in the module contents.

## Dependencies And Integration Points

It integrates with the Allwinner parent Makefile and Kconfig options for sun4i SS and PRNG support.

## Risks And Test Signals

Risks include enabling PRNG registration without linking the PRNG implementation or adding a source file without updating this list. Test by building with PRNG on and off and running module load plus crypto RNG self-tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun4i-ss/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun4i-ss/sun4i-ss-cipher.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun4i-ss/sun4i-ss-cipher.c

## Purpose

`sun4i-ss-cipher.c` implements synchronous skcipher operations for the Allwinner sun4i Security System FIFO engine. It supports AES, DES, and 3DES in CBC and ECB modes, using software fallback for unsupported lengths or awkward scatterlists.

## Important APIs, Types, And Functions

The main data path is `sun4i_ss_cipher_poll()`, with a fast aligned path in `sun4i_ss_opti_poll()` and fallback path in `sun4i_ss_cipher_poll_fallback()`. Mode-specific exported callbacks include AES/DES/3DES CBC/ECB encrypt/decrypt functions. TFM lifecycle uses `sun4i_ss_cipher_init()` and `sun4i_ss_cipher_exit()`. Key setup is handled by `sun4i_ss_aes_setkey()`, `sun4i_ss_des_setkey()`, and `sun4i_ss_des3_setkey()`.

## Control Flow

Cipher requests validate non-empty SGs, reject non-block-multiple request lengths to fallback, and choose the optimized path when all source and destination SG offsets and lengths are 32-bit aligned. Hardware entry writes key registers, optional IV registers, and `SS_CTL`, streams input words into `SS_RXFIFO`, drains output from `SS_TXFIFO`, then clears the control register. CBC IV is updated from ciphertext on encryption or restored from the saved tail block on decryption.

## State And Persistence Behavior

TFM context stores key words, key length, key mode, hardware context, and fallback TFM. Request context stores mode, backup IV, and embedded fallback request. Device access is serialized with `ss->slock`; runtime PM is held for the TFM lifetime.

## Dependencies And Integration Points

It depends on skcipher API, scatterwalk/sg mapping iterators, DES key verification, runtime PM, SS register definitions, and algorithm templates registered by `sun4i-ss-core.c`.

## Risks And Test Signals

Risks include unaligned SG linearization bugs, IV corruption on in-place CBC decrypt, FIFO polling stalls, fallback flag propagation mistakes, and key material lifetime. Test with crypto manager vectors for AES/DES/3DES CBC/ECB, unaligned SGs, in-place and out-of-place requests, zero length, non-block-multiple fallback, and runtime PM cycling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun4i-ss/sun4i-ss-cipher.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun4i-ss/sun4i-ss-core.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun4i-ss/sun4i-ss-core.c

## Purpose

`sun4i-ss-core.c` is the platform and algorithm registration core for the Allwinner sun4i Security System. It probes clocks, reset, MMIO, variant data, runtime PM, registers hash/cipher/RNG algorithms, and exposes optional debugfs statistics.

## Important APIs, Types, And Functions

`ss_algs[]` contains the MD5, SHA1, AES CBC/ECB, DES CBC/ECB, 3DES CBC/ECB, and optional PRNG algorithm templates. `sun4i_ss_probe()` initializes hardware resources and registers algorithms. `sun4i_ss_remove()` unregisters them. Runtime PM callbacks `sun4i_ss_pm_suspend()` and `sun4i_ss_pm_resume()` assert/deassert reset and disable/enable bus and module clocks. Variants `ss_a10_variant` and `ss_a33_variant` describe SHA1 digest endianness.

## Control Flow

Probe maps MMIO, loads match data, gets `mod` and `ahb` clocks, obtains optional reset, sets module clock rate, logs clock compliance, initializes runtime PM, temporarily resumes the device to read the die ID from `SS_CTL`, then iterates `ss_algs[]` registering each algorithm with the correct crypto API. Failure unwinds already registered algorithms and disables runtime PM.

## State And Persistence Behavior

`struct sun4i_ss_ctx` persists as platform data and holds base address, clocks, reset, spinlock, buffers, optional PRNG seed, variant, and debugfs dentries. Algorithm templates store back-pointers to the single device and optional stats.

## Dependencies And Integration Points

It depends on platform devices, OF match compatibles `allwinner,sun4i-a10-crypto` and `allwinner,sun8i-a33-crypto`, common clocks, reset controller, runtime PM, crypto API registration, debugfs, and the cipher/hash/PRNG implementation files.

## Risks And Test Signals

Risks include global algorithm templates limiting multiple device instances, clock-rate assumptions, missing debugfs cleanup, partial registration unwind errors, and SHA1 endian variant mistakes. Test probe/remove, runtime suspend/resume, crypto self-tests, A10 versus A33 SHA1 vectors, and debugfs stats under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun4i-ss/sun4i-ss-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun4i-ss/sun4i-ss-hash.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun4i-ss/sun4i-ss-hash.c

## Purpose

`sun4i-ss-hash.c` implements MD5 and SHA1 ahash operations for the sun4i Security System. It feeds data through the SS FIFO, preserves partial blocks and intermediate digest state, and performs software-style padding for finalization.

## Important APIs, Types, And Functions

TFM lifecycle uses `sun4i_hash_crainit()` and `sun4i_hash_craexit()`. Request APIs are `sun4i_hash_init()`, `sun4i_hash_update()`, `sun4i_hash_final()`, `sun4i_hash_finup()`, and `sun4i_hash_digest()`. Export/import helpers support MD5 and SHA1 state migration. The main worker `sun4i_hash()` handles update and final logic.

## Control Flow

Small non-final data is buffered in `op->buf`. For hardware processing, the driver restores arbitrary IV registers when continuing a previous hash, enables the SS with MD5 or SHA1 mode, streams full 32-bit words from SGs while linearizing partial bytes, and either saves intermediate digest registers or finalizes. Finalization writes remaining bytes, appends the 0x80 bit, zero padding, and bit length in SHA1 big-endian or MD5 little-endian format, sets `SS_DATA_END`, waits for completion, delays briefly, and reads digest registers.

## State And Persistence Behavior

`struct sun4i_req_ctx` stores mode, byte count uploaded to hardware, intermediate hash words, a 64-byte partial buffer, length, and flags. Runtime PM is held by the TFM. Hardware access is serialized with `ss->slock`.

## Dependencies And Integration Points

It depends on ahash internals, MD5/SHA1 state formats, SG mapping iterators, unaligned stores, SS FIFO/register definitions, runtime PM, and variant SHA1 endianness from core.

## Risks And Test Signals

Risks include padding off-by-one errors, timeout on `SS_DATA_END`, partial-SG handling bugs, export/import state mismatch, and digest endianness regressions. Test MD5/SHA1 crypto vectors across update/final/digest/export/import paths, small messages, large scatterlists, unaligned SGs, and A10/A33 variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun4i-ss/sun4i-ss-hash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun4i-ss/sun4i-ss-prng.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun4i-ss/sun4i-ss-prng.c

## Purpose

`sun4i-ss-prng.c` implements the optional crypto API RNG interface for the sun4i Security System pseudo-random generator.

## Important APIs, Types, And Functions

`sun4i_ss_prng_seed()` copies caller-provided seed bytes into `ss->seed`. `sun4i_ss_prng_generate()` resumes the device, enables PRNG continuous mode, repeatedly writes the current seed to key registers, reads generated words from `SS_TXFIFO`, updates the stored seed from key registers, and returns generated bytes.

## Control Flow

Generation rounds `dlen` down to a multiple of four bytes and processes chunks of `SS_DATA_LEN` bits. It holds `ss->slock` while touching registers and clears `SS_CTL` before releasing the lock. Debug builds increment request and byte counters. Runtime PM is acquired for each generate call and released afterward.

## State And Persistence Behavior

The persistent PRNG seed lives in `struct sun4i_ss_ctx` when the PRNG option is enabled. The seed is updated after every generated chunk, so output depends on prior calls and the last seed operation.

## Dependencies And Integration Points

It depends on the RNG algorithm template in `sun4i-ss-core.c`, SS register definitions, runtime PM, and the global SS spinlock.

## Risks And Test Signals

Risks include silently ignoring trailing non-word bytes, weak or uninitialized seed use, PRNG state shared across all consumers, and register access races with other SS algorithms. Test crypto RNG self-tests, seed/generate sequences, odd output lengths, concurrent cipher/hash/RNG requests, and runtime PM suspend during idle periods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun4i-ss/sun4i-ss-prng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun4i-ss/sun4i-ss.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun4i-ss/sun4i-ss.h

## Purpose

`sun4i-ss.h` is the shared private header for the sun4i Security System driver. It defines register offsets, control bits, FIFO helpers, device/algorithm/TFM/request contexts, and cross-file function prototypes.

## Important APIs, Types, And Functions

Register definitions include `SS_CTL`, key registers, IV registers, `SS_FCSR`, digest registers, and RX/TX FIFOs. Control bits describe PRNG mode, IV mode, ECB/CBC/CTS, AES key size, encrypt/decrypt, AES/DES/3DES/SHA1/MD5/PRNG operation, `SS_DATA_END`, and enable. Core types are `struct sun4i_ss_ctx`, `struct sun4i_ss_alg_template`, `struct sun4i_tfm_ctx`, `struct sun4i_cipher_req_ctx`, and `struct sun4i_req_ctx`.

## Control Flow

The header has no executable flow, but its constants drive how cipher, hash, PRNG, and core files program the hardware and share state. The `fallback_req` fields are deliberately last in request contexts to allow variable crypto request sizes.

## State And Persistence Behavior

It defines persistent device state, per-algorithm stats/back-pointers, per-TFM key and fallback state, per-request IV backup, and hash buffering/intermediate state. Optional PRNG seed state is included only when configured.

## Dependencies And Integration Points

It pulls in Linux crypto, skcipher, ahash, RNG, DES/AES/SHA/MD5, platform, reset, runtime PM, IO, scatterlist, and module interfaces.

## Risks And Test Signals

Risks include register bit drift from hardware documentation, mismatched context sizes with algorithm templates, and incorrect alignment or field ordering for fallback requests. Test through full driver builds, sparse/compile warnings, crypto manager tests, and hardware register traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun4i-ss/sun4i-ss.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun8i-ce/Makefile -->
# sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun8i-ce/Makefile

## Purpose

The sun8i Crypto Engine Makefile assembles the `sun8i-ce` driver from its core and optional algorithm implementation files.

## Important APIs, Types, And Functions

It builds `sun8i-ce.o` when `CONFIG_CRYPTO_DEV_SUN8I_CE` is enabled. Base objects are `sun8i-ce-core.o` and `sun8i-ce-cipher.o`. Optional objects are `sun8i-ce-hash.o`, `sun8i-ce-prng.o`, and `sun8i-ce-trng.o` under their corresponding Kconfig symbols.

## Control Flow

There is no runtime flow. Build-time composition determines whether hash, PRNG, and TRNG algorithm registration has implementation code available.

## State And Persistence Behavior

No runtime state is stored here. The selected object set persists in the built module or kernel image.

## Dependencies And Integration Points

It integrates with Allwinner Kconfig and parent Makefile selections for the sun8i CE driver.

## Risks And Test Signals

Risks include missing optional sources for enabled symbols or stale object names. Test by building all combinations of hash, PRNG, and TRNG options and loading the resulting module on supported SoCs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun8i-ce/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun8i-ce/sun8i-ce-cipher.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun8i-ce/sun8i-ce-cipher.c

## Purpose

`sun8i-ce-cipher.c` implements skcipher support for the Allwinner sun8i Crypto Engine. It prepares DMA task descriptors for AES and 3DES cipher requests, queues work through `crypto_engine`, and falls back to software for requests the hardware cannot safely process.

## Important APIs, Types, And Functions

`sun8i_ce_cipher_need_fallback()` enforces hardware constraints. `sun8i_ce_cipher_fallback()` dispatches to a fallback skcipher. `sun8i_ce_cipher_prepare()` maps keys, IVs, and scatterlists and fills a `struct ce_task`. `sun8i_ce_cipher_unprepare()` unmaps DMA and updates CBC IVs. `sun8i_ce_cipher_do_one()` runs a task and finalizes the engine request. Public request callbacks are `sun8i_ce_skencrypt()` and `sun8i_ce_skdecrypt()`. TFM/key APIs are `sun8i_ce_cipher_init()`, `sun8i_ce_cipher_exit()`, `sun8i_ce_aes_setkey()`, and `sun8i_ce_des3_setkey()`.

## Control Flow

Encrypt/decrypt sets request direction, checks fallback gates for SG count, crypt length, IV size, zero length, 16-byte multiple, and 32-bit SG alignment, then selects a CE flow and transfers the request to that flow's crypto engine. The worker fills task control fields from variant algorithm and block-mode tables, maps key/IV/SGs, runs `sun8i_ce_run_task()`, unmaps everything, updates IV state, and completes the skcipher request.

## State And Persistence Behavior

TFM context stores a DMA-friendly key buffer, key length, CE device, and fallback TFM. Request context stores direction, flow, DMA addresses, mapped SG counts, bounce IV, backup IV, and embedded fallback request. Runtime PM is held for the TFM lifetime and released on exit.

## Dependencies And Integration Points

It depends on crypto_engine, skcipher API, DMA mapping, scatterwalk IV handling, DES3 key verification, runtime PM, CE variant descriptors and helpers from `sun8i-ce.h`, and core functions that allocate flows and submit tasks.

## Risks And Test Signals

Risks include DMA mapping leaks on error, using original SG counts instead of mapped counts, strict `% 16` fallback that may exclude DES-sized requests, IV update mistakes for decrypt, flow selection races, and fallback flag propagation. Test AES/3DES ECB/CBC vectors, in-place/out-of-place DMA, unaligned and over-`MAX_SG` fallback cases, runtime PM, concurrent flows, and DMA API debug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun8i-ce/sun8i-ce-cipher.c -->
