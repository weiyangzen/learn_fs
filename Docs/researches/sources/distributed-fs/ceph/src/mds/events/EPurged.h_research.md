# sources/distributed-fs/ceph/src/mds/events/EPurged.h

Purpose: Declares a journal event recording purged inode intervals and associated inode-table version.

Important APIs/types: `EPurged` stores `interval_set<inodeno_t> inos`, log segment sequence, and `inotablev`, and implements encode/decode/dump/print/update_segment/replay.

Control flow: After purge work frees inode ranges, this event lets replay advance inode-table purge/free state and update segment accounting.

State and persistence behavior: Persistent payload is the interval set, segment seq, and inotable version. It links purge completion to inode-table durability.

Dependencies and integration points: Uses `LogEvent`, `interval_set`, and `LogSegment` sequence types; consumed by purge/inotable replay.

Risks: The print string says `Eurged`, likely a typo but harmless unless tests assert text. Incorrect intervals can leak or double-free inode numbers.

Test signals: Interval encode/decode, replay inotable version advancement, and segment update accounting.
