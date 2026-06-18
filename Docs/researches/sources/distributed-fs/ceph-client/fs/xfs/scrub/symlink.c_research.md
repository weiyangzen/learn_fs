<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/symlink.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/symlink.c

Purpose: implements online scrub setup and validation for XFS symbolic links. It verifies target type, health-zapped state, plausible size, inline target layout, remote target readability, and null-termination consistency.

Important APIs and functions: `xchk_setup_symlink()` allocates a `XFS_SYMLINK_MAXLEN + 1` scratch buffer before taking the inode lock, asks repair setup to create/reserve a temporary symlink when repair is possible, and delegates inode-content setup to `xchk_setup_inode_contents()`. `xchk_symlink()` is the scrubber; it checks `S_ISLNK`, `XFS_SICK_INO_SYMLINK_ZAPPED`, data fork format, `i_disk_size`, inline fork size and `strnlen`, and remote target contents via `xfs_symlink_remote_read()`.

Control flow: setup prepares shared scratch and repair resources, then locks/loads the target inode contents. Scrub rejects non-symlink inodes with `-ENOENT`, treats a zapped symlink sickness as data-fork corruption, validates size bounds, fast-checks inline symlinks against fork capacity and embedded string length, or reads remote target blocks into the scratch buffer and checks that a null byte is not found before the declared length. A clean remote read clears the zapped-health reminder with `xchk_mark_healthy_if_clean()`.

State and persistence: this file is read-only except for health reporting. It stores transient target bytes in `sc->buf` and updates scrub output flags and healthy masks through common helpers. Persistent repair is delegated to `symlink_repair.c`; setup reserves repair blocks only when the request could repair.

Dependencies and integration points: depends on inode-content setup, common scrub health helpers, XFS symlink remote verifiers/read helpers, data fork layout helpers, and the repair setup path. It is wired into `meta_scrub_ops[]` as `XFS_SCRUB_TYPE_SYMLINK` with `xchk_setup_symlink`, `xchk_symlink`, and `xrep_symlink`.

Risks and test signals: risks include off-by-one size/string checks, treating zero-length or overlong targets inconsistently with VFS/XFS symlink creation rules, and remote read errors being converted incorrectly by `xchk_fblock_process_error`. Tests should cover inline and remote symlinks, missing/incorrect data fork format, zapped health state, exact `XFS_SYMLINK_MAXLEN`, truncated remote block contents, and repair setup reservation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/symlink.c -->
