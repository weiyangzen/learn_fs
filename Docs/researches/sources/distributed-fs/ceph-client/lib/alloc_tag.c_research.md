<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/alloc_tag.c -->
# sources/distributed-fs/ceph-client/lib/alloc_tag.c

## Purpose
Implements memory allocation profiling support based on code tags. It exposes allocation-site accounting through `/proc/allocinfo`, manages page allocation tag references, handles module allocation tag sections, and controls boot/sysctl toggles for memory profiling.

## APIs, Types, and Functions
Important exports and globals include `mem_alloc_profiling_key`, `mem_profiling_compressed`, `kernel_tags`, `alloc_tag_ref_mask`, `alloc_tag_ref_offs`, `alloc_tag_top_users()`, `pgalloc_tag_split()`, `pgalloc_tag_swap()`, and `page_alloc_tagging_ops`. Major internal functions are seq-file callbacks for `/proc/allocinfo`, `shutdown_mem_profiling()`, `alloc_tag_sec_init()`, module tag area helpers under `CONFIG_MODULES`, early parameter parsing in `setup_early_mem_profiling()`, optional debug early-PFN tracking, sysctl registration, and `alloc_tag_init()`.

## Control Flow, State, and Persistence
Boot state starts from config defaults and the early parameter `sysctl.vm.mem_profiling`. `alloc_tag_sec_init()` initializes compressed tag indexing by locating allocation-tag sections and mapping them into spare page-flag bits; otherwise page extension storage is requested through `page_alloc_tagging_ops`. `alloc_tag_init()` creates `/proc/allocinfo`, reserves module tag virtual memory, and registers the codetag type. For modules, a maple tree tracks reserved tag ranges, grows the backing `execmem_vmap()` area, assigns percpu counters on module load, and marks ranges unloaded until counters reach zero. `/proc/allocinfo` iterates codetags under the codetag module-list lock and prints bytes/calls plus tag text. Persistent state is runtime-only: static keys, proc/sysctl visibility, codetag sections, percpu counters, module range map, and page tag references.

## Dependencies and Integration
Depends on `linux/alloc_tag.h`, codetag infrastructure, page extension and page-allocation tag helpers, procfs, sysctl, module loader callbacks, maple tree, KASAN vmalloc shadow setup, kmemleak, kallsyms, static keys, and RCU. It is built by `lib/Makefile` under `CONFIG_MEM_ALLOC_PROFILING`.

## Risks and Test Signals
Risks are high because this code touches allocation and module unload paths. Important risks include static-key state diverging from `mem_profiling_support`, compressed tag count exceeding spare page-flag capacity, module tag virtual space exhaustion, leaked percpu counters for unloaded modules with live allocations, races while clearing early PFN tag refs in debug mode, and proc/sysctl toggles after shutdown. This snapshot also shows suspicious duplicated source lines around `kallsyms_lookup_name()` and `if (!mod)`, which should be treated as source-integrity/build-risk signals. Test signals include boot with profiling disabled/enabled/compressed/never, `/proc/allocinfo` format version checks, sysctl write permissions, module load/unload with outstanding allocations, page split/swap tag propagation, KASAN/module shadow growth, page_ext initialization, and stress under allocation-heavy workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/alloc_tag.c -->
