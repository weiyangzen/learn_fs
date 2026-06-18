# sources/distributed-fs/ceph-client/drivers/s390/char/tape_char.c

Purpose: character-device frontend for the tape subsystem, exposing rewinding and non-rewinding tape minors and implementing read, write, open, release, and MTIO ioctls.

Important APIs/types/functions: defines `tape_fops`, `tapechar_setup_device`, `tapechar_cleanup_device`, `tapechar_read`, `tapechar_write`, `tapechar_open`, `tapechar_release`, `__tapechar_ioctl`, `tapechar_ioctl`, `tapechar_init`, and `tapechar_exit`.

Control flow: setup registers `ntibmN` and `rtibmN` class devices for the assigned minor pair. Open resolves minor to `tape_device`, calls `tape_open`, and stores the device in `private_data`. Reads terminate pending writes first, choose fixed or variable block size, allocate/check IDAL buffers, let the discipline build a read request, execute it, and copy IDAL data to userspace. Writes split input into fixed-size blocks when configured, copy userspace data into IDAL buffers, reuse the discipline write request, and update required tape marks. Release rewinds rewinding minors and writes required tape marks before dropping buffers and references.

State and persistence: tracks per-device `char_data.block_size`, IDAL buffer arrays, and `required_tapemarks`; file private data holds the active device reference. No persistent storage is created.

Dependencies and integration: depends on tape core request APIs, `tape_std_terminate_write`, `tape_mtop`, `register_tape_dev`, Linux mtio helpers such as `put_user_mtget`/`put_user_mtpos`, and IDAL user-copy helpers.

Risks: required tapemarks must be flushed before reads, seeks, and close to maintain tape format; partial writes at ENOSPC require discipline EOV processing; reads infer transferred bytes from CPA/residual count; block-size and userspace buffer constraints return EINVAL/EFAULT.

Test signals: open exclusivity via core state, fixed and variable block reads/writes, rewinding vs non-rewinding close behavior, MTIOCTOP/MTIOCGET/MTIOCPOS ioctls, ENOSPC partial-write handling, and IDAL allocation boundary at `MAX_BLOCKSIZE`.
