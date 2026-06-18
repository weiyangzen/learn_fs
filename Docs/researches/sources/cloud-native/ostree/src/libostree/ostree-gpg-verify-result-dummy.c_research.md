# sources/cloud-native/ostree/src/libostree/ostree-gpg-verify-result-dummy.c

## Purpose
This file provides ABI-compatible dummy `OstreeGpgVerifyResult` functions for builds compiled with GPGME support disabled.

## Important APIs, Types, And Functions
It defines a minimal `OstreeGpgVerifyResult` GObject implementing `GInitable` without real initialization. Public result APIs log critical messages and return empty/false/NULL values. `ostree_gpg_verify_result_require_valid_signature()` returns `G_IO_ERROR_NOT_SUPPORTED`. `ostree_gpg_verify_result_describe_variant()` validates the expected full-result tuple type and appends a disabled-feature message if called with a valid variant. It also defines the `OstreeGpgError` quark.

## Control Flow, State, And Persistence
There is no verification state. The dummy implementation preserves symbols so callers can link, but any real GPG inspection fails explicitly at runtime.

## Dependencies And Integration Points
It includes public `ostree-gpg-verify-result.h` and must only compile when `OSTREE_DISABLE_GPGME` is defined. It substitutes for the real result implementation in no-GPG builds.

## Risks And Test Signals
Callers must handle disabled GPG as unsupported, not as a valid signature absence unless that is intended. `ostree_gpg_verify_result_describe()` calls `get_all()` after logging, which returns `NULL`; downstream `describe_variant()` has `g_return_if_fail`. Tests should cover no-GPG build behavior, error code from `require_valid_signature()`, critical logging expectations, and symbol availability.
