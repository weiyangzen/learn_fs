# sources/distributed-fs/ceph-client/drivers/hv/mshv_common.c

## Purpose

`mshv_common.c` implements common Hyper-V helper calls shared across MSHV modules, plus x86 power-off integration. It wraps VP register and partition-property hypercalls behind safer batching and per-CPU page handling.

## Important APIs, Types, and Functions

- `hv_call_get_vp_registers()` fills caller-provided `struct hv_register_assoc` values by issuing repeated `HVCALL_GET_VP_REGISTERS` batches.
- `hv_call_set_vp_registers()` copies register associations into the per-CPU input page and issues repeated `HVCALL_SET_VP_REGISTERS` batches.
- `hv_call_get_partition_property()` issues `HVCALL_GET_PARTITION_PROPERTY` and returns the scalar property value.
- On x86, `hv_sleep_notifiers_register()` registers a reboot notifier that initializes S5 sleep-state system properties, and `hv_machine_power_off()` enters S5 through `HVCALL_ENTER_SLEEP_STATE`.

## Control Flow

The get/set register wrappers disable local interrupts, take the current CPU's Hyper-V input/output pages, initialize common fields once, and loop until all requested registers have been processed or a hypercall fails. Batch size is derived from `HV_HYP_PAGE_SIZE`. Partition-property reads similarly use current CPU pages, zero input, issue one hypercall, copy output on success, and return an errno-mapped Hyper-V status.

For power off, the reboot notifier validates ACPI S5 support, reads PM sleep type data, writes `HV_SYSTEM_PROPERTY_SLEEP_STATE`, and later `hv_machine_power_off()` asks Hyper-V to enter S5.

## State and Persistence Behavior

Register calls do not persist kernel state beyond modifying caller arrays; persistent effects occur inside Hyper-V. The sleep-state notifier persists registration in the reboot notifier chain. Local IRQ masking protects per-CPU hypercall pages from same-CPU reentrancy while formatting inputs.

## Dependencies and Integration Points

The file depends on `asm/mshyperv.h`, ACPI, reboot notifiers, exports, and `mshv.h`. Its exported wrappers are used by root partition management, SynIC setup, VTL paths, and any module that needs VP registers or partition properties.

## Risks and Edge Cases

The loops rely on `hv_repcomp(status)` making progress after successful rep hypercalls. If Hyper-V returns success with zero completions, callers could spin. Sleep-state initialization is x86-only and depends on ACPI S5 being available. Local IRQ disabling means wrappers should avoid long or blocking work while using per-CPU pages.

## Test Signals

Tests should cover single and multi-batch register operations, partial completion on failures, property read success/failure, IRQ-context safety assumptions, reboot notifier registration failure logging, ACPI S5 unsupported paths, and power-off hypercall invocation on x86 builds.
