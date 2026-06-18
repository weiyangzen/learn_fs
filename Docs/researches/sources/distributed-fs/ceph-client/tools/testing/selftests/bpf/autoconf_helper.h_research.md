# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/autoconf_helper.h

## Purpose

This header supplies a small compatibility bridge for generated kernel configuration. If `HAVE_GENHDR` is set it includes generated `autoconf.h`; otherwise it defines `CONFIG_HAVE_EFFICIENT_UNALIGNED_ACCESS` for common architectures.

## Important APIs, Types, and Functions

The only exported behavior is conditional preprocessing around `HAVE_GENHDR` and fallback architecture checks for x86, s390x, and aarch64.

## Control Flow and Data Flow

There is no runtime flow. Preprocessor state determines whether tests see kernel config definitions from the build tree or the fallback unaligned-access capability.

## State and Persistence Behavior

No runtime state exists.

## Dependencies and Integration Points

It is included by BPF selftest sources needing config-sensitive behavior while still being buildable outside a full generated-header environment.

## Risks and Edge Cases

The fallback covers only selected architectures and only one config symbol. Architectures with efficient unaligned access but not listed may compile conservative paths.

## Test Signals

Compilation both with and without `include/generated/autoconf.h` validates this helper.
