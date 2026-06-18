# File Research: sources/cow-pools/nilfs-utils/bin/rmcp.c

Implements `rmcp`, checkpoint deletion. It accepts checkpoint numbers and ranges like `START..END`, `START..`, and `..END`, with `-f` force and `-i` interactive confirmation.

It opens NILFS read-write, gets checkpoint stats, clips ranges to valid oldest/current checkpoint bounds, and deletes each checkpoint with `nilfs_delete_checkpoint()`. `EBUSY` means the target is a snapshot; without force it warns and later tells the user to use `chcp` before removal.

Range parsing comes from `parser.c`. The command does not take the cleaner semaphore directly, unlike `chcp` and snapshot-creating `mkcp`.
