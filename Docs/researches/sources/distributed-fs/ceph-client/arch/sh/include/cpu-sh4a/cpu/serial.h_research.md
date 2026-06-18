<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4a/cpu/serial.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4a/cpu/serial.h

Purpose: provides the SH-4A CPU serial include guard placeholder.

Important APIs/types/functions: no public symbols beyond `__CPU_SH4A_SERIAL_H`.

Control flow: there is no runtime control flow; platform serial resources are declared elsewhere.

State and persistence: no state or persistence.

Dependencies/integration: included by generic SH serial plumbing when CPU-local serial declarations are expected.

Risks: empty compatibility headers can hide missing subtype serial definitions if callers assume symbols exist.

Test signals: compile serial users for SH-4A subtypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4a/cpu/serial.h -->
