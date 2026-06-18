# sources/distributed-fs/ceph-client/drivers/acpi/cppc_acpi.c

## Purpose
Implements the ACPI CPPC library used primarily by CPU frequency and scheduler-related code. It parses per-CPU `_CPC` and `_PSD` packages, maps CPPC registers across PCC, SystemMemory, SystemIO, and FFH address spaces, exposes read-only per-CPU CPPC sysfs data, and exports helpers for performance capabilities, feedback counters, desired performance, autonomous selection, EPP, performance limits, and perf/frequency conversion.

## Important APIs, Types, And Functions
`struct cppc_pcc_data` stores PCC channel state per subspace: mailbox channel, timing limits, ownership bits, pending write state, write counters, locks, wait queue, and reference count. `pcc_data[]` maps subspace IDs to that state; `cpu_pcc_subspace_idx` and `cpc_desc_ptr` are per-CPU. Each `struct cpc_desc` contains parsed CPC register resources, `_PSD` domain info, sysfs kobject, CPU ID, and RMW lock.

Probe and cleanup are exported as `acpi_cppc_processor_probe()` and `acpi_cppc_processor_exit()`. Domain helpers include `acpi_cpc_valid()`, `cppc_allow_fast_switch()`, and `acpi_get_psd_map()`. PCC helpers include `check_pcc_chan()`, `send_pcc_cmd()`, `register_pcc_channel()`, and `pcc_data_alloc()`.

Register access is centralized in `cpc_read()`, `cpc_write()`, `cppc_get_reg_val()`, and `cppc_set_reg_val()`, with PCC-specific wrappers that ring the doorbell. Architecture hooks `cpc_ffh_supported()`, `cpc_supported_by_cpu()`, `cpc_read_ffh()`, and `cpc_write_ffh()` are weak defaults for arch overrides.

Exported performance APIs include `cppc_get_desired_perf()`, `cppc_get_nominal_perf()`, `cppc_get_highest_perf()`, `cppc_get_epp_perf()`, `cppc_get_perf_caps()`, `cppc_get_perf_ctrs()`, `cppc_set_epp_perf()`, `cppc_set_epp()`, `cppc_get_auto_act_window()`, `cppc_set_auto_act_window()`, `cppc_get_auto_sel()`, `cppc_set_auto_sel()`, `cppc_set_enable()`, `cppc_get_perf()`, `cppc_set_perf()`, `cppc_get_perf_limited()`, `cppc_set_perf_limited()`, `cppc_get_transition_latency()`, `cppc_get_dmi_max_khz()`, `cppc_perf_to_khz()`, and `cppc_khz_to_perf()`.

## Control Flow
`acpi_cppc_processor_probe()` first requires CPPC v2 `_OSC` acknowledgement unless the CPU architecture reports native CPPC support. It evaluates `_CPC`, validates revision and entry count, allocates a descriptor, parses integer and register-buffer entries, validates address spaces, maps SystemMemory registers, records a single PCC subspace ID, marks unsupported future entries, parses `_PSD`, registers a PCC channel once per subspace, stores the per-CPU descriptor, and creates an `acpi_cppc` kobject under the CPU device.

Reads of PCC-backed register sets take the PCC write lock, send a read command to refresh shared memory, then read all registers. Writes to individual PCC-backed registers write shared memory and send a write command. `cppc_set_perf()` has a special two-phase algorithm: multiple CPUs take the PCC read lock to update their desired/min/max registers in parallel, mark a pending write, and then one CPU obtains the write lock and sends the batched PCC write command; others wait for `pcc_write_cnt` to advance.

SystemMemory writes use the per-descriptor raw spinlock for read-modify-write masking. SystemIO uses ACPICA port helpers. FFH delegates to arch hooks. Unknown address spaces fall back to ACPICA memory access when appropriate.

## State And Persistence
CPPC state is entirely in memory and per CPU or per PCC subspace. PCC subspace objects are reference counted across CPUs and freed when the last CPU exits. SystemMemory register mappings are ioremapped during probe and unmapped at exit. Per-CPU sysfs kobjects live under CPU devices while the descriptor is active. Static `max_khz` caches the DMI fallback frequency for perf/frequency conversion.

## Dependencies And Integration Points
Depends on ACPI processor objects, `_OSC` capability flags from `bus.c`, ACPICA package extraction, PCC mailbox channels, CPU topology/cpumasks, per-CPU storage, sysfs kobjects, DMI, IO port and MMIO helpers, weak arch FFH hooks, and cpufreq shared-policy semantics. It is consumed by CPPC cpufreq drivers and other CPU performance management code.

## Risks
Firmware parsing is strict and can reject malformed `_CPC`/`_PSD` packages. PCC ownership, MPAR/MRTT timing, and batched write concurrency are high-risk areas: missed wakeups or incorrect lock transitions can lose performance requests. Flexible address-space support is gated by `_OSC`; accepting SystemMemory/SystemIO without it can violate older ACPI contracts unless CPU native support is present. Register bit-width and offset masking must avoid corrupting adjacent fields. The DMI frequency fallback is intentionally crude and should only be used when firmware lacks frequency registers.

## Test Signals
Signals include successful per-CPU `acpi_cppc` sysfs directories, valid `cppc_get_perf_caps()` values, cpufreq policy creation, correct `_PSD` shared CPU masks, PCC command completion without timeout/error bits, fast-switch allowance only for SystemMemory/SystemIO desired registers, EPP/autonomous selection writes, performance-limited sticky-bit clearing, and CPU hotplug cleanup. Stress tests should target concurrent `cppc_set_perf()` on shared PCC subspaces, malformed firmware packages, unsupported address spaces, and MPAR/MRTT limit handling.
