# sources/cloud-native/moby/daemon/graphdriver/errors.go

Purpose: shared unsupported/prerequisite error taxonomy for graphdriver selection.

Important APIs and control flow: constants `ErrNotSupported`, `ErrPrerequisites`, and `ErrIncompatibleFS` are `NotSupportedError` values. `ErrUnSupported` is an interface with marker method `NotSupported`. `NotSupportedError` implements `Error` and `NotSupported`. `IsDriverNotSupported` returns true when the direct error value implements `ErrUnSupported`.

State, dependencies, and risks: no state or external dependencies. The integration point is `graphdriver.New`, which skips drivers whose init error is recognized as unsupported but returns other errors. A risk is that `IsDriverNotSupported` uses a direct type switch and does not unwrap wrapped errors, so drivers must return marker errors directly or risk aborting selection. No direct tests in this group cover wrapping behavior.
