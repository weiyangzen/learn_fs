<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/opts/opts.go -->
# sources/cloud-native/moby/daemon/internal/opts/opts.go

Purpose: implements boolean set/map daemon options with optional names for config reflection.

Important APIs and types: `SetOpts`, `NewSetOpts`, `Set`, `GetAll`, `String`, `Type`, `NamedSetOpts`, `NewNamedSetOpts`, and `Name`.

Control flow: `Set` splits input on `=`, rejects empty keys, treats missing value as true, parses present values with `strconv.ParseBool`, and writes the map. `NewSetOpts` initializes nil maps. `NamedSetOpts` embeds `SetOpts` and implements `opts.NamedOption`.

State and persistence: mutates an in-memory map supplied by caller or created on construction.

Dependencies and integration: used by daemon config/flag parsing for named feature-like maps.

Risks: map is not synchronized; callers must serialize option parsing. String output uses Go map formatting, which is not stable for user-facing ordering.

Test signals: `opts_test.go` covers true/false syntax, missing value, errors, and named option behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/opts/opts.go -->
