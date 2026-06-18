# sources/distributed-fs/ceph-client/include/linux/arm_mpam.h

## Purpose
Declares Arm MPAM integration with Linux resctrl, ACPI MPAM parsing, MSC resource creation, requestor registration, and architecture hooks for closid/rmid scheduling and monitoring.

## Important APIs, Types, And Functions
`enum mpam_msc_iface` distinguishes MMIO and PCC MSC interfaces. `enum mpam_class_types` describes cache, memory, or unknown classes, with `MPAM_CLASS_ID_DEFAULT`. ACPI helpers `acpi_mpam_parse_resources()` and `acpi_mpam_count_msc()` are gated by `CONFIG_ACPI_MPAM`; `mpam_ris_create()` is gated by `CONFIG_ARM64_MPAM_DRIVER`. Resctrl architecture APIs include allocation/monitoring capability checks, CPU/task closid/rmid setters, scheduler hook `resctrl_arch_sched_in()`, match helpers, RMID index encode/decode, monitor context allocation/free, and no-op enable/disable helpers. `mpam_register_requestor()` lets requestors advertise PARTID/PMG limits.

## Control Flow, State, And Persistence
MPAM driver setup parses ACPI resources, creates RIS instances for MSCs, and registers requestor limits before user-visible resctrl sizes are finalized. Runtime scheduling writes CPU/requestor MPAM state when closid/rmid changes. Persistent state lives in MPAM MSC/resource objects and resctrl task/CPU assignments.

## Dependencies And Integration Points
Depends on ACPI MPAM structures, `linux/resctrl_types.h`, task structs, and resctrl resources/events. Integrates Arm64 MPAM driver, ACPI, resctrl filesystem, scheduler context switches, monitoring, and allocation control.

## Risks And Test Signals
Late requestor registration can conflict with values already advertised to userspace. Wrong RMID encoding or scheduling hooks can attribute monitoring data to the wrong control group. Tests should cover ACPI parsing failures, no-driver stubs returning `-EINVAL`, closid/rmid context switch behavior, resctrl alloc/mon capabilities, monitor context lifecycle, and requestor registration before/after exposure.
