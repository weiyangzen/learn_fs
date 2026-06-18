<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/case_sensitivity.h -->
# sources/distributed-fs/lizardfs/src/common/case_sensitivity.h

## Purpose

This header defines a small enum for APIs that need to choose case-sensitive or case-insensitive behavior.

## Important APIs, Types, and Functions

`enum class CaseSensitivity` has `kIgnore` and `kSensitive`.

## Control Flow

There is no executable control flow.

## State and Persistence Behavior

The enum is value state only. No serialization helpers are declared here.

## Dependencies and Integration Points

It includes `common/platform.h`. Path/name matching code can use this type to avoid boolean ambiguity.

## Risks and Edge Cases

Because no serialization or parsing helpers are present, each caller must define its own external representation if needed.

## Test Signals

Compile coverage of case-sensitivity-aware callers is the relevant signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/case_sensitivity.h -->
