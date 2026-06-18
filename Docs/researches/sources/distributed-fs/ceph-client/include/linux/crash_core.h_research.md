<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crash_core.h -->
# sources/distributed-fs/ceph-client/include/linux/crash_core.h

## Purpose

`crash_core.h` declares core crash-kexec and crash-dump helpers, crash memory range representation, crash hotplug event constants, and optional crash dm-crypt key export support. The source was read as a complete 99-line file.

## Important APIs, Types, and Functions

`struct crash_mem` stores a flexible array of memory `range` entries with current and maximum counts. With `CONFIG_CRASH_DUMP`, APIs include `crash_shrink_memory()`, `crash_get_memory_size()`, `crash_check_hotplug_support()`, `crash_exclude_mem_range()`, `crash_prepare_elf64_headers()`, `__crash_kexec()`, `crash_kexec()`, `kexec_should_crash()`, `kexec_crash_loaded()`, `crash_save_cpu()`, and `kimage_crash_copy_vmcoreinfo()`. Architecture-overridable hooks include crash memory protection and crash hotplug support. Hotplug action constants cover CPU and memory add/remove. `CONFIG_CRASH_DM_CRYPT` adds `crash_load_dm_crypt_keys()` and `dm_crypt_keys_read()`.

## Control Flow

On panic or fatal conditions, crash paths decide whether a crash kernel is loaded, save CPU state, prepare vmcore information, and jump through kexec. Crash dump setup filters reserved ranges and builds ELF headers. Hotplug support updates crash kernel metadata when CPUs or memory change.

## State and Persistence Behavior

Crash memory ranges and vmcoreinfo are in-memory metadata used by the crash kernel. Architecture protection hooks can protect the reserved crash kernel memory after loading. dm-crypt key data may be copied into crash image metadata when configured.

## Dependencies and Integration Points

It depends on linkage and ELF core definitions. It integrates with kexec, panic handling, CPU register capture, memory hotplug, crashkernel reservation, architecture memory protection, vmcoreinfo, and dm-crypt crash key handling.

## Risks and Edge Cases

Crash paths run in failure contexts where locking and allocation options are limited. Range exclusion and ELF header generation must avoid overlapping or invalid memory. Hotplug metadata must stay synchronized with loaded crash images. Disabled-config stubs silently do nothing, so callers must not assume crash functionality exists.

## Test Signals

Signals include kdump boot tests, crashkernel reserved memory protection checks, crash range exclusion unit tests, ELF64 header validation, CPU/memory hotplug update tests, dm-crypt key copy/read tests, and builds with `CONFIG_CRASH_DUMP=n`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/crash_core.h -->
