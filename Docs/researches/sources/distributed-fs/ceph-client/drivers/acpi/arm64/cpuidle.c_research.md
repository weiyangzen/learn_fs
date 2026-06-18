# sources/distributed-fs/ceph-client/drivers/acpi/arm64/cpuidle.c

## Purpose
Implements ARM64 ACPI FFH low-power idle support using PSCI CPU suspend.

## Important APIs, Types, And Functions
Exports `acpi_processor_ffh_lpi_probe()` and defines `acpi_processor_ffh_lpi_enter()`. Internal validation is in `psci_acpi_cpu_init_idle()`.

## Control Flow
Probe checks that the CPU has ACPI LPI data, PSCI `cpu_suspend` exists, and every non-index-zero LPI state's low 32-bit address encodes a valid PSCI power state. Enter reads the LPI address as PSCI state and invokes the CPU PM idle helper, choosing retention or full idle based on `arch_flags`.

## State And Persistence
No file-local state. It consumes per-CPU ACPI processor LPI state and PSCI operation pointers.

## Dependencies And Integration Points
Integrates ACPI processor idle, PSCI, CPU PM, and cpuidle.

## Risks
Firmware can provide invalid power states or unsupported FFH encodings. Incorrect retention classification can call the wrong CPU PM helper.

## Test Signals
Check CPUs without LPI, missing PSCI suspend, invalid PSCI state rejection, retention and non-retention entry paths, and suspend/resume behavior.
