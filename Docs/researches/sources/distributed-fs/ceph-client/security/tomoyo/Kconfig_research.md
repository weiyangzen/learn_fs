# sources/distributed-fs/ceph-client/security/tomoyo/Kconfig

## Purpose

This Kconfig file declares the build-time configuration surface for the TOMOYO Linux security module. It enables TOMOYO itself and exposes defaults controlling learning-mode policy growth, audit log buffering, userspace policy-loader behavior, activation trigger path, and an insecure fuzzing-only built-in setup.

## Important APIs, types, and functions

The primary symbol is `SECURITY_TOMOYO`, a boolean that depends on `SECURITY` and `NET` and selects `SECURITYFS`, `SECURITY_PATH`, and `SECURITY_NETWORK`. Supporting symbols are `SECURITY_TOMOYO_MAX_ACCEPT_ENTRY`, `SECURITY_TOMOYO_MAX_AUDIT_LOG`, `SECURITY_TOMOYO_OMIT_USERSPACE_LOADER`, `SECURITY_TOMOYO_POLICY_LOADER`, `SECURITY_TOMOYO_ACTIVATION_TRIGGER`, and `SECURITY_TOMOYO_INSECURE_BUILTIN_SETTING`.

## Control flow

There is no runtime control flow in this file. Kconfig dependency resolution controls which TOMOYO code is compiled and which constants become available to C sources. If TOMOYO is enabled, securityfs/path/network hooks are selected. If the userspace loader is not omitted, path strings for the loader and activation trigger are configurable and can be overridden later via kernel command line options. The insecure built-in setting selects loader omission and is intended only for fuzzing kernels.

## State and persistence behavior

The file defines persistent kernel configuration state. Integer defaults become compile-time defaults for TOMOYO learning and audit queues. String defaults become built-in fallback paths for policy loading. These settings persist for the built kernel image and influence boot-time TOMOYO behavior before userspace policy is loaded.

## Dependencies and integration points

It integrates with the Linux security subsystem through `SECURITY`, `SECURITYFS`, `SECURITY_PATH`, and `SECURITY_NETWORK`, and with TOMOYO C sources that read the configured maximum learning entries, audit log count, loader path, trigger path, and insecure built-in policy mode. The help text points administrators to TOMOYO userspace tooling and documents kernel command-line overrides.

## Risks and test signals

Risks are configuration skew and unsafe defaults in specialized builds. Disabling the loader changes when policy becomes active; insecure built-in mode deliberately disables important runtime checks and must not appear in production kernels. Test signals are Kconfig dependency tests, build coverage with TOMOYO enabled/disabled, boot tests for loader and omit-loader paths, verification that audit log limits match `SECURITY_TOMOYO_MAX_AUDIT_LOG`, and fuzzing builds that intentionally enable `SECURITY_TOMOYO_INSECURE_BUILTIN_SETTING`.
