<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/progress/bar.go -->
# sources/cloud-native/containerd/pkg/progress/bar.go

## Purpose
Implements a simple fmt.Formatter-backed terminal progress bar rendered by the custom %r verb.

## Important APIs, Types, And Functions
Bar is a float64 progress ratio; Format clamps the value to [0,1], honors the left/right reversal flag, chooses a default width of 40, and emits colored plus/minus segments bounded by vertical bars.

## Control Flow
fmt calls Format with the requested rune. The code rejects non-r verbs by panic, computes filled and empty width, inserts ANSI green/reset escape sequences, and writes directly to fmt.State.

## State And Persistence
No persistent state. Output is derived entirely from the receiver and fmt formatting state.

## Dependencies And Integration Points
Depends on bytes, fmt, and escape constants from escape.go. Used by progress displays that rely on terminal ANSI colors.

## Risks And Edge Cases
Panicking on unexpected verbs is intentional but can surprise generic formatting. Width calculations count escape bytes separately to keep visible width stable, but terminal color support is assumed.

## Test Signals
No local test in this subset; coverage is indirect through callers or manual formatting behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/progress/bar.go -->
