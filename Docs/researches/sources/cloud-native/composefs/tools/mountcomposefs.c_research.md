# sources/cloud-native/composefs/tools/mountcomposefs.c

## Purpose
`mountcomposefs.c` implements the `mount.composefs` helper. It parses mount-style arguments and options, translates them into `lcfs_mount_options_s`, and calls `lcfs_mount_fd` to mount a composefs image.

## Important APIs, Types, And Functions
`usage` documents helper and direct invocation forms. `parse_option` handles comma-separated mount options with backslash escaping, delegating value unescaping to `unescape_option`. `main` maps options into `lcfs_mount_options_s`, including object directories, digest, idmap fd, upper/work dirs, readonly, and verity flags.

## Control Flow
The program accepts `-t composefs`, `-o`, and `-h`, then requires `IMAGE MOUNTPOINT`. It parses mount options, splits `basedir=PATH[:PATH]` into `options.objdirs`, validates that at least one object dir exists, requires `upperdir` and `workdir` together, sets digest and verity flags, optionally opens an idmap user namespace, opens the image, calls `lcfs_mount_fd`, and reports specialized verity/signature errors before freeing allocated object-dir storage.

## State And Persistence
Runtime state is local option parsing and file descriptors. The persistent effect is a kernel mount at the requested mount point. No configuration is written.

## Dependencies And Integration Points
It depends on `libcomposefs/lcfs-mount.h`, Linux mount/fsverity headers, and POSIX open/error APIs. It integrates with `/sbin/mount.<type>` helper conventions and with composefs object directories and optional overlay upper/work dirs.

## Risks
Option parsing mutates the `-o` string in place, as mount helpers usually can but tests should cover escaping. `basedir` splitting uses colon as a separator, so object paths containing colons are not representable. A missing object dir is fatal. The code frees `options.objdirs` only on success path after `lcfs_mount_fd`; failures exit via `errx`, which is acceptable for a short-lived CLI.

## Test Signals
Tests should cover direct and mount-helper syntax, unsupported `-t`, escaped commas/equals, multi-basedir parsing, verity/tryverity/digest flag mapping, idmap fd opening, ro/rw handling, upper/work pairing validation, and error messages for libcomposefs verity failures.
