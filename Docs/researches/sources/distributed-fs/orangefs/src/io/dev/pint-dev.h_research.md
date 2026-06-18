# sources/distributed-fs/orangefs/src/io/dev/pint-dev.h

Purpose: public user-space API for the OrangeFS kernel request-device bridge.

Important APIs/types: `dev_mask_info_t` distinguishes kernel vs client debug mask updates. `enum pvfs_bufmap_type` indexes I/O and readdir maps. `PINT_dev_unexp_info` describes an upcall buffer, size, and tag. `enum PINT_dev_buffer_type` distinguishes preallocated vs external buffers for writes. `PINT_dev_params` configures mapped buffer count and size. Function prototypes cover initialization/finalization, mapping/unmapping, buffer lookup, unexpected upcall polling/release, downcall writes, remount, and memory helpers.

State/integration: callers treat this as the interface around `pint-dev.c` globals and mapped regions. `PINT_dev_release_unexpected()` must be paired with successful `PINT_dev_test_unexpected()` buffers. The header includes shared ioctl definitions from `pint-dev-shared.h`.

Risks/test signals: buffer type currently has limited behavior in implementation but is validated, so callers should pass the correct enum. Mapped buffer lookup depends on global bufmap values set during mapping. Tests should verify API contracts around upcall ownership, mapped buffer indexing, invalid `bm_type`, and write-list size validation.
