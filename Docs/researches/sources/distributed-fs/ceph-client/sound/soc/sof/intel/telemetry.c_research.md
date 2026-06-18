<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/telemetry.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/intel/telemetry.c

## Purpose
IPC4 Intel telemetry dump helper that reads a firmware telemetry debug slot, validates Xtensa core dump metadata, and forwards register/stack information into the existing SOF oops and stack dump paths.

## Important APIs, Types, and Functions
Exports `sof_ipc4_intel_dump_telemetry_state(struct snd_sof_dev *sdev, u32 flags)`. It uses `sof_ipc4_find_debug_slot_offset_by_type()`, `sof_mailbox_read()`, `struct sof_ipc4_telemetry_slot_data`, `struct xtensa_arch_block`, `struct sof_ipc_dsp_oops_xtensa`, `sof_oops()`, and `sof_stack()`.

## Control Flow, State, and Persistence
The function chooses log level from `SOF_DBG_DUMP_OPTIONAL`, locates the telemetry slot, reads the slot header, validates separator, reads the architecture block, checks SOC and coredump IDs, logs toolchain type, allocates an Xtensa oops object with AR register storage, copies exception PC/cause/address/status/SAR and all AR registers, then emits oops and stack dumps. Allocations are temporary and freed on all visible paths.

## Dependencies and Integration
Depends on IPC4 debug slot metadata, Xtensa register constants, SOF mailbox IO, and generic SOF crash dump helpers. Exported in the HDA common namespace for Intel IPC4 HDA dump paths to call when firmware exposes telemetry data.

## Risks and Test Signals
Risks include trusting telemetry struct layout to match firmware, rejecting useful dumps on header ID mismatch, allocation failures silently dropping optional dump data, and reading stale mailbox slots after severe firmware crashes. Test signals are induced firmware exceptions with valid telemetry separator/SOC/header IDs, Zephyr and XCC toolchain cases, optional versus error-level dump flags, and malformed slot validation paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/telemetry.c -->
