# sources/distributed-fs/ceph-client/fs/ext4/mmp.c

## Purpose
`mmp.c` implements ext4 Multiple Mount Protection. MMP stores a heartbeat block on disk and refuses mount if that block appears to be actively updated by another node or fsck. After mount, a kernel thread (`kmmpd`) periodically writes a changing sequence number, timestamp, nodename, device name, and checksum to the MMP block.

## Important APIs, Types, And Functions
Checksum helpers are `ext4_mmp_csum()`, `ext4_mmp_csum_verify()`, and `ext4_mmp_csum_set()`. I/O helpers are `write_mmp_block_thawed()`, `write_mmp_block()`, and `read_mmp_block()`. Diagnostics use `__dump_mmp_msg()`. The heartbeat thread is `kmmpd()`. Public lifecycle functions are `ext4_multi_mount_protect()` and `ext4_stop_mmpd()`.

## Control Flow
`ext4_multi_mount_protect()` validates the MMP block location, reads and verifies the block, derives a check interval, and rejects fsck-active or changing sequences. It writes a new random sequence, waits, rereads, and verifies the sequence remains unchanged before storing the buffer and starting `kmmpd`.

`kmmpd()` updates the sequence, timestamp, nodename, device name, checksum, and adaptive check interval. It writes synchronously each update interval, self-checks if writes take too long, reports multiply-mounted evidence if the sequence or nodename changes unexpectedly, and writes `EXT4_MMP_SEQ_CLEAN` on clean stop. `ext4_stop_mmpd()` stops the thread and releases the buffer.

## State And Persistence Behavior
The persistent state is the MMP block containing magic, sequence, timestamp, nodename, block device name, check interval, padding, and checksum. While mounted, `mmp_seq` changes regularly. On clean unmount it becomes `EXT4_MMP_SEQ_CLEAN`; `EXT4_MMP_SEQ_FSCK` blocks mount regardless of timestamp age.

In-memory state is `s_mmp_bh` and `s_mmp_tsk`. Reads force fresh disk I/O by clearing the buffer uptodate bit. Writes use synchronous priority metadata submission and are protected against filesystem freezing except during mount/remount setup, where existing mount locks already apply.

## Dependencies And Integration Points
The file depends on buffer heads, synchronous block I/O, random numbers, UTS nodename, kthreads, scheduling/jiffies, superblock freeze guards, ext4 feature/checksum helpers, mount/remount setup, unmount teardown, emergency state, and metadata checksum configuration.

## Risks And Edge Cases
Timing is the core risk. Slow storage can delay heartbeats, while cached reads could miss another writer. The code adapts the check interval, forces fresh reads, and treats interruptions as mount failure. Bad magic/checksum prevents safe MMP use. Persistent write errors undermine the heartbeat and are logged with throttling. Feature disablement while running stops the active loop.

## Test Signals
Tests should cover clean mount/unmount, active sequence change rejection, fsck sequence rejection, invalid MMP block location, bad magic, bad checksum, interrupted waits, thread creation failure, adaptive interval clamping, delayed-write self-check detecting another updater, write I/O error handling, and feature-disabled shutdown. Shared-device or mocked block-I/O tests should verify reads do not trust stale cached buffers.
