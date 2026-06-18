<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/powernow-k8.h -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/powernow-k8.h

## Purpose

Defines the state structure, MSR constants, FID/VID limits, ACPI control-field masks, and BIOS PSB/PST table layouts used by `powernow-k8.c`.

## APIs, Types, And Functions

`struct powernow_k8_data` stores CPU id, number of P-states, transition timing fields, current FID/VID, cpufreq table pointer, ACPI performance data, and associated core mask. `struct psb_s` and `struct pst_s` describe BIOS PowerNow table records. Constants cover `MSR_FIDVID_CTL`, `MSR_FIDVID_STATUS`, pending/status bits, low/high FID table rules, valid frequency/VID ranges, and `_PSS` control extraction masks. The header also forward-declares transition helpers shared within the C file.

## Control Flow

The header itself has no runtime flow. It constrains the K8 driver's ACPI and PSB parsing and the sequence of MSR writes during transitions.

## State And Persistence

No standalone persistent state exists in the header. It documents software state in `powernow_k8_data` and hardware-persistent FID/VID MSR fields.

## Dependencies And Integration Points

Integrated with ACPI processor performance structures, cpufreq tables, cpumasks, and x86 MSR operations. The PSB signature and version constants define compatibility with BIOS-provided tables.

## Risks And Test Signals

Incorrect masks or FID/VID bounds could make table validation unsound and allow unsafe MSR writes. Test evidence is indirect: K8 ACPI/PSB table loading must reject invalid VID/FID values, extended `_PSS` decoding must pick the expected fields, and transitions must leave `currfid/currvid` matching requested values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/powernow-k8.h -->
