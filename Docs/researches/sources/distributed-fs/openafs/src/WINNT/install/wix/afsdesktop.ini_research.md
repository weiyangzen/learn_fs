<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/install/wix/afsdesktop.ini -->
## sources/distributed-fs/openafs/src/WINNT/install/wix/afsdesktop.ini

Purpose: Provides shell folder customization metadata for an OpenAFS desktop/start-menu folder icon in the WiX installer tree.

Important fields: `[.ShellClassInfo]` sets `IconFile=client\\program\\afsd_service.exe` and `IconIndex=0`.

Control flow and state: Windows Explorer reads this INI when the folder is marked appropriately by installer attributes.

Persistence and dependencies: Persisted as an installed INI file. Depends on the referenced executable path existing relative to the folder context and on shell folder customization behavior.

Integration points: WiX installer packaging for OpenAFS client desktop resources.

Risks: If `afsd_service.exe` is moved or not installed, the icon breaks. The file has no localized resource indirection.

Test signals: Install package and verify folder icon display, uninstall cleanup, and path validity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/install/wix/afsdesktop.ini -->
