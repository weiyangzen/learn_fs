## sources/distributed-fs/lizardfs/src/mount/sugid_clear_mode_string.h

Purpose: small helper converting `SugidClearMode` enum values to uppercase diagnostic strings.

Important API: `sugidClearModeString(SugidClearMode mode)` returns `NEVER`, `ALWAYS`, `OSX`, `BSD`, `EXT`, `XFS`, or `???` for out-of-range values.

Dependencies and integration: includes `protocol/MFSCommunication.h` for the enum. Useful for logs/config displays.

Risks and tests: array order must match enum numeric order. A simple enum-coverage test should pin every expected string and invalid fallback.
