<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/kcore.c -->
## sources/distributed-fs/ceph-client/fs/proc/kcore.c

Purpose: implements `/proc/kcore`, an ELF core-image view of kernel virtual memory for privileged readers. It builds program headers over RAM, vmalloc, vmemmap, kernel text, and module ranges, emits ELF notes including vmcoreinfo, and reads memory with architecture-safe access helpers.

Important APIs and functions: exports `register_mem_pfn_is_ram` and init-time `kclist_add`. Main internals include `update_kcore_size`, `kcore_ram_list`, `kcore_update_ram`, `append_kcore_note`, `read_kcore_iter`, `open_kcore`, `release_kcore`, `kcore_callback`, `proc_kcore_text_init`, `add_modules_range`, and `proc_kcore_init`. State is held in `kclist_head`, `kcore_nphdr`, `kcore_*_len`, `kcore_data_offset`, `kcore_need_update`, and `proc_root_kcore`.

Control flow: boot init creates `/proc/kcore`, records special text/vmalloc/module ranges, builds RAM ranges, and registers a memory-hotplug notifier. Open requires `CAP_SYS_RAWIO` and passes `security_locked_down(LOCKDOWN_KCORE)`, allocates a page bounce buffer, refreshes RAM ranges if hotplug marked them stale, and updates inode size. Reads first synthesize the ELF header, program headers, and note segment, then translate file offsets to kernel virtual addresses and copy page-sized chunks from the matching `kcore_list` entry.

State and persistence behavior: memory range metadata persists in a global list protected by `kclist_lock`, a percpu rwsem. Hotplug sets `kcore_need_update`, and the next open rebuilds RAM/VMEMMAP entries. The proc entry size mirrors generated ELF metadata plus the highest virtual offset. Each open file owns a temporary bounce page.

Dependencies and integration points: depends on ELF/core note definitions, vmcoreinfo, memory hotplug, memblock/system RAM walkers, vmalloc `vread_iter`, capability and lockdown LSM checks, page offline freeze/thaw, architecture hooks for physical-to-virtual translation and kernel text sections, and procfs read-iter support.

Risks: `/proc/kcore` is security-sensitive and must remain gated by capability and lockdown. Reads can touch volatile kernel memory, offline pages, hwpoisoned pages, unaccepted memory, vmalloc holes, and architecture-specific mappings; bad filtering can fault or disclose invalid data. Hotplug update and range list replacement must avoid readers seeing freed entries. ELF note sizing must guard against vmcoreinfo races.

Test signals: permission and lockdown denial; `readelf -h/-l /proc/kcore`; reads across ELF header, notes, RAM holes, vmalloc area, text/module ranges; memory online/offline while opening; hwpoison/offline page reads returning zeros; KASAN/lockdep around `kclist_lock` and page-offline freeze.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/kcore.c -->
