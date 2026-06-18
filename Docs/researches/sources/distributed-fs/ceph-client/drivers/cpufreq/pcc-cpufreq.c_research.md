# sources/distributed-fs/ceph-client/drivers/cpufreq/pcc-cpufreq.c

## Purpose

`pcc-cpufreq.c` implements the ACPI Processor Clocking Control interface. It communicates with firmware through a shared PCCH memory region and a doorbell register, exposing firmware-defined percentage-of-nominal frequency control as a cpufreq driver.

## Important APIs, types, and functions

- `struct pcc_header` maps the shared PCCH header containing command/status, latency, nominal, throttled, and minimum frequencies.
- `struct pcc_register_resource` and `struct pcc_memory_resource` parse ACPI resource buffers from the `PCCH` package.
- `struct pcc_cpu` stores per-CPU input and output offsets obtained from each processor's `PCCP` object.
- `pcc_cpufreq_evaluate()` finds `\_SB.PCCH`, optionally negotiates `_OSC`, maps the shared memory, parses doorbell preserve/write masks, allocates per-CPU data, and logs limits.
- `pcc_get_offset()` evaluates `PCCP` for a CPU and clears its buffers.
- `pcc_cmd()` rings the ACPI doorbell and polls `pcch_hdr->status` for `CMD_COMPLETE`.
- `pcc_get_freq()` issues `CMD_GET_FREQ`; `pcc_cpufreq_target()` issues `CMD_SET_FREQ`.

## Control flow

`late_initcall(pcc_cpufreq_init)` uses `platform_driver_probe()` so probe runs once. Probe refuses to initialize if another cpufreq driver is active or ACPI is disabled. It evaluates PCCH, disables dynamic switching on systems with more than four CPUs, and registers cpufreq. CPU init evaluates `PCCP` offsets and sets policy min/max from PCCH minimum/nominal frequencies. Target changes translate target kHz to a percentage of nominal, write the CPU input buffer, set command, ring the doorbell, clear the input buffer, and end the cpufreq transition based on completion status.

## State and persistence behavior

Global state includes the PCCH mapping, header pointer, doorbell GAS, preserve/write masks, spinlock, and per-CPU offset storage. All firmware commands are serialized by `pcc_lock`. Mapped shared memory persists until platform remove, which unregisters cpufreq, unmaps PCCH, and frees per-CPU data. Firmware owns the actual processor clock state.

## Dependencies

The driver depends on ACPI `PCCH`, processor `PCCP`, optional `_OSC` negotiation, ACPI generic address read/write helpers, shared memory resources, cpufreq core, and per-CPU ACPI processor objects. It also depends on firmware respecting the command/status protocol and percentage encodings.

## Risks and edge cases

- `pcc_cmd()` busy-polls without delay or timeout error reporting beyond status not complete after 300 loops.
- Shared memory resource lengths and offset bounds are trusted after basic type checks; malformed firmware could point offsets outside the mapping.
- More than four CPUs causes `CPUFREQ_NO_AUTO_DYNAMIC_SWITCHING`, reflecting protocol scalability concerns.
- `pcc_cpufreq_target()` uses the target frequency directly rather than selecting a validated table, so firmware percentage rounding determines the actual result.
- ACPI `_OSC` failure is nonfatal by design, so systems with ambiguous control ownership may still proceed.

## Test signals

Validation should include ACPI table parsing, successful PCCH mapping, correct per-CPU PCCP offsets, get/set command completion, min/max policy bounds matching firmware, dynamic switching disabled on large systems, and cleanup on remove. Firmware error injection should verify incomplete commands return safe failures and clear status/input buffers.
