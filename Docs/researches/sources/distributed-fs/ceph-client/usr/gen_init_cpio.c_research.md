<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/usr/gen_init_cpio.c -->
# sources/distributed-fs/ceph-client/usr/gen_init_cpio.c

## Purpose

Host utility that converts a textual initramfs file list into a `newc` or checksum `crc` cpio archive. It supports regular files, hard links, directories, symlinks, device nodes, pipes, sockets, fixed timestamps, output files, checksums, and best-effort data alignment.

## Important APIs, Types, and Functions

Source size: 781 lines, 17489 bytes. Functions/classes: push_buf, push_pad, push_rest, cpio_trailer, cpio_mkslink, cpio_mkslink_line, if, cpio_mkgeneric, cpio_mkgeneric_line, if, cpio_mkdir_line, cpio_mkpipe_line, cpio_mksock_line, cpio_mknod, cpio_mknod_line, if, cpio_mkfile_csum, cpio_mkfile, plus 32 more. Includes: stdio.h, stdlib.h, stdint.h, stdbool.h, sys/types.h, sys/stat.h, string.h, unistd.h, time.h, fcntl.h, errno.h, ctype.h, limits.h. Macros/defines: _GNU_SOURCE, xstr, str, MIN, CPIO_HDR_LEN, CPIO_TRAILER, padlen, LINE_SIZE.

## Control Flow and Data Flow

Main parses options, opens the list, dispatches each line through `file_handler_table`, writes cpio headers and payloads with `push_*` helpers, and appends a padded `TRAILER!!!`. File entries stat the source, optionally checksum and copy via `copy_file_range` or read/write fallback, and emit hard-link names before the payload-carrying final link.

## State and Persistence Behavior

Persistent output is the archive written to stdout or `-o`. Internal global state tracks archive `offset`, synthetic inode number, timestamp policy, checksum mode, output fd, alignment, and zero padding.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/usr`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Text parsing uses fixed `PATH_MAX` buffers and whitespace-separated fields. Cpio has 32-bit timestamp and file-size limits. Alignment padding is constrained by `PATH_MAX`, and environment expansion writes into the location buffer.

## Test Signals

Generate archives with every record type, hard links, env-expanded paths, checksum mode, fixed timestamps, negative/overflow timestamps, large files, alignment requests, stdin list input, and malformed list lines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/usr/gen_init_cpio.c -->
