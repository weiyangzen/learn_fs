# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/vhost_virtio_ioctl.sh

Purpose: Generates vhost/virtio ioctl command name tables.

Important APIs/types/functions: It emits `vhost_virtio_ioctl_cmds[]` for non-read or write-only commands and `vhost_virtio_ioctl_read_cmds[]` for commands with read direction.

Control flow: Two regex passes over `vhost.h` match `VHOST_*` macros using `VHOST_VIRTIO` and hexadecimal command numbers. The read table specifically matches `_IOWR`/read-containing forms so the C consumer can disambiguate by `_IOC_READ`.

State and persistence: stdout-only generator.

Dependencies and integration points: Output is included by `ioctl__scnprintf_vhost_virtio_cmd` in `ioctl.c`.

Risks: Direction-sensitive command names depend on the regex split matching kernel macros exactly. Non-hex command numbers or helper macros would be missed.

Test signals: Regenerate and trace vhost fd ioctls with read and write directions; verify the C consumer selects the expected table.
