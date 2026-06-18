<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/media_label.cc -->
# sources/distributed-fs/lizardfs/src/common/media_label.cc

## Purpose
Implements global string-to-16-bit-handle interning for chunk media labels and validation rules. The source was read completely for this report.

## Important APIs, Types, And Functions
`MediaLabelManager::iGetHandle`, `iGetLabel`, `isLabelValid`, wildcard constants, and `MediaLabel::kWildcard` are implemented.

## Control Flow
The manager initializes wildcard `_` to max handle. New labels receive monotonically increasing handles starting at 1, with rollback if reverse-map insertion fails. Label lookup by handle throws on invalid handle.

## State And Persistence Behavior
State is a function-local static manager containing two unordered maps and the next handle. No disk persistence, but handles may be serialized by callers.

## Dependencies And Integration Points
Integrates with chunk part/media label placement algorithms; uses `<cctype>` style `isalnum` through included headers.

## Risks And Edge Cases
The singleton maps are not synchronized, so concurrent first-use/new-label registration can race. `isLabelValid` should cast to unsigned char before `isalnum` for non-ASCII safety.

## Test Signals
`media_label_unittest.cc` covers validation, handle round trips, wildcard, and invalid handles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/media_label.cc -->
