# sources/distributed-fs/openafs/src/config/vioc.h

This header centralizes Venus ioctl and pioctl numeric command constants. It includes `afs/vice.h` unless `_VICEIOCTL` is already available, then defines legacy IBM-managed `VIOC*` commands, coordinated central registry `C` commands, and OpenAFS-specific `O` commands.

Important constants include file-descriptor ioctls `VIOCCLOSEWAIT`, `VIOCABORT`, `VIOCIGETCELL`; pioctls for ACLs, tokens, volume state, flushing, checks, prefetch, PAG, cache size, new cells, sysname, NFS export, server/client preferences, RX stats, encryption settings, OSD extensions, and VCX status; coordinated commands like `VIOC_NEWALIAS`, `VIOC_GETTOK2`, `VIOC_NEWUUID`, `VIOC_GETPAG`, `VIOC_FLUSHALL`; and OpenAFS commands `VIOC_NFS_NUKE_CREDS` and `VIOC_SETBYPASS_THRESH`.

There is no runtime state; the ABI is the persisted contract. Integration is with userspace tools, `pioctl`, cache manager dispatch tables, and kernel/user boundary marshalling. Risks are number collisions, accidental use of reserved site/private ranges in distributed software, and mismatched command definitions between clients and kernel modules. Test signals are compile-time inclusion by `venus.h`/`kopenafs.h` and runtime pioctl dispatch tests for commands whose structures are defined elsewhere.
