## sources/distributed-fs/ceph-client/drivers/s390/Makefile

Purpose: Defines the top-level build aggregation for S/390-specific drivers.

Important APIs/types/functions: This is a kbuild Makefile rather than C code. Its only build rule appends `cio/`, `block/`, `char/`, `crypto/`, `net/`, `scsi/`, and `virtio/` subdirectories to `obj-y`.

Control flow: During kernel build descent into `drivers/s390`, kbuild always visits the listed subdirectories because they are under `obj-y`; configuration inside each child directory decides which objects are built.

State and persistence: No runtime state. Build state is the set of subdirectory make invocations.

Dependencies/integration: Integrates with Linux kbuild and the architecture-specific driver tree. It is the parent entry point for `drivers/s390/block/Makefile`, including DASD and SCM block drivers.

Risks: Removing a subdirectory here silently excludes its internal Kconfig-selected objects from the build. Adding optionality here would be redundant with child Kconfig/Makefile logic and could break expected S/390 driver discovery.

Test signals: `make drivers/s390/` or a full S390 build should descend into all listed directories. Kbuild warnings about missing directories or unvisited configured objects would indicate issues.
