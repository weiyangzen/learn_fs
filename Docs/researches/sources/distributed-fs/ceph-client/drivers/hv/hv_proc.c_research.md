<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/hv_proc.c -->
# sources/distributed-fs/ceph-client/drivers/hv/hv_proc.c

## Purpose

`hv_proc.c` provides Hyper-V root-partition processor and memory-deposit hypercall helpers. It allocates pages for child/root partition deposits, retries processor creation when Hyper-V reports insufficient memory, adds logical processors, creates VPs, notifies that processors have started, and probes whether an LP index exists.

## Important APIs, Types, and Functions

- `hv_call_deposit_pages()` allocates exactly the requested number of pages, fills a `hv_deposit_memory` input page, and performs `HVCALL_DEPOSIT_MEMORY`.
- `hv_deposit_memory_node()` chooses deposit count and partition target based on insufficient-memory status codes.
- `hv_result_needs_memory()` identifies hypercall statuses that require a memory deposit and retry.
- `hv_call_add_logical_proc()` wraps `HVCALL_ADD_LOGICAL_PROCESSOR` with memory-deposit retry.
- `hv_call_create_vp()` wraps `HVCALL_CREATE_VP`, including an empirical pre-deposit for non-current partitions and retry on memory pressure.
- `hv_call_notify_all_processors_started()` sends `HVCALL_NOTIFY_PARTITION_EVENT`.
- `hv_lp_exists()` probes `HVCALL_GET_LOGICAL_PROCESSOR_RUN_TIME` and treats `HV_STATUS_INVALID_LP_INDEX` as nonexistence.

## Control Flow

Deposit flow allocates a temporary page to hold page pointers, separately allocates a counts array, then allocates all deposit pages in the largest orders possible before disabling interrupts. With interrupts disabled it uses the per-CPU Hyper-V input page, populates partition ID and GPA page list, issues a rep hypercall, and either transfers ownership to Hyper-V or frees all pages on failure. Processor add/create functions build input structures on the per-CPU hypercall page, call Hyper-V, and if the status indicates insufficient memory call `hv_deposit_memory_node()` before retrying.

## State and Persistence Behavior

Successful deposits transfer page ownership to Hyper-V and the pages are not freed by Linux. Failed deposits free each split page. The helper itself keeps no persistent state, but it relies on globally initialized per-CPU input/output pages from `hv_common.c`, `hv_current_partition_id`, and root-partition capability state. `hv_call_create_vp()` may deposit pages into child partitions before creating a VP.

## Dependencies and Integration Points

The file depends on Hyper-V Hvhdk structures, `hyperv_pcpu_input_arg`, `hyperv_pcpu_output_arg`, `hv_result_to_errno()`, `hv_status_err()`, NUMA-to-PXM helpers, and root partition code that creates logical processors or VPs. It is exported for GPL consumers.

## Risks and Edge Cases

`hv_call_deposit_pages()` requires interrupts enabled before entry because it disables interrupts around per-CPU hypercall page use after doing all allocations. `HV_DEPOSIT_MAX` bounds the page list to one Hyper-V page. High-order allocation fallback splits pages and must free every split page on failure. The empirical 90-page pre-deposit for child VP creation is host behavior dependent. Unexpected root-memory statuses in non-root partitions are rejected.

## Test Signals

Test exact deposit counts including zero and over-limit, allocation fallback and cleanup, insufficient-memory retry loops for LP and VP creation, root versus child partition deposit targets, notify-all-processors-started errors, and `hv_lp_exists()` for valid, invalid, and unexpected status codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/hv_proc.c -->
