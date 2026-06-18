<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/parser.cc -->
# sources/distributed-fs/lizardfs/src/common/parser.cc

## Purpose
Implements a small string parser with position tracking and consume-by-size/string/type-predicate operations. The source was read completely for this report.

## Important APIs, Types, And Functions
`Parser` constructor/destructor, `consume(size_t)`, `consume(std::string)`, `consume(TypeCheckFunction)`, `checkState`, and `getLastConsumedCharacterCount` are implemented.

## Control Flow
Consumes update `previousPosition_` and `position_` after validating availability and match. Predicate consume advances while the type-check function accepts characters and fails if no characters matched.

## State And Persistence Behavior
State is the input string and current/previous positions. No persistence.

## Dependencies And Integration Points
Used as a base helper for typed parsers; depends only on standard string utilities.

## Risks And Edge Cases
Predicate consume calls `data_.at(newPosition)` without checking `newPosition < size` inside the loop, so a predicate that stays true through the final character can throw out_of_range. Number helpers in the header check `number.at(0)` rather than the requested position.

## Test Signals
Needs tests for end-of-string predicate consumes, no-match cases, and numeric conversion boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/parser.cc -->
