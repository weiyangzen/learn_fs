# sources/distributed-fs/ceph-client/scripts/extract-vmlinux

Purpose: Extracts an uncompressed `vmlinux` image from a compressed kernel image or emits an already uncompressed image.

Important APIs/functions: `check_vmlinux()` accepts files identified by `file` as Linux boot executables or by successful `readelf -h`. `try_decompress()` scans for compression magic, tails from candidate offsets through a decompressor into a temp file, then checks the result.

Control flow: Validates one image argument, creates a temp file with `mktemp`, tries gzip, xz, bzip2, lzma, lzop, lz4, and zstd offsets, then checks the original file. On success it cats the uncompressed image to stdout and reports method/offset to stderr; otherwise prints failure and exits nonzero by falling off shell end after echo.

State/persistence: Uses one temp file removed by trap. Writes binary image to stdout.

Dependencies/integration: Shell, `file`, `readelf`, `tr`, `grep`, `tail`, and optional decompressors. Used for debugging and certificate/config extraction.

Risks: Magic scanning can false-positive. Missing decompressors are hidden by redirected errors. Binary output and stderr status must be redirected correctly by callers. It only validates enough to identify an ELF/kernel image.

Test signals: Known compressed formats, already uncompressed vmlinux, invalid image, missing decompressor, and images with multiple embedded compression streams.
