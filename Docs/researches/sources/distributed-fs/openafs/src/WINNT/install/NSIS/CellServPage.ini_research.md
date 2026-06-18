<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/install/NSIS/CellServPage.ini -->
## sources/distributed-fs/openafs/src/WINNT/install/NSIS/CellServPage.ini

Purpose: Defines an NSIS InstallOptions page that asks where the installer should obtain `CellServDB`.

Important fields: The page offers radio buttons for using an existing `CellServDB`, using the packaged file, downloading from `http://grand.central.org/dl/cellservdb/CellServDB`, or selecting a local file. Field 7 is a `FileRequest` with `FILE_MUST_EXIST`.

Control flow and state: NSIS displays mutually exclusive options and a text/file input. Installer script logic must interpret which radio button is selected and then copy/download/use the chosen source.

Persistence and dependencies: The INI itself persists nothing. It depends on installer script handling and network/file availability for selected sources.

Integration points: Affects client cell-server database installation, which later determines how the client locates AFS cell servers when DNS is not used.

Risks: The default radio `State` is only explicit for the download option and is `0`; if scripts do not initialize defaults, behavior can be ambiguous. The URL is plain HTTP and external. Mixed `Type` key casing depends on parser tolerance.

Test signals: Verify radio defaults, packaged/existing/download/file paths, file-exists enforcement, and installer behavior when the download URL is unreachable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/install/NSIS/CellServPage.ini -->
