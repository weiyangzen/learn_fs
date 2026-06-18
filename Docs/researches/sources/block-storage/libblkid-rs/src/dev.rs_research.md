# File Research: sources/block-storage/libblkid-rs/src/dev.rs

Purpose: Wraps cached libblkid device handles and device iteration.

Key APIs:
- `BlkidDev::devname`
- `BlkidDev::devsize`
- `BlkidDev::tag_iter`
- `BlkidDev::has_tag`
- `BlkidDevIter::search`
- `Iterator for BlkidDevIter`

Implementation notes:
- `BlkidDev` is a non-owning wrapper around `blkid_dev`.
- `devsize` opens the device path and passes its file descriptor to `blkid_get_dev_size`.
- `BlkidDevIter` owns the C iterator and ends it in `Drop`.

Notable risks:
- `BlkidDev::new` accepts null pointers from callers; methods assume valid C handles.
- `Iterator::next` treats any negative return as end-of-iteration, so libblkid errors cannot be distinguished from normal completion.
- `devsize` depends on opening the device path, so cached devices that no longer exist or require privileges return I/O errors.
