## sources/distributed-fs/ceph-client/tools/lib/bpf/usdt.c

Purpose: Implements libbpf user-space USDT discovery, argument-spec parsing, BPF map population, and uprobe attachment.

Important APIs/functions: `usdt_manager_new/free()` creates per-`bpf_object` state and feature probes. `usdt_manager_attach_usdt()` is the attach entry point. `collect_usdt_targets()` parses ELF notes and resolves probe/semaphore offsets. `parse_usdt_note()`, `parse_usdt_spec()`, and architecture-specific `parse_usdt_arg()` convert SystemTap notes into BPF-side specs. `bpf_link_usdt_*()` handles detach/deallocation.

Control flow: Attach opens and validates ELF, normalizes PID, scans `.note.stapsdt`, resolves ET_EXEC/ET_DYN file offsets and optional process VMAs, handles `.stapsdt.base` prelink correction, validates semaphore support, parses argument specs, deduplicates specs within one logical attach, updates spec and IP maps, then attaches either uprobe-multi or individual uprobes. Detach destroys links, removes IP map entries when needed, and returns spec IDs to the manager free list.

State/persistence: `usdt_manager` persists per object, tracking maps, feature flags, next/free spec IDs. `bpf_link_usdt` persists per attach with spec IDs and child links. BPF maps persist spec/IP data for loaded programs.

Dependencies/integration: Uses libelf/gelf, `/proc/<pid>/maps`, BPF map APIs, uprobe attach APIs, kernel feature probes, hashmap, architecture-specific `pt_regs` layouts, and SystemTap SDT note format.

Risks: Unsupported ELF class/endianness/type, missing notes, shared-library attachment without cookies and PID, semaphore refcount kernel support, IP collisions, spec-map exhaustion, arch parser gaps, and SIB/register syntax coverage. NOP optimization adjusts offsets on x86_64 and needs instruction validation.

Test signals: Tests should cover ET_EXEC and ET_DYN, PID 0/-1, container `/proc/<pid>/root` paths, prelink base adjustment, semaphore probes, uprobe-multi and fallback links, spec dedup/free-list reuse, map-update failures, each supported architecture parser, too many args, invalid sizes, and unsupported arch behavior.
