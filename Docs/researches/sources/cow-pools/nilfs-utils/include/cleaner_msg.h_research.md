# File Research: sources/cow-pools/nilfs-utils/include/cleaner_msg.h

Defines POSIX message queue protocol structures for cleaner control. Commands include get status, run, suspend, resume, tune, reload, wait, stop, and shutdown.

Requests carry command, argument size, client UUID, and optional payloads for cleaner args, paths, or job IDs. Responses carry ACK/NACK result, cleaner status, errno, and job ID. Message sizes are capped at 4096 bytes, with path payload up to 4064 bytes.
