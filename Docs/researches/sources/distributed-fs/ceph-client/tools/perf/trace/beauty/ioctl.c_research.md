# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/ioctl.c

Purpose: This file beautifies `ioctl` command arguments for `perf trace`, translating encoded `_IOC` command words into subsystem command names or a structured fallback tuple.

Important APIs/types/functions: `syscall_arg__scnprintf_ioctl_cmd` is the exported formatter. Static helpers handle TTY, DRM, ALSA PCM, ALSA control, KVM, vhost/virtio, perf event, and USBDEVFS command spaces. `ioctl__scnprintf_cmd` decodes `_IOC_DIR`, `_IOC_TYPE`, `_IOC_NR`, and `_IOC_SIZE`.

Control flow: The formatter first checks the traced file descriptor via `thread__files_entry`; USB device major 189 is treated as USBDEVFS even though it shares type letter `U` with ALSA control. Otherwise, the decoded ioctl type indexes a sparse ordered dispatch table. If no specialized table matches, the code prints `_IOC_NONE`, `_IOC_READ`, and/or `_IOC_WRITE` with the raw type, number, and size.

State and persistence: No persistent state is stored. It consumes live thread file metadata and generated static string arrays.

Dependencies and integration points: It includes generated arrays from beauty shell scripts and uses `struct syscall_arg`, `struct file`, `strarray`, `scnprintf`, and UAPI ioctl macros. It is wired into perf trace syscall argument formatting for x86 according to the source comment.

Risks: Type collisions are real, especially `U`, so file metadata quality determines USB versus ALSA decoding. Generated table omissions degrade output to raw tuples. The subsystem dispatch table relies on index arithmetic from `$` to `0xAF`.

Test signals: Exercise representative ioctl syscalls for TTY, KVM, perf event, ALSA control/PCM, and USB device fds. Confirm unknown commands print fallback tuples and `show_string_prefix` controls `_IOC_` prefixes.
