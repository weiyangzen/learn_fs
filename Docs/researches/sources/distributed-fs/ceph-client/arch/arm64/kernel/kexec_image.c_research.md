# sources/distributed-fs/ceph-client/arch/arm64/kernel/kexec_image.c

Purpose: Implements the arm64 `Image` format loader for `kexec_file_load`.

Important APIs: static `image_probe()` validates the arm64 magic and buffer size. `image_load()` validates a nonzero image size, endian compatibility, page-size granule support, loads the kernel segment with `TEXT_OFFSET`, and delegates initrd/DTB/crash segments to `load_other_segments()`. `kexec_image_ops` exposes probe/load and optional PE signature verification.

Control flow: the loader repeatedly tries to place the kernel segment, then attempts to place dependent segments. If dependent placement fails, it removes the kernel segment, advances the minimum address, and retries. On success it adjusts the visible segment start/memsz by `text_offset` and sets `image->start`.

Dependencies and integration: depends on arm64 Image header definitions, cpufeature granule checks, kexec buffer placement, `machine_kexec_file.c` helpers, optional PE signature verification, and `kexec-tools` expectations for direct kernel entry.

Risks and test signals: risks are accepting incompatible endian/page-size images, mishandling text offset, exhausting placement holes, or leaking segments after retries. Test with signed/unsigned Image loads, all page sizes, mixed-endian capability, initrd/DTB placement pressure, and crash/non-crash kexec_file paths.
