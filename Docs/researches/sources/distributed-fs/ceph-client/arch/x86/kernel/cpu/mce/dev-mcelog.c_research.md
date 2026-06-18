# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mce/dev-mcelog.c

Purpose: provides the legacy `/dev/mcelog` misc device and helper trigger interface for user-space MCE consumers.

Important APIs and flow: `dev_mce_log()` is a notifier that copies decoded MCEs into a fixed in-memory ring-like buffer, marks overflow, wakes pollers, and marks non-AMD records handled by mcelog. `mce_work_trigger()` schedules an optional usermode helper configured through the `trigger` sysfs attribute. Character device operations implement exclusive open, full-buffer reads that first drain APEI ERST records, poll readiness, privileged ioctls for record length/log length/flags, and privileged writes that call the injector notifier chain. `dev_mcelog_init_device()` allocates the buffer, registers the misc device, and registers the decode notifier.

State and persistence: state includes the allocated `mce_log_buffer`, open/exclusive counters, trigger helper path, waitqueue, APEI-read completion flag, and injector notifier chain. APEI records may originate from persistent ERST storage but are cleared after read.

Dependencies and integration: depends on common MCE notifier priorities, APEI helpers, miscdevice, usermodehelper, poll/ioctl APIs, and optional injection support.

Risks and test signals: legacy ABI expectations are strict; buffer full behavior discards new entries. Signals include `/dev/mcelog` read/ioctl/poll tests, helper trigger execution, exclusive-open behavior, ERST drain ordering, and injection writes with `CAP_SYS_ADMIN`.
