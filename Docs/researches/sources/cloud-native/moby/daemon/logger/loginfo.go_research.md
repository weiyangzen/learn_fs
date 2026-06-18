# sources/cloud-native/moby/daemon/logger/loginfo.go

Purpose: holds per-container context passed to logging drivers and helper methods for metadata extraction.

Important APIs/types/functions: `Info`, attr option constants, `ExtraAttributes`, `Hostname`, `Command`, `ID`, `FullID`, `Name`, `ImageID`, `ImageFullID`, and `ImageName`.

Control flow/state/persistence: `ExtraAttributes` builds a new map from selected labels and env vars using explicit comma lists and regex filters, optionally modifying keys through a driver-supplied function. Other methods normalize/truncate container and image fields for templates.

Dependencies/integration: used by every driver at construction time and by `loggerutils.ParseLogTag`.

Risks: regex compilation errors abort logger creation. Duplicate keys after key modification overwrite previous attrs. Env parsing ignores entries without `=`.

Test signals: log tag tests and driver attr tests cover common metadata extraction.
