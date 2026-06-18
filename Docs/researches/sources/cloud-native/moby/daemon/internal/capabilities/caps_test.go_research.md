# sources/cloud-native/moby/daemon/internal/capabilities/caps_test.go

## Purpose
Validates OR-of-AND capability matching semantics.

## APIs, Control Flow, and Integration
`TestMatch` builds a set containing `foo` and `bar`, then table-tests empty AND-list match, single capability matches, first-match ordering, multi-capability AND matches, fallback to later OR entries, and several non-match cases. It compares returned slice length and values in order.

## State, Dependencies, and Risks
No external state. The tests document the important nil-versus-empty distinction and ordered selection behavior. They do not exercise nil `Set`; production code explicitly returns nil for that.
