# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool.d/defect

Symlink to `smart`; behavior is selected by invoked basename `defect`.

Behavior:
- Parses SMART/SAS output from `smartctl -a`.
- Extracts `Elements in grown defect list` into `defect=<value>`.
- Returns an empty `defect=` field if not available.

Role:
- Provides a SAS-focused custom column for grown defect list size.
