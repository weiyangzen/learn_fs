# sources/distributed-fs/ceph-client/tools/mm/page_owner_sort.c

Purpose: Sorts and culls `/sys/kernel/debug/page_owner` dumps so repeated allocation records can be grouped and ordered by count, memory, process, command, stack, allocator, or timestamp.

Important APIs and types: `struct block_list` stores one parsed page-owner block plus parsed pid/tgid/comm/order/timestamp/allocator. `struct filter_condition` and `struct sort_condition` hold CLI state. Key functions are `read_block`, regex helpers, `get_page_num`, `get_pid`, `get_tgid`, `get_comm`, `get_allocator`, `parse_cull_args`, `parse_sort_args`, `add_list`, and comparator functions.

Control flow: `main` parses short and long options, configures default or custom sort, opens input/output, compiles regexes for page-owner fields, estimates capacity from input size, reads blocks separated by blank lines while carrying `PFN` metadata in `ext_buf`, filters records, sorts by cull key, coalesces adjacent equivalent records, sorts by requested output order, and writes either full records or culled summaries.

State and persistence behavior: All parsed records are held in memory. Output is a new sorted text file. The input page-owner dump is read-only.

Dependencies and integration points: Consumes the exact text format produced by kernel page_owner debugfs and references Documentation/mm/page_owner.rst conventions.

Risks: Capacity is estimated as `st_size / 100`, which can underallocate for small or unusual records. Regex assumptions can fail on format changes. `get_allocator` walks backward from `__vmalloc_node_range` and can be fragile. Some allocations are not freed individually before exit.

Test signals: Use fixture dumps with repeated stacks, different PIDs/TGIDs/comms, CMA/slab/vmalloc markers, custom `--cull` and `--sort`, malformed fields with `-d`, and large inputs.
