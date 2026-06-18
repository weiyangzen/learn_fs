## sources/distributed-fs/ceph-client/arch/s390/mm/extmem.c

Purpose: manages z/VM DCSS external memory segments on s390. It can query, load, unload, save, and change shared/nonshared access for named segments, maps loaded segments into the kernel address space, reserves their physical ranges, and exports the segment API to loadable users.

Important APIs, types, and functions: `struct dcss_segment` stores EBCDIC name, resource name, start/end, refcount, access mode, VM segment type, ranges, segment count, and `struct resource`. `segment_type()`, `segment_load()`, `segment_unload()`, `segment_save()`, `segment_modify_shared()`, and `segment_warning()` are exported. Internals include `dcss_mkname()`, `dcss_diag()`, `query_segment_type()`, `segment_overlaps_others()`, and `__segment_load()`.

Control flow: callers enter `segment_load()`, which rejects non-VM machines, serializes on `dcss_lock`, reuses an already loaded segment if access mode matches, or allocates a new `dcss_segment`. `__segment_load()` queries segment metadata through diagnose x'64', rejects unsupported multipart layouts, checks overlap with loaded DCSS entries and `iomem_resource`, creates kernel virtual mapping via `vmem_add_mapping()`, then issues shared or nonshared load diagnose. Failures unwind mapping, resource, and allocation state. `segment_modify_shared()` only reloads when the segment refcount is one. `segment_unload()` drops the refcount, releases resources and mappings at zero, and purges on CPU 0 for a documented z/VM workaround. `segment_save()` constructs DEFSEG/SAVESEG CP commands from stored ranges.

State and persistence: persistent in-kernel state is `dcss_list`, guarded by `dcss_lock`, plus per-segment resource reservations and virtual mappings. VM-side persistent state can be changed by `segment_save()`. `loadshr_scode`, `loadnsr_scode`, `purgeseg_scode`, and `segext_scode` hold diagnose subcodes.

Dependencies and integration points: depends on z/VM detection, diagnose x'64', EBCDIC conversion, CPCMD, mem resources, `vmem_add_mapping()`/`vmem_remove_mapping()`, and exported extmem headers. It integrates with users of DCSS segments that need shared memory, exclusive writable segments, or saved segment contents.

Risks: mapping/resource/diagnose ordering must remain exact to avoid leaked resources or stale mappings. Segment overlap checks compare megabyte-shifted ranges and must match DCSS granularity. `segment_modify_shared()` frees and removes a segment on reload failure, so callers must handle invalidation. `segment_save()` command construction depends on bounded string formatting and stored range metadata.

Test signals: VM-only tests should cover query, load shared, load nonshared, duplicate load refcounting, access-mode mismatch `-EPERM`, unload-to-zero purge, unsupported multipart segment `-EOPNOTSUPP`, range overflow `-ERANGE` from `vmem_add_mapping()`, and save command response handling.
