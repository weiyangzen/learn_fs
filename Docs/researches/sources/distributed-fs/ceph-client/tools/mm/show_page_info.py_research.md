# sources/distributed-fs/ceph-client/tools/mm/show_page_info.py

Purpose: A drgn-based diagnostic script that prints detailed kernel `struct page` state for a process virtual address.

Important APIs and functions: `format_page_data` emits a raw word dump of the `struct page`; `get_memcg_info` decodes `page.memcg_data` into cgroup name/path; `show_page_state` prints flags, PFN, physical/virtual addresses, refcount, mapcount, folio index, mapping, VMA, slab/compound status; `main` parses `pid` and hex `vaddr`, finds the task, and calls `follow_page`.

Control flow: The script validates the virtual address, resolves `task.mm`, obtains the page for the virtual address, and prints structured fields with guarded exception handling around fragile kernel memory reads.

State and persistence behavior: Read-only against a live kernel or crash dump through drgn. No files are written.

Dependencies and integration points: Requires drgn runtime globals such as `prog`, drgn Linux helpers for tasks, mm, cgroups, and page flags, plus kernel layout constants like `MEMCG_DATA_OBJEXTS`.

Risks: Kernel field names are version-sensitive (`__folio_index`, `memcg_data`, counters). Access can fault for invalid tasks, unmapped addresses, or unavailable debug info. The reported anon/file classification checks low bit of `mapping`, which depends on kernel encoding.

Test signals: Run against known anonymous, file-backed, slab, compound head/tail, unmapped, and invalid PID/address cases on kernels with matching debug info.
