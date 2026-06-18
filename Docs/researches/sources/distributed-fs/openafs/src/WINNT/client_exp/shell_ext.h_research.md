## sources/distributed-fs/openafs/src/WINNT/client_exp/shell_ext.h

Purpose: Declares the `CShellExt` COM/MFC shell extension class and overlay variant `CShellExt2`.

Important APIs/types: The class contains nested interface parts for `IContextMenu`, `IShellExtInit`, `IShellIconOverlayIdentifier`, `IQueryInfo`, `IPersistFile`, and `IShellPropSheetExt`. State fields track file selection, AFS classification, overlay object type, allocator, and overlay setting.

Control flow/state: `CShellExt2` derives from `CShellExt` and sets `m_overlayObject = 1` for mount overlays; the base object uses `0` for symlink overlays.

Dependencies/integration: Includes `shlobj.h`, MFC `CCmdTarget`, COM macros, and registry title/path constants. Implementation integrates with Explorer registration and AFS operations.

Risks/tests: Global reference counters are declared here and shared across interface parts. Test COM aggregation/interface querying, object lifetime, overlay selection, and registration constants.
