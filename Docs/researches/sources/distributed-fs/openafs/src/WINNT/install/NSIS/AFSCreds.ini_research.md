<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/install/NSIS/AFSCreds.ini -->
## sources/distributed-fs/openafs/src/WINNT/install/NSIS/AFSCreds.ini

Purpose: Defines an NSIS InstallOptions page for AFS Credentials startup and command-line options.

Important fields: The page has 14 fields. It defaults to starting AFS Credentials at system login and enabling auto-initialize (`-a`), renew drive maps (`-m`), IP address change detection (`-n`), and quiet (`-q`). It defaults to not showing the credentials window on startup (`-s` absent). Labels group startup parameters and command-line options.

Control flow and state: NSIS renders checkboxes and labels from fixed coordinates. Installer scripts consume checkbox `State` values to construct shortcut parameters or registry settings.

Persistence and dependencies: Persistence occurs later through installer registry/shortcut writes. Depends on NSIS InstallOptions.

Integration points: Related WiX custom action code reads/writes `StartAfscredsOnStartup` and `AfscredsShortcutParams`; this NSIS page represents the older installer path.

Risks: Mixed-case `Type`/`type` keys depend on parser tolerance. Defaults may silently enable behaviors users did not expect. Fixed coordinates are localization-sensitive.

Test signals: Verify checkbox defaults, generated shortcut parameters, persisted registry values, and upgrade migration consistency with WiX `DetectSavedConfiguration`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/install/NSIS/AFSCreds.ini -->
