## sources/distributed-fs/openafs/src/WINNT/client_exp/resource.h

Purpose: Defines numeric resource IDs for the AFS shell extension's menus, strings, dialogs, and controls.

Important APIs/types: Contains command help IDs (`ID_*`), string IDs (`IDS_*`), context-menu command offsets (`IDM_*`), dialog IDs (`IDD_*`), and control IDs (`IDC_*`). These constants bind C++ code to `afs_shl_ext.rc` and localized resources.

Control flow/state: No runtime logic; this is compile-time glue. Duplicates and aliases are meaningful because message maps and string loads use exact numeric IDs.

Dependencies/integration: Included by most dialog headers and `msgs.h`; consumed by menu construction, help routing, and DDX control binding.

Risks/tests: Duplicate control IDs exist (`IDC_OTHER_WRITE2`/`IDC_OTHER_EXECUTE`, `IDC_PROP_SMINFO`/`IDC_QUOTA_MAX`, `IDC_PROP_FID`/others nearby), so resource editing can break bindings. Test resource compilation, every dialog template/control mapping, context-menu command IDs, and localized string availability.
