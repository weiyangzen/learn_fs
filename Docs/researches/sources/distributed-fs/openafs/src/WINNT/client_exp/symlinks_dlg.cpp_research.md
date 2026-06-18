## sources/distributed-fs/openafs/src/WINNT/client_exp/symlinks_dlg.cpp

Purpose: Displays symlink descriptions produced by `ListSymlink`.

Important APIs/functions: `SetSymlinks` copies caller-provided rows. `OnInitDialog` sets a tab stop and inserts each row into the list. `OnHelp` opens symlink help.

Control flow/state: Presentation-only; all AFS probing is done before the dialog is created.

Dependencies/integration: MFC list box, localized resources, and `SYMLINK_HELP_ID`. Called from `gui2fs.cpp`.

Risks/tests: Long symlink targets may exceed the list layout. Test no symlinks, error rows, long targets, Unicode targets, and help routing.
