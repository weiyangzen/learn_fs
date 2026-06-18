# sources/distributed-fs/beegfs-go/ctl/internal/cmdfmt/json.go

Purpose: implements the JSON/NDJSON backend for `Printomatic`.

Important APIs/types/functions: `jsonPrinter`; `newJSONPrinter`; `SetColumnConfigs`; `AppendRow`; `Render`; `printPrettyJSON`; `printJSON`.

Control flow: rows are appended as maps keyed by visible column names. `Render` emits a single row object for NDJSON (`pageSize == 0`) or an array for JSON modes, with optional indentation.

State and persistence: buffers rows in memory until rendered. No persistence.

Dependencies and integration points: implements enough of the go-pretty `Printer`-like interface to be swapped into `Printomatic`. Uses `table.ColumnConfig` for hidden/name metadata and standard `encoding/json`.

Risks: panics on row/column count mismatch or invalid NDJSON row count, intentionally treating these as programmer bugs. Map key order in JSON is handled by Go's encoder deterministically for strings today, but callers should not rely on display order semantically.

Test signals: no direct tests. Useful tests would assert hidden columns, NDJSON single-object rendering, pretty formatting, and panic conditions.
