# sources/cloud-native/moby/daemon/logger/templates/templates.go

## Purpose
This file provides reusable template helpers for logger tag formatting.

## Important APIs, Types, And Functions
`basicFunctions` exposes `json`, `split`, `join`, `title`, `lower`, `upper`, `pad`, and `truncate` to Go text templates. `NewParse(tag, format)` attaches those functions to a template and parses the format. `padWithSpace` and `truncateWithLength` implement the custom formatting helpers.

## Control Flow
Callers invoke `NewParse` with a template name and format string. The JSON helper encodes without HTML escaping and trims the encoder newline. `pad` returns the original empty string unchanged and otherwise adds requested leading/trailing spaces. `truncate` returns the original string when shorter than the requested length and byte-slices otherwise.

## State, Persistence, And Dependencies
There is no mutable state. Dependencies are standard `text/template`, `encoding/json`, `bytes`, and `strings`.

## Integration Points
Logger packages use these helpers to build configurable log tags and structured strings from container metadata.

## Risks And Edge Cases
`strings.Title` is deprecated and has Unicode boundary limitations; the code explicitly tolerates that for compatibility. `truncate` is byte-based, not rune-aware, so non-ASCII strings can be cut mid-rune. The JSON helper ignores encode errors by design.

## Test Signals
`templates_test.go` only verifies basic parse and execution; helper-specific edge cases are not directly tested here.
