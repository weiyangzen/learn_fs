# sources/distributed-fs/ceph-client/drivers/hv/mshv_root_hv_call.c

## Purpose

`mshv_root_hv_call.c` is the Hyper-V hypercall adapter for the root MSHV driver. It formats input/output pages, handles repeated hypercalls and memory-deposit retries, maps/unmaps GPA and state pages, manages ports, stats pages, and sparse SPA host access.

## Important APIs, Types, and Functions

- Partition lifecycle: `hv_call_create_partition`, `initialize`, `finalize`, `delete`, `withdraw_memory`.
- GPA mapping: `hv_call_map_gpa_pages`, `hv_call_map_mmio_pages`, `hv_call_unmap_gpa_pages`, and access-state reads.
- VP state: `hv_call_get_vp_state`, `hv_call_set_vp_state`, `hv_map_vp_state_page`, `hv_unmap_vp_state_page`, and `hv_call_delete_vp`.
- Interrupts: `hv_call_assert_virtual_interrupt()` and `hv_call_clear_virtual_interrupt()`.
- Ports and doorbells: create/delete/connect/disconnect port and notify ring empty.
- Stats: `hv_map_stats_page()` and `hv_unmap_stats_page()` support old hypervisor-provided mappings and L1VH overlay-GPFN mappings.
- `hv_call_modify_spa_host_access()` acquires/releases sparse SPA host access for encrypted memory transitions.

## Control Flow

Most calls disable local interrupts while using current CPU hypercall pages, zero and fill the input structure, invoke a fast, normal, or repeated hypercall, restore interrupts, and translate Hyper-V status to errno. Calls that can return `HV_STATUS_INSUFFICIENT_MEMORY` or equivalent loop through `hv_deposit_memory()` or `hv_call_deposit_pages()` until success or deposit failure. Repeated mapping/unmapping walks batches sized by the hypercall page.

## State and Persistence Behavior

The file does not own high-level objects but mutates persistent Hyper-V partition state. GPA/state/stats mappings persist until corresponding unmap/finalize calls. Overlay-GPFN mode allocates Linux pages for VP state and stats mappings and frees them on unmap. Withdraw-memory returns deposited pages to the kernel.

## Dependencies and Integration Points

It depends on `asm/mshyperv.h`, `hvhdk.h` structures, global `mshv_root.vmm_caps`, and tracepoints. It is called throughout partition lifecycle, memory mapping, debugfs stats, SynIC doorbells, eventfd interrupts, and VP ioctls.

## Risks and Edge Cases

Large-page mapping requires 2 MiB aligned page counts and indexes into the original page array with shifted offsets. Error rollback after partial map uses `done`, which is counted in large-page units when large mappings are active and should be reviewed against `hv_call_unmap_gpa_pages()` expectations. Old stats-page mapping returns success with NULL for unsupported PARENT area; callers must handle NULL. Local IRQ masking assumes hypercalls are bounded. `hv_call_modify_spa_host_access()` returns early on index overflow before restoring IRQs if that path is hit inside the IRQ-disabled loop, which should be reviewed.

## Test Signals

Fault-inject Hyper-V statuses for memory-deposit loops, partial completions, GPA map rollback, MMIO RAM rejection, large-page alignment, VP state page overlay allocation/free, PARENT stats unsupported fallback, port create/connect cleanup, sparse SPA host access for encrypted partitions, and tracepoint emission for lifecycle calls.
