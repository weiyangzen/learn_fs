# sources/cloud-native/moby/daemon/internal/capabilities/caps.go

## Purpose
Provides a tiny generic capability matching helper.

## APIs, Control Flow, and Integration
`Set` is `map[string]struct{}`. `Match(caps [][]string)` treats the input as OR-of-AND capability requirements, scanning in order and returning the first AND-list fully contained in the set. A nil set returns nil. If no list matches, it returns nil; an empty inner list matches immediately.

## State, Dependencies, and Risks
No persistence and no imports. Risks are semantic: nil also means no match, while an empty returned slice means a deliberately empty requirement matched. Callers must distinguish nil from empty when needed. Tests cover matching, ordering, empty lists, and non-matches.
