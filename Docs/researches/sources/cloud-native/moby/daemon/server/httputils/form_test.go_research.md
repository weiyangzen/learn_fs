# sources/cloud-native/moby/daemon/server/httputils/form_test.go

## Purpose
Tests HTTP form helper parsing for booleans, int64s, uint32s, and OCI platform JSON.

## Important APIs, Types, And Functions
Tests call `BoolValue`, `BoolValueOrDefault`, `Int64ValueOrZero`, `Int64ValueOrDefault`, `Uint32Value`, and `DecodePlatform`.

## Control Flow
Table tests populate `http.Request.Form` values and assert parsed values or error categories. Platform tests cover empty, non-JSON, malformed JSON, missing OS/architecture, optional-only fields, and a valid platform.

## State And Persistence
Only local request form maps are mutated. No network or disk state is involved.

## Dependencies And Integration Points
Uses containerd errdefs, OCI platform types, and gotest assertions. It guards parser behavior used by routes such as resize and create.

## Risks And Edge Cases
The uint32 test checks that negative values return `strconv.ErrRange`, while absent or empty values return syntax errors. Platform tests distinguish optional-only payload errors from missing required field errors.

## Test Signals
Failures indicate request compatibility changes in common API parsers.
