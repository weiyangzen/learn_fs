# sources/distributed-fs/coda/coda-src/partition/ftreeifs.c

Purpose: inode backend that maps synthetic inode numbers into a fixed-depth hex directory tree and stores inode metadata in a central `FTREEDB` resource file.

APIs and flow: `f_init` validates partition options (`depth`, `width`), opens `FTREEDB`, builds a free bitmap from nonzero header records, and records geometry. `f_inotostr` derives payload paths. `f_icreate` allocates a free bitmap slot, creates parent directories via `mkpath`, creates the payload file, writes the header to `FTREEDB`, and fsyncs it. `f_iinc`/`f_idec` update link counts through `f_change_lnk`, deleting payload and clearing bitmap at zero. Read/write/open operate on payload files; list scans headers and stats payload paths.

State/persistence: persistent state is payload file tree plus `FTREEDB`; in-memory state is open fd and free bitmap. Risks include bitmap not set on successful `f_icreate` in the visible code, option validation typo (`i != 10`), central fd seek races, and no locking despite a `Lock` field. Tests are partition test programs and server inode scans.
