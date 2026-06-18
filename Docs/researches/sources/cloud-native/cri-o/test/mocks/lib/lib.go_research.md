# sources/cloud-native/cri-o/test/mocks/lib/lib.go

## Purpose
Generated GoMock for `pkg/config.Iface`.

## Important APIs, Types, And Functions
`MockIface` provides `GetData()` and `GetStore()` mock methods plus recorder helpers.

## Control Flow
Methods delegate to GoMock and return configured config/store values.

## State And Persistence
No persistence. It supplies test-controlled config and storage handles.

## Dependencies And Integration Points
The server constructor tests use this as the main dependency injection point for CRI-O config and storage store access.

## Risks And Test Signals
Very small interface mock; failures usually mean constructor call-order or config access changed.
