# sources/distributed-fs/openafs/src/WINNT/client_creds/mounttab.cpp

Purpose: implements the Drive/Mount tab for viewing, adding, editing, removing, activating, and deactivating AFS drive mappings.

Important APIs/functions: `Mount_DlgProc`, `Mount_OnUpdate`, `Mount_OnSelect`, `Mount_OnCheck`, `Mount_OnRemove`, `Mount_AdjustMapping`, `Mount_DriveFromItem`, `Mapping_DlgProc`, `Mapping_OnInitDialog`, `Mapping_OnOK`, and `Mapping_OnEnable`.

Control flow: initialization configures list tabs and populates mappings from `QueryDriveMapList`. Clicking a checked list item activates or inactivates the selected mapping and persists active state. Add/edit opens the mapping dialog, validates drive/path/submount, inactivates old active mappings if needed, activates the new mapping, writes `DRIVEMAPLIST`, and refreshes the list.

State/persistence: file-static `l.iDriveSelectLast` preserves selection. Persistent mapping data is read/written through drive-map APIs; active map state is written by `WriteActiveMap`.

Dependencies/integration: relies on OpenAFS fs utility path constants, drive-map functions, service status, localized messages, and custom checklist/listbox helpers.

Risks: `Mount_DriveFromItem` parses the displayed string rather than storing drive index in item data. Some removal error paths return before freeing `DRIVEMAPLIST`. Mapping validation only checks `/afs` or `\afs` prefix and submount name.

Test signals: no mappings, add/edit/remove, active checkbox toggles, service stopped disabling, unavailable drive letters, invalid paths/submounts, persistent mapping restart behavior, and failed map/unmap status display.
