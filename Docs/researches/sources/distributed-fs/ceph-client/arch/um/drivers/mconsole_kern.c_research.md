<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/mconsole_kern.c -->
# sources/distributed-fs/ceph-client/arch/um/drivers/mconsole_kern.c

Purpose: implements the kernel-side UML management console. It creates the control socket, handles mconsole commands, supports dynamic device configuration/removal, memory plug/unplug, proc reads, SysRq/stack/log/control operations, console-output streaming, boot/panic/user notifications, and socket cleanup.

Important APIs/types/functions: command handlers include `mconsole_version()`, `mconsole_log()`, `mconsole_proc()`, `mconsole_help()`, `mconsole_halt()`, `mconsole_reboot()`, `mconsole_cad()`, `mconsole_stop()`, `mconsole_go()`, `mconsole_config()`, `mconsole_remove()`, `mconsole_sysrq()`, and `mconsole_stack()`. Device registration uses `mconsole_register_dev()` and `struct mc_device`. Init paths include `mem_mc_init()`, `mc_add_console()`, `mconsole_init()`, `create_proc_mconsole()`, and panic notifier setup.

Control flow: the mconsole Unix socket is registered as a UML IRQ. `mconsole_interrupt()` drains requests; interrupt-safe commands run immediately, while process-context commands are copied into `mc_requests` and processed by `mc_work_proc()`. Config/remove locate registered `mc_device` entries and call their callbacks. `mconsole_stop()` blocks signals and synchronously loops on the socket until `go`. Notifications send datagrams to an optional `mconsole=notify:<socket>` target.

State and persistence: runtime globals include proc mount, request queue, registered mconsole devices, unplugged-memory page lists/counts, console streaming clients, notify socket string and socket FD, and mconsole socket path. No state is persisted beyond the host socket file, which is unlinked on reboot.

Dependencies and integration points: depends on UML IRQ/user socket helpers, procfs mounting/reading, reboot and panic notifiers, workqueues, console subsystem, SysRq, task lookup/stack dump, memory dropping support, and mconsole user protocol.

Risks: this is a privileged control plane. Command context classification matters because some operations cannot run in IRQ context. `proc` reads expose guest `/proc` data to the host-side mconsole client. Memory unplug stores dropped pages in custom lists and must keep accounting consistent. Socket cleanup and notification locking must avoid stale paths and races.

Test signals: run `uml_mconsole version/help/config/remove/sysrq/proc/stack/log/stop/go/halt/reboot`, boot with notify socket, panic notification, memory plug/unplug if supported, dynamic console/ubd/vector config through registered devices, and malformed datagrams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/mconsole_kern.c -->
