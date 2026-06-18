# sources/distributed-fs/beegfs-go/ctl/internal/util/flags.go

Purpose: provides reusable pflag values for human-readable byte sizes, constrained string choices, and remote target ID lists.

Important APIs/types/functions: `I64BytesVar`; `i64BytesFlag`; `ValidatedStringFlag`; `validatedStringFlag`; `NewRemoteTargetsFlag`; `rstsFlag`.

Control flow: byte-size flags parse defaults and user values through `ParseIntFromStr` and reject values above `math.MaxInt64`. Validated strings lowercase input and compare against allowed `fmt.Stringer` values. RST flags accept `none` as an empty configured list or comma-separated nonzero unique uint32 IDs.

State and persistence: flag values write to caller-provided pointers. No persistence.

Dependencies and integration points: integrates pflag and parser utilities; used by global output flags and Remote target selection.

Risks: `i64BytesFlag.String` returns the default text, not the current parsed value, which may surprise generic flag display. RST `String` returns "unchanged" for nil and empty slices, while `Set("none")` semantically means changed-to-empty. `ValidatedStringFlag` stores the `fmt.Stringer` object from the allowed slice.

Test signals: no direct tests for this file. Parser tests indirectly validate byte parsing. Useful flag tests would cover current-value display, duplicate RST IDs, zero ID rejection, `none`, and case-insensitive string validation.
