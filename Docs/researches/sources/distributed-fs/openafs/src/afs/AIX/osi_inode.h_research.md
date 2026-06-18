# sources/distributed-fs/openafs/src/afs/AIX/osi_inode.h

Purpose: AIX inode metadata definitions needed by OpenAFS servers and salvager code.

Important APIs and types: defines `BAD_IGET`, `VICEMAGIC`, accessors `DI_VICEP3` and `I_VICE3`, maps dinode reserved fields to `di_vicemagic` and `di_vicep1` through `di_vicep4`, maps in-core inode fields to the dinode fields, and provides test/clear macros for vice magic.

Control flow: none.

State and persistence: defines how OpenAFS stores volume/file identity metadata in AIX JFS reserved inode fields. These fields are persistent on disk.

Dependencies and integration: consumed by `osi_inode.c` and any AIX code that interprets AFS special inodes.

Risks and test signals: reserved field usage is filesystem-layout sensitive; the comment notes `rsvrd[4]` is used for large-file size, yet `di_vicep4` maps there. Salvager consistency and correct `VICEMAGIC` detection are key signals.
