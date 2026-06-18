# Research: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/IpConfiguratorCommander.h

Purpose: declares the sheet controller used to edit one `DBCellElement` and its server IP/comment list.

Important APIs and state: stores panel/UI outlets, `hasSaved`, target `DBCellElement *cellElement`, backup/work IP arrays, and current selected IP. Methods include `setWorkCell:`, save/cancel, create/delete IP, `saved`, `getPanel`, `commitModify`, `rollbackModify`, `loadValueFromCellIPClass`, and `manageTableSelection:`.

Control flow and persistence: edits are staged in `workIPArray` while the sheet is open, then committed back to the cell model. Persistence to disk is later performed by `AFSPropertyManager saveConfigurationFiles:`.

Dependencies and integration: imports `DBCellElement` and `AFSCommanderPref`. Used by the main pane when a CellServDB row is double-clicked or the IP button is pressed.

Risks: the header imports the main controller, creating tight coupling. The backup/work array naming hides that the object mutates the same `CellIp` instances in the shallow copy.

Test signals: opening with nil/non-nil cell, save vs cancel, add/delete rows, table edits, and subsequent CellServDB save serialization.
