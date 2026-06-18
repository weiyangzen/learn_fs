# sources/distributed-fs/openafs/src/WINNT/client_exp/PropVolume.cpp

Purpose: implements the Explorer property page for AFS volume and server/quota information.

Important APIs/functions: `CPropVolume::PropPageProc` handles initialization, apply, and flush button commands.

Control flow: on init it decides whether to follow a mountpoint, displays selected path, cell, fileserver, volume info, quota and partition metrics, and "where is" server list. It uses `StrFormatByteSize64` for human-readable quota/partition sizes. The flush button calls `FlushVolume`.

State/persistence: no pending editable state; page is mostly read-only. Persistent/remote effect is cache flush through `FlushVolume`.

Dependencies/integration: relies on `gui2fs` functions (`GetCellName`, `GetServer`, `GetVolumeInfo`, `GetServers`, `FlushVolume`), MFC, `shlwapi`, and resource IDs.

Risks: partition percentage divides by `m_nPartSize` without guarding zero. If `GetVolumeInfo` fails, partially initialized `volInfo` fields must be safe. Multi-selection uses only first filename.

Test signals: normal volume info, quota unlimited, zero partition size, mountpoint follow/non-follow behavior, multiple servers list formatting, `GetVolumeInfo` failure message, and flush-volume command.
