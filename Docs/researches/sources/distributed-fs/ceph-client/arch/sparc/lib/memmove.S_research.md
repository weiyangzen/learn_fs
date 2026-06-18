# sources/distributed-fs/ceph-client/arch/sparc/lib/memmove.S

Purpose: SPARC64 `memmove` implementation.

Important APIs/functions: Exports `memmove`.

Control flow: Compares destination/source ranges. If forward copy is safe, copies bytes/xwords forward with alignment checks. If ranges overlap with destination after source, it copies backward from the end to preserve source bytes.

State and persistence: Mutates destination buffer only.

Dependencies/integration: Includes `linux/export.h` and `linux/linkage.h`; built for `CONFIG_SPARC64`.

Risks/test signals: Overlap direction and tail handling are primary. Test identical pointers, forward/backward overlap, unaligned starts, zero length, and random memmove comparisons.
