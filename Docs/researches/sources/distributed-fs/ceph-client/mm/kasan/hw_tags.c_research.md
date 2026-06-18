## sources/distributed-fs/ceph-client/mm/kasan/hw_tags.c

Purpose: implements hardware tag-based KASAN boot parameters, mode selection, CPU tag-check enablement, vmalloc tagging, and KUnit-only helpers.

Important APIs and state: defines early parameters `kasan=`, `kasan.mode=`, `kasan.vmalloc=`, `kasan.write_only=`, `kasan.page_alloc.sample=`, and `kasan.page_alloc.sample.order=`. Exports `kasan_mode`, `kasan_flag_vmalloc`, page allocation sampling globals, and `kasan_init_hw_tags_cpu()`, `kasan_init_hw_tags()`, `__kasan_unpoison_vmalloc()`, `__kasan_poison_vmalloc()`, and `kasan_enable_hw_tags()`.

Control flow: boot parsing records requested state. Per-CPU init skips disabled KASAN and enables hardware tag checks. Boot CPU init verifies MTE support, applies sync/async/asymmetric mode selection, toggles vmalloc tagging static key, initializes tag infrastructure, enables KASAN, and prints the active mode. Vmalloc unpoisoning tags only suitable `VM_ALLOC` normal-protection mappings, assigns or preserves a tag, unpoisons requested bytes, poisons the in-page redzone, and stores page tags for `page_address(vmalloc_to_page())` access.

State and persistence: persistent runtime state is static-key controlled enablement, selected mode, write-only flag, vmalloc tag state, page allocation sampling counters, and per-page tags for vmalloc backing pages.

Dependencies and integration: integrates with arm64 MTE-style arch hooks, static keys, early param parsing, vmalloc metadata, page tag APIs, and KUnit visibility exports.

Risks and test signals: risks include enabling unsupported MTE or write-only modes, tagging executable/non-VM_ALLOC mappings, stale tag checks after synchronous faults, and sampling reducing coverage. Tests should cover boot parameter matrix, CPU hotplug, vmalloc tagging on/off, async fault forcing, write-only behavior, and KUnit tag range tests.
