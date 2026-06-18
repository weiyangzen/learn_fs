# File Research: sources/cow-pools/nilfs-utils/lib/cleaner_ctl.c

Implements high-level cleaner daemon control over POSIX message queues. It discovers mounted NILFS filesystems, extracts `gcpid` from mount options, resolves device IDs, opens per-client receive queues and per-device daemon send queues, and sends cleaner protocol requests.

Commands implemented include status, run, suspend, resume, tune, reload, wait, relative wait, stop, and shutdown. Each command clears stale receive messages first, sends a request with client UUID, receives a response, and maps NACK responses back to `errno`.

The file also supports launching a cleaner through `nilfs_launch_cleanerd()` and later opening queues separately.
