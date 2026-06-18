<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/hv_common.c -->
# sources/distributed-fs/ceph-client/drivers/hv/hv_common.c

## Purpose

`hv_common.c` contains architecture-neutral Hyper-V support that must be built in when `CONFIG_HYPERV` is enabled. It defines shared Hyper-V globals, allocates per-CPU hypercall argument pages, records VP indexes, reports panic data to Hyper-V, seeds randomness from a Microsoft ACPI table, queries extended capabilities, exposes weak architecture hooks, identifies partition type, and maps Hyper-V status codes to Linux errors and strings.

## Important APIs, Types, and Functions

- Exported globals include `hv_current_partition_id`, `hv_curr_partition_type`, `hv_nested`, `ms_hyperv`, `hv_vp_index`, `hv_max_vp_index`, `hyperv_pcpu_input_arg`, `hyperv_pcpu_output_arg`, and `hv_synic_eventring_tail`.
- `hv_common_init()` initializes panic reporting, sysctl state, per-CPU hypercall pointers, root output pages, event-ring tails, and VP-index storage.
- `hv_common_free()` tears down sysctl, panic dump hooks, VP indexes, and per-CPU pointer arrays.
- `hv_common_cpu_init()` allocates per-CPU hypercall input/output pages, decrypts them for isolated guests when required, records `HV_MSR_VP_INDEX`, and allocates root SynIC event-ring tails.
- `hv_common_cpu_die()` frees root event-ring tail storage.
- `hv_kmsg_dump()` and `hv_die_panic_notify_crash()` report panic/oops information through Hyper-V crash MSRs.
- `hv_get_partition_id()`, `get_vtl()`, `hv_query_ext_cap()`, `hv_identify_partition_type()`, `hv_result_to_errno()`, and `hv_result_to_string()` are exported utility functions.

## Control Flow

`hv_common_init()` obtains hypervisor version information, disables panic-message recording by default for isolated guests, and if crash MSRs are available registers a sysctl plus panic/die/kmsg dump notifiers. It then allocates per-CPU holders for input and optional output hypercall pages and initializes `hv_vp_index[]` to invalid. Per-CPU bring-up calls `hv_common_cpu_init()`, which lazily allocates the real hypercall pages, handles memory decryption before publishing `hyperv_pcpu_input_arg`, reads the VP index MSR, updates the maximum VP index, and prepares root event-ring state.

Panic reporting either sends register-only crash notification or, when enabled and supported, writes kmsg tail data into `hv_panic_page`, programs crash MSRs P0-P4, and sets crash control notify bits. `hv_query_ext_cap()` performs a one-time extended capability hypercall and caches the result. Partition type is inferred from privilege bits while explicitly ignoring root privileges when isolation is present.

## State and Persistence Behavior

Most state is global and persists for the kernel lifetime or Hyper-V platform lifetime. Per-CPU hypercall pages are intentionally retained across CPU offline because later interrupt reassignment may still need them. `hv_extended_cap` is static and cached after first query. Panic-page allocation persists while crash reporting is registered. Weak hook definitions provide default no-op behavior until architecture-specific code overrides them at link time.

## Dependencies and Integration Points

This file is used by architecture initialization, VMBus core, MSHV root/VTL code, Hyper-V timer code, balloon page reporting, DMA setup, and crash/kexec paths. It depends on Hyper-V Hvhdk definitions, ACPI, sysctl, panic notifier, kmsg dumper, DMA-map ops, and architecture hypercall/MSR helpers.

## Risks and Edge Cases

`BUG_ON()` is used for fatal allocation failures in Hyper-V boot-critical paths. If `set_memory_decrypted()` fails in CPU init, memory may be unsafe to free and is intentionally left allocated. Panic reporting is deliberately limited in isolated guests. `hv_status_infos[]` contains duplicate status entries with different errno values for a couple of codes; first match wins. Status-to-errno mapping is necessarily lossy, so call sites still need context-specific handling.

## Test Signals

Verify boot on guest, root, L1VH, nested, SNP, TDX, and VTL configurations; CPU hotplug with retained hypercall pages; panic/oops reporting with sysctl enabled and disabled; ACPI OEM0 entropy seeding and table zeroing; extended capability caching; partition-type identification; and status-to-errno/string mappings for known and unknown hypercall statuses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/hv_common.c -->
