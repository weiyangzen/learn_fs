# sources/distributed-fs/openafs/src/platform/SOLARIS/fs_conv_sol26.c

## Purpose
Implements `fs_conv_sol26`, a root-only Solaris utility that converts raw AFS partition inode metadata between pre-SunOS 5.6 and SunOS 5.6 encodings, with a reverse `unconvert` mode.

## Important APIs, Types, And Functions
Key routines are `main`, `ConvCmd`, `UnConvCmd`, `handleit`, `ProcessFileSys`, `ProcessAfsInodes`, `bread`, `vol_DevName`, `rawname`, `unrawname`, `blockcheck`, `EnsureDevice`, and `CheckMountedDevice`. Global flags `force`, `verbose`, and `unconv` control dry-run/output/direction. The utility uses `struct fs`, `struct dinode`, `vfstab`, `mnttab`, and OpenAFS `VICEMAGIC`, `UID_LONG`, and `GID_LONG` inode conventions.

## Control Flow
`main` requires root, defines `convert` and `unconvert` command syntaxes, and dispatches through the OpenAFS command package. `handleit` parses `-part`, `-device`, `-verbose`, and `-force`; it maps AFS partition names through `/etc/vfstab` or processes explicit raw devices after `CheckMountedDevice`. `ProcessAfsInodes` opens the raw device read-write, validates the UFS superblock, reads cylinder-group inode arrays, classifies AFS inodes by generation/flags/uid/gid fields, and when `-force` is present rewrites uid/gid/large-size fields to the target format.

## State And Persistence
Without `-force`, the utility only reports planned changes. With `-force`, it directly writes modified inode blocks to the raw filesystem device. It also reads `/etc/vfstab`, `/etc/mnttab`, and device nodes under `/dev`.

## Dependencies And Integration Points
Depends tightly on Solaris UFS on-disk structures and OpenAFS partition naming (`/vicep*`). It is an administrative migration tool, not a normal server runtime dependency.

## Risks And Test Signals
Risks are severe: raw-device writes can corrupt mounted or non-AFS filesystems, buffer sizes are fixed, some helpers use static small path buffers, and mounted-device checks allow interactive override. Test signals include dry-run counts, superblock validation, refusal without `-force`, mounted-device prompts, and validation on disposable UFS images before production use.
