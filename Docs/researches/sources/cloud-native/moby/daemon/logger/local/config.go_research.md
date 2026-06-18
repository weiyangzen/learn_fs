# sources/cloud-native/moby/daemon/logger/local/config.go

Purpose: parses and validates local logger rotation/compression config.

Important APIs/types/functions: `CreateConfig`, `newConfig`, and `validateConfig`. Defaults are defined in `local.go`.

Control flow/state/persistence: `newConfig` starts from defaults, parses `max-size`, `max-file`, and `compress`, then validates non-negative size/count and disallows compression when max file count is 1 or less.

Dependencies/integration: uses go-units and strconv; called by `local.New`.

Risks: `max-size` can be zero, effectively rotating before writes depending on `LogFile` capacity logic. Compression constraints differ from json-file because local defaults enable compression with multiple files.

Test signals: local logger tests cover option behavior through `New`.
