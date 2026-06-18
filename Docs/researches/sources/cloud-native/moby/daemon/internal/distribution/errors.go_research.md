# sources/cloud-native/moby/daemon/internal/distribution/errors.go

## Purpose
Normalizes registry/pull/push errors into daemon error classes and controls retry/fallback behavior.

## APIs, Control Flow, and Integration
`fallbackError` marks endpoint fallback eligibility and TLS transport success. `notFoundError`, `unsupportedMediaTypeError`, AI model, invalid manifest class/format, reserved name, and invalid argument types implement daemon error interfaces. `translatePullError` maps registry errcodes to not-found/unauthorized/unknown. `continueOnError` decides endpoint fallback, especially for mirrors and transport errors. `retryOnError` wraps non-retryable transfer failures in `xfer.DoNotRetry`. `DeprecatedSchema1ImageError` emits the removal message.

## State, Dependencies, and Risks
No persistence. Risks include string matching `ESRCH`/`ENOSPC`, taking first error from `errcode.Errors`, and nuanced differences between retry and endpoint fallback. Tests focus on `continueOnError`; most translation behavior is integration-tested through pull/push.
