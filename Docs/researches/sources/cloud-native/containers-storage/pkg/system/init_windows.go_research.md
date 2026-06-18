# sources/cloud-native/containers-storage/pkg/system/init_windows.go

Purpose: initializes Windows LCOW support flag from the environment.

Important APIs, types, and functions: package variable `lcowSupported` and `init`.

Control flow: default is false; init sets true when environment variable `LCOW_SUPPORTED` is non-empty.

State and persistence: in-memory package-global state derived from process environment at init time.

Dependencies and integration points: depends on `os`; used by `lcow_windows.go`.

Risks and edge cases: environment is read only once at package initialization. Comment notes this was a development-era feature gate and may not reflect modern Windows capability detection.

Test signals: no direct Windows LCOW tests in requested files.
