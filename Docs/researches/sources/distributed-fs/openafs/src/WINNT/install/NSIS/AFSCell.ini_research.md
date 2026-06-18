<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/install/NSIS/AFSCell.ini -->
## sources/distributed-fs/openafs/src/WINNT/install/NSIS/AFSCell.ini

Purpose: Defines an NSIS InstallOptions page for OpenAFS client cell and behavior defaults.

Important fields: The page has 11 fields. It prompts for the AFS cell name with default `openafs.org`, enables crypt security by default, enables Freelance client by default, enables DNS lookup for cell servers by default, disables integrated logon by default, and shows explanatory label text.

Control flow and state: NSIS reads the `[Settings]` and `[Field N]` sections to render controls and later consume `State` values. The field numbering is not strictly visual order; fields 9/10 appear before 7/8.

Persistence and dependencies: The INI does not persist by itself; installer scripts use selected states to write registry/service configuration. It depends on NSIS InstallOptions semantics.

Integration points: Feeds client configuration properties such as cell name, security level, freelance mode, DNS cell server lookup, and integrated logon in the NSIS installer.

Risks: Defaulting to `openafs.org` may be inappropriate for local deployments if the installer does not override it. Text/control coordinates are fixed and may not localize well. Field order mismatches can break scripts that assume sequential visual layout.

Test signals: Run the NSIS page, verify default states, ensure installer script reads the intended field IDs, and test persisted registry values after install.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/install/NSIS/AFSCell.ini -->
