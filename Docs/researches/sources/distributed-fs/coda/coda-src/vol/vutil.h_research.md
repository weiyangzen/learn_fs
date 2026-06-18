# sources/distributed-fs/coda/coda-src/vol/vutil.h

Purpose: declares utility routines used by offline volume programs and dump/salvage tooling.

Important APIs: `VCreateVolume`, `MakeBackupVolume`, `AssignVolumeName`, `CopyVolumeHeader`, `ClearVolumeStats`, `ListViceInodes`, `ListCodaInodes`, `HashString`, and `CloneVolume`. `VCreateVolume` is annotated as transaction-required and has default type/log-size arguments.

Control flow/state: the header exposes creation/clone/list helpers but implementations are split across several utility files. Inode listing callbacks accept `ViceInodeInfo` and a volume id parameter to judge ownership.

Dependencies/integration: includes transaction annotations and `voldefs.h`; depends on `Volume`, `Error`, `VolumeDiskData`, and inode info types from surrounding includes. Risks include broad prototypes with raw `char *` and function-pointer callbacks, and default arguments coupling C++ callers to volume type constants. Test signals: compile volutil programs, create/clone/backup workflows, inode listing callbacks, and hash compatibility with VLDB generation.
