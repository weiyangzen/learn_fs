<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tracex4.bpf.c -->
# sources/distributed-fs/ceph-client/samples/bpf/tracex4.bpf.c

## Purpose
`tracex4.bpf.c` tracks kernel slab allocations that have not yet been freed, storing allocation time and caller IP for later userspace inspection.

## Important APIs, Types, And Functions
`my_map` is a large hash keyed by object pointer with `struct pair { val, ip }`. `bpf_prog1()` attaches to `kprobe/kmem_cache_free`; `bpf_prog2()` attaches to `kretprobe/kmem_cache_alloc_node_noprof`. It uses `PT_REGS_PARM2()`, `PT_REGS_RC()`, `BPF_KRETPROBE_READ_RET_IP()`, `bpf_ktime_get_ns()`, `bpf_map_update_elem()`, and `bpf_map_delete_elem()`.

## Control Flow
On allocation return, the program records the returned object pointer, current timestamp, and caller IP. On free, it deletes the pointer key from the map. Userspace later reports objects older than one second.

## State And Persistence
Outstanding allocation records persist in `my_map` while the BPF object is loaded or until a matching free occurs.

## Dependencies And Integration Points
It depends on kprobe/kretprobe attachment to kernel slab allocation symbols and the userspace map walker.

## Risks And Edge Cases
Kernel allocator symbol names change across versions; this sample probes `kmem_cache_alloc_node_noprof`. Pointer reuse and missed events can produce misleading records. The map can grow large under high allocation rates.

## Test Signals
The userspace companion should show old object pointers and allocation IPs during normal kernel allocation activity, and records should disappear after frees.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tracex4.bpf.c -->
