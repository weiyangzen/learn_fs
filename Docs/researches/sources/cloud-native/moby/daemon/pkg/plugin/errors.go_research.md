<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/errors.go -->
# sources/cloud-native/moby/daemon/pkg/plugin/errors.go

## Purpose
Defines typed plugin errors that map to Docker API error classes.

## Important APIs, Types, And Functions
Error types include `errNotFound`, `errAmbiguous`, `errDisabled`, `inUseError`, `enabledError`, and `alreadyExistsError`. Marker methods implement `NotFound`, `InvalidParameter`, or `Conflict`.

## Control Flow
Each type formats an error string and marker methods are no-op interfaces used by error classification.

## State, Dependencies, And Integration Points
No state. These errors flow through plugin manager operations and API handlers for correct HTTP/status classification.

## Risks And Test Signals
String wording can affect tests or clients that compare messages, but the main contract is marker-interface behavior. There are no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/errors.go -->
