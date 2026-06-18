# sources/distributed-fs/beegfs-go/ctl/internal/cmdfmt/fmt.go

Purpose: provides the command output abstraction used for structured table, JSON, pretty JSON, and NDJSON rendering.

Important APIs/types/functions: `Printf` writes diagnostic text to stderr; `Printer` abstracts table/JSON renderers; `Printomatic` tracks columns, selected columns, page size, output type, and row count; `NewPrintomatic`; `WithEmptyColumns`; `replacePrinter`; `AddItem`; `PrintRemaining`.

Control flow: construction reads Viper global output, columns, debug/page-size settings indirectly through config keys, normalizes spaces in column names to underscores, selects a JSON printer or go-pretty table, hides unselected columns with `table.ColumnConfig`, and prints when page size is zero or reached. JSON with page size zero becomes NDJSON.

State and persistence: no persistence. Per-instance state buffers rows until page flush. Output configuration is global through Viper.

Dependencies and integration points: central integration point for all CLI commands that emit structured output. Depends on go-pretty table/text, Viper, and `ctl/pkg/config` output constants.

Risks: `AddItem` assumes row width matches configured columns; JSON printer panics on mismatch. `NewPrintomatic` mutates the input `columns` and `defaultColumns` slices in place while replacing spaces, so callers reusing those slices may observe changes. Sorting is mentioned in comments but not implemented here. Mixed stderr/stdout behavior matters for scripts.

Test signals: no direct tests in this work item. High-value tests include column selection, all-columns/debug behavior, page-size zero table/NDJSON semantics, empty-column suppression, and mismatch panics.
