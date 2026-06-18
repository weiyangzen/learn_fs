# sources/cloud-native/moby/internal/sliceutil/sliceutil_test.go

## Purpose
Unit tests for slice mapping helpers.

## Important APIs, Types, And Functions
- `TestMap` doubles integers and verifies nil input returns nil while empty input returns non-nil empty output.
- `TestMap_TypeConvert` maps integers to strings.
- `TestMapper` builds a reusable `netip.MustParseAddr` mapper and tests normal, nil, and empty inputs.

## Control Flow
Tests call `sliceutil.Map` or a `Mapper` closure, compare lengths and values, and use ordinary `testing` failures.

## State And Persistence
Only local slices and parsed addresses are used.

## Dependencies And Integration Points
Imports the package as `sliceutil_test`, so it exercises only exported API. Uses `net/netip` and `strconv`.

## Risks And Edge Cases
Tests do not cover `Deref` or `Dedup`, so those helpers rely on indirect or absent coverage here. Mapper panic behavior for invalid addresses is not covered.

## Test Signals
Passing confirms `Map` and `Mapper` preserve length, support output type conversion, and preserve the nil-versus-empty distinction.
