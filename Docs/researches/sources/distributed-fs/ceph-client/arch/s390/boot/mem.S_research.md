<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/mem.S -->
# sources/distributed-fs/ceph-client/arch/s390/boot/mem.S

Purpose: Reuses the architecture library memory assembly routines in the boot environment.

Important APIs/types/functions: Declares no local symbols; all memory routine symbols come from `../lib/mem.S`.

Control flow: The assembler includes the shared s390 memory implementation directly, making low-level memory primitives available to decompressor code.

State and persistence: No local data is defined here.

Dependencies and integration points: Depends on `arch/s390/lib/mem.S` and on that file being safe to build for boot. These primitives underpin early `memcpy`, `memmove`, and related operations used by decompression and memory layout setup.

Risks: Assembly include wrappers are sensitive to section, relocation, and instrumentation assumptions. Changes in the shared memory assembly can affect boot long before normal exception handling is available.

Test signals: s390 decompressor build/link tests, early boot smoke tests, and objdump/relocation checks after changing shared memory assembly.

Source read size: 2 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/mem.S -->
