# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/perf_ioctl.sh

Purpose: Generates perf event ioctl command names.

Important APIs/types/functions: It parses `PERF_EVENT_IOC_*` definitions from `perf_event.h` and emits `static const char *perf_ioctl_cmds[]`.

Control flow: Optional header directory selection is followed by a regex matching `_IO*('$', nr, ...)`, sed conversion to index/name pairs, sorting, and formatted output.

State and persistence: Stateless stdout generator.

Dependencies and integration points: The output is included by `ioctl__scnprintf_perf_cmd` in `ioctl.c`.

Risks: The regex is specialized to the dollar ioctl type and numeric command argument; formatting changes may drop entries.

Test signals: Regenerate and confirm entries for common perf ioctls such as enable, disable, reset, and set output; trace ioctl calls on perf event fds.
