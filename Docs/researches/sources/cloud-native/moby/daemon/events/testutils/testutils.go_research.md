# sources/cloud-native/moby/daemon/events/testutils/testutils.go

Purpose: test helper for parsing human-readable Docker event CLI output into structured `events.Message` fixtures.

Important APIs and control flow: regular-expression constants describe timestamp, event type, action, ID, and optional parenthesized attributes. `eventCliRegexp` is lazily compiled. `ScanMap` returns named capture groups for a line or an empty map on no match. `Scan` validates the line, parses the timestamp with daemon timestamp helpers, splits attributes on `", "`, splits each attribute on the first `=`, and builds an `events.Message` with `Time`, `TimeNano`, `Type`, `Action`, actor ID, and attributes.

State, dependencies, and risks: state is only the lazy regexp. Dependencies include `lazyregexp`, `timestamp.Parse`, and API event types. The parser is deliberately tailored to test fixtures, not a full CLI parser: attributes containing `, ` or `=` in values are lossy, missing attributes can produce an empty-key entry because the split loop still runs, and the regexp only accepts word-like action/type tokens. Test signal comes from event buffer tests that use historical CLI output fixtures.
