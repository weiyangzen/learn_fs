# Research: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/DBCellElement.h

Purpose: declares the model object for an AFS CellServDB cell, including default-token flags, default-cell flag, name, comment, and server list.

Important APIs and state: fields are `userDefaultForToken`, `userDefaultCell`, `cellName`, `cellComment`, and `ipCellList`. Public methods set/get cell name and comment, set/query token default and default cell flags, add/get `CellIp` entries, serialize via `description`, and compare via `isEqual:`/`isEqualToString:`.

Control flow and persistence: `AFSPropertyManager` populates these objects from `ThisCell`, `TheseCells`, and `CellServDB`; `AFSCommanderPref` displays and toggles flags; `IpConfiguratorCommander` edits cell metadata and IPs; `AFSPropertyManager saveConfigurationFiles:` writes each `description`.

Dependencies and integration: imports Cocoa and `CellIp.h`. The mutable IP array is exposed directly for table editing.

Risks: the object has no validation for CellServDB grammar, duplicate cell names, default-cell uniqueness, or server list validity. Direct mutable array exposure allows callers to bypass invariants.

Test signals: default flags, unique default-cell assignment through `AFSPropertyManager`, equality behavior, empty/duplicate IP lists, and serialization of comments and addresses.
