# sources/distributed-fs/ceph-client/kernel/crash_core.c

## Purpose
`crash_core.c` implements shared crash-kernel support for kdump/kexec: copying vmcoreinfo into crash memory, deciding when oops paths should crash-kexec, executing the crash kernel, generating ELF core headers and CPU notes, shrinking reserved crash memory, and optionally updating crash-kernel segments when CPU or memory hotplug events occur.

## Important APIs, types, and functions
Important globals include per-CPU `crash_notes`, `kexec_crash_image`, crash resource variables from reservation code, and crash hotplug locks/notifiers under `CONFIG_CRASH_HOTPLUG`. Public functions include `kimage_crash_copy_vmcoreinfo()`, `kexec_should_crash()`, `kexec_crash_loaded()`, `__crash_kexec()`, BPF kfunc `crash_kexec()`, `crash_prepare_elf64_headers()`, `crash_exclude_mem_range()`, `crash_get_memory_size()`, `crash_shrink_memory()`, `crash_save_cpu()`, and `crash_check_hotplug_support()`.

Internal helpers include `crash_cma_clear_pending_dma()`, `crash_resource_size()`, `__crash_shrink_memory()`, `crash_notes_memory_init()`, `crash_handle_hotplug_event()`, memory and CPU hotplug notifiers, and `crash_hotplug_init()`.

## Control flow
When a crash kimage is loaded, `kimage_crash_copy_vmcoreinfo()` allocates pages from crash memory, maps them with `vmap()`, stores `image->vmcoreinfo_data_copy`, and points the vmcoreinfo safe-copy machinery at that mapping. On panic or eligible oops, `crash_kexec()` uses `panic_try_start()` so only one CPU proceeds. `__crash_kexec()` takes the kexec lock, saves registers and vmcoreinfo, runs machine crash shutdown, waits for crashkernel CMA DMA quiescence if configured, and calls `machine_kexec()`.

`crash_prepare_elf64_headers()` allocates an ELF64 core header, emits one PT_NOTE for each possible CPU's `crash_notes`, one PT_NOTE for vmcoreinfo, optionally one PT_LOAD for the kernel text virtual mapping, and one PT_LOAD per crash memory range. `crash_exclude_mem_range()` mutates a sorted `struct crash_mem` range list to remove a closed interval, handling complete removal, left/right trimming, and splitting with `-ENOMEM` if no spare range slot exists.

`crash_shrink_memory()` rejects shrinking while a crash image is loaded, rounds the requested size, releases the tail of `crashk_res` or `crashk_low_res` back to system RAM, reinserts freed resources, and swaps high/low resource roles if needed. Crash hotplug notifiers locate the elfcorehdr segment, unprotect crash reserved memory, set `image->hp_action`, call arch update code, mark the elfcorehdr updated, and re-protect the region.

## State and persistence behavior
Persistent kernel state includes allocated per-CPU `crash_notes`, the protected crash kimage, vmcoreinfo safe copy, crash reserved resources, image hotplug metadata, and ELF header buffers passed to kexec. `crash_shrink_memory()` changes the kernel resource tree and frees reserved physical ranges back to normal RAM. Crash hotplug updates modify the loaded crash image in reserved memory, but there is no filesystem persistence.

## Dependencies and integration points
The file integrates with kexec image locking and segment management, architecture crash shutdown/kexec/protect/unprotect hooks, vmcoreinfo, panic ownership, BPF kfunc exposure, ELF core definitions, per-CPU allocation, memblock/resources, RCU crash callback migration indirectly through CPU hotplug, memory hotplug notifier chains, cpuhp dynamic states, CMA crashkernel ranges, and kdump tooling expectations for ELF core headers.

## Risks and edge cases
`__crash_kexec()` runs in panic context and must tolerate broken system state. Lock acquisition can fail if another kexec operation owns the lock. `crash_exclude_mem_range()` assumes sorted non-overlapping ranges and requires spare capacity before split operations. Shrinking crash memory while image state or resource tree state is inconsistent could expose reserved memory incorrectly. Crash hotplug intentionally does not roll back CPU/memory hotplug on update failure, so a stale elfcorehdr can be left behind with only diagnostics. CMA reservations force a fixed 10-second delay before entering the crash kernel.

## Test signals
Existing direct test coverage comes from `crash_core_test.c` for `crash_exclude_mem_range()`. Additional signals include kdump boot with and without vmcoreinfo safe copy, ELF header validation with per-CPU notes and memory ranges, panic/oops paths with `crash_kexec_post_notifiers` and `panic_on_oops`, crash memory shrink via sysfs/control callers, memory and CPU hotplug while a hotplug-capable crash image is loaded, CMA crashkernel reservations, and architecture protect/unprotect verification.
