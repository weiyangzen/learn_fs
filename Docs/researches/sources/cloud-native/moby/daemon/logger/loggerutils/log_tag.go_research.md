# sources/cloud-native/moby/daemon/logger/loggerutils/log_tag.go

Purpose: renders configurable log tags from `logger.Info`.

Important APIs/types/functions: `DefaultTemplate`, template constants, and `ParseLogTag`.

Control flow/state/persistence: selects configured tag template or default. Fast paths handle common exact templates such as container ID, full ID, name, command, image, and hostname. Other templates are parsed and executed via logger templates.

Dependencies/integration: used by journald, json-file, local, Splunk, and other drivers for metadata/tag fields.

Risks: arbitrary templates can fail parse/execute. Hostname lookup can fail. Empty default lets drivers opt into no tag unless configured.

Test signals: `log_tag_test.go` covers zero values and supported substitutions.
