# sources/distributed-fs/ceph-client/sound/core/seq/seq_compat.c

Purpose: provides 32-bit compat ioctl handling for ALSA sequencer when included from `seq_clientmgr.c`.

Important APIs and types: defines `struct snd_seq_port_info32`, compat command constants for port operations, `snd_seq_call_port_info_ioctl()`, and `snd_seq_ioctl_compat()`.

Control flow: most ioctl commands are ABI-compatible and delegate directly to native `snd_seq_ioctl()` after `compat_ptr()`. Port-info commands need conversion because the embedded kernel callback pointer/flags/time fields differ in 32-bit layout; the helper copies the 32-bit struct into a native `snd_seq_port_info`, clears the kernel callback pointer, calls native kernel client control, and copies results back.

State and persistence: no independent state; mutates sequencer client, port, queue, subscription, and UMP state through native ioctl handlers.

Dependencies and integration: depends on native client manager functions, Linux compat APIs, and kernel allocation helpers.

Risks: port-info conversion must not allow user-provided `kernel` callback pointers. Direct delegation for other commands assumes identical compat layout. UMP info commands are delegated, so their user-pointer handling must already be compat-safe.

Test signals: 32-bit userspace tests for create/delete/get/set/query port, all directly delegated ioctls, invalid pointers, and running-mode convert32 interaction with variable user pointers.
