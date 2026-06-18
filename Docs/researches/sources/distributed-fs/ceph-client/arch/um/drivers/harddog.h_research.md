<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/harddog.h -->
# sources/distributed-fs/ceph-client/arch/um/drivers/harddog.h

Purpose: declares the host-side helper interface for the UML watchdog driver.

Important APIs/types/functions: exported prototypes are `start_watchdog()`, `stop_watchdog()`, and `ping_watchdog()`.

Control flow: kernel watchdog file operations call these functions to spawn `/usr/bin/uml_watchdog`, stop it, and send keepalive bytes.

State and persistence: no state is defined in the header. FDs and helper process IDs are tracked by the C files.

Dependencies and integration points: connects `harddog_kern.c` to `harddog_user.c`, and optionally exports symbols through `harddog_user_exp.c` for module builds.

Risks: prototype mismatch would break the kernel/user helper boundary. The functions are part of the small internal ABI between watchdog halves.

Test signals: build built-in and modular watchdog configurations and exercise open/write/ioctl/release paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/harddog.h -->
