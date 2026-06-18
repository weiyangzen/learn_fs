# sources/distributed-fs/ceph-client/rust/helpers/security.c

## Purpose
Exposes LSM/security hook stubs to Rust when full security hooks are not configured.

## APIs, Types, and Functions
Under `!CONFIG_SECURITY`, wraps credential secid lookup, secid-to-secctx conversion, secctx release, and Binder-specific LSM hooks for context manager, transaction, binder transfer, and file transfer.

## Control Flow, State, and Persistence
State is in security subsystem contexts and caller-managed `lsm_context` storage; helpers keep no local state.

## Dependencies and Integration
Depends on `linux/security.h`, LSM configuration, credentials, files, and Binder Rust integration.

## Risks and Test Signals
Risks include config-dependent no-op/security behavior, secctx lifetime leaks, and Binder permission checks diverging across configs. Test signals are Binder security tests, LSM-enabled/disabled builds, and secctx conversion/release coverage.
