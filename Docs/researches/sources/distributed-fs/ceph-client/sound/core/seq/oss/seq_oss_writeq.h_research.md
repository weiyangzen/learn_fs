# sources/distributed-fs/ceph-client/sound/core/seq/oss/seq_oss_writeq.h

Purpose: defines the OSS write queue synchronization structure and public writeq operations.

Important APIs and types: `struct seq_oss_writeq` stores the owning `seq_oss_devinfo`, max length, sync time, pending flag, wait queue, and spinlock. Declares allocation, deletion, clear, sync, wakeup, free-size query, and output threshold setting.

Control flow: open allocates a writeq, ioctl sync/threshold uses it, reset/release clears and deletes it, and echo event input calls wakeup.

State and persistence: no globals; per-open transient queue metadata.

Dependencies and integration: includes central OSS device state and works with ALSA sequencer client pools and echo events.

Risks: users must not call sync on a freed writeq; release/reset ordering relies on file-level serialization in `seq_oss.c`.

Test signals: compile all users and run sync/clear/free-size/threshold tests through an OSS write-open file.
