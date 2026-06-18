## sources/distributed-fs/openafs/src/WINNT/client_exp/mount_points_dlg.cpp

Purpose: Displays a list of mount point descriptions produced by `ListMount`.

Important APIs/functions: `SetMountPoints` copies caller-provided strings into `m_MountPoints`. `OnInitDialog` configures list-box tab stops and inserts each mount point. `OnHelp` opens the mount point help context.

Control flow/state: All display state is in the copied `CStringArray`; the dialog does not query AFS itself.

Dependencies/integration: Depends on localized dialog resources and MFC list boxes. `gui2fs.cpp` constructs and shows it after probing selected paths.

Risks/tests: Tab stop values assume localized text width and may truncate long volume/cell names. Test empty lists, many selections, long mount targets, and help routing.
