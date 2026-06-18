# sources/distributed-fs/ceph-client/arch/x86/kernel/acpi/cstate.c

## Purpose
`cstate.c` implements x86-specific ACPI processor C-state support, especially FFH C-state entry through the `MONITOR/MWAIT` instruction pair. It also sets bus-mastering flags that tell the generic ACPI processor idle code whether C3 entry needs cache flushing or ARB_DISABLE handling on different CPU vendors.

## Important APIs, Types, and Functions
- `acpi_processor_power_init_bm_check()` initializes `struct acpi_processor_flags` fields `bm_check` and `bm_control` based on online CPU count, vendor, family/model, and Zen feature state.
- `struct cstate_entry` stores per-CPU MWAIT `eax` and `ecx` hints for ACPI C-state indices.
- `cpu_cstate_entry` is a per-CPU allocation used by C-state probe, idle entry, and offline play-dead.
- `acpi_processor_ffh_cstate_probe()` validates FFH register data, runs the CPU-local CPUID MWAIT probe, stores hints, and marks Intel BM_STS skip behavior.
- `acpi_processor_ffh_cstate_enter()` calls `mwait_idle_with_hints()`.
- `acpi_processor_ffh_play_dead()` calls `mwait_play_dead()` for CPU offline.
- `ffh_cstate_init()` allocates per-CPU storage for Intel, AMD, and Hygon systems at `arch_initcall`.

## Control Flow
The generic ACPI processor driver asks x86 to initialize bus-master behavior after CPUs are online. For FFH C-states, `acpi_processor_ffh_cstate_probe()` rejects unsupported conditions, clears the per-CPU state entry, and uses `call_on_cpu()` so CPUID leaf 5 is evaluated on the target CPU. The CPU-local probe verifies that the ACPI C-state MWAIT hint has a hardware-supported substate and that interrupt-break extensions are present. A successful probe stores the MWAIT hint and interrupt-break ECX flag for later idle entry.

Idle entry is direct: the cpuidle path calls `acpi_processor_ffh_cstate_enter()`, which fetches the current CPU's stored hints and executes the MWAIT idle helper. CPU offline death uses the same stored EAX hint through `acpi_processor_ffh_play_dead()`.

## State and Persistence Behavior
The per-CPU `cpu_cstate_entry` array persists for the lifetime of the module/built-in code and is freed only by the exit callback. `mwait_supported[]` suppresses repeated debug logging per C-state type. The function mutates ACPI processor C-state descriptors (`cx->desc`, `cx->bm_sts_skip`) and stores per-CPU idle hints derived from firmware `_CST` data.

## Dependencies and Integration Points
The file integrates ACPI processor idle data, `struct acpi_processor_cx`, CPUID leaf `CPUID_LEAF_MWAIT`, `asm/mwait.h`, SMP CPU-local execution helpers, CPU vendor/family identification, cpuidle annotations, and CPU hotplug play-dead support.

## Risks
- Incorrect BM flag decisions can cause unnecessary `WBINVD`, skipped cache-coherency handling, or wrong ARB_DISABLE behavior on C3 entry.
- Firmware can advertise unsupported MWAIT hints; the probe rejects many cases but relies on CPUID decoding and `_CST` address semantics.
- Per-CPU state must be initialized before idle entry or play-dead; missing allocation causes probe failure.
- C-state entry is CPU-local and low-level; incorrect hints can hang or wake CPUs incorrectly.

## Test Signals
- Boot with ACPI processor idle enabled and check logs for `Monitor-Mwait will be used` messages.
- Validate cpuidle state entry/exit and CPU offline on Intel and AMD/Hygon systems.
- Exercise vendor-specific BM behavior on Intel, Centaur, Zhaoxin, and Zen systems.
- Use firmware with invalid FFH/MWAIT C-state data to verify graceful rejection.
