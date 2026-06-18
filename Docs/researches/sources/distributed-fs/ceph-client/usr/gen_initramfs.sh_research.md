<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/usr/gen_initramfs.sh -->
# sources/distributed-fs/ceph-client/usr/gen_initramfs.sh

## Purpose

Shell frontend that turns directories, cpio-list files, or existing cpio archives into the list consumed by `usr/gen_init_cpio`, while also producing dependency lists for kbuild.

## Important APIs, Types, and Functions

Source size: 250 lines, 5922 bytes. No local symbols are defined; the file is data, glue, or an empty compatibility placeholder.

## Control Flow and Data Flow

Options are processed sequentially so uid/gid/date settings affect following inputs. Directories are traversed with `find`, sorted, converted to `file`, `dir`, `nod`, `slink`, `pipe`, or `sock` entries, and optional deps are emitted. File-list inputs are copied through and scanned for file dependencies, then `usr/gen_init_cpio` is invoked.

## State and Persistence Behavior

Uses a temporary cpio-list removed by trap, plus optional dependency output. Root uid/gid remapping and timestamp options persist across subsequent input arguments until changed.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/usr`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

The script relies on external `find`, `sort`, `sed`, `date`, `ls`, and `readlink`; whitespace in paths is not robustly handled. Direct `.cpio` handling is in the Makefile, not this script.

## Test Signals

Test directory, list-file, multiple input, uid/gid squash and current-user remaps, dependency generation, fixed dates, filenames beginning with `-`, and each file type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/usr/gen_initramfs.sh -->
