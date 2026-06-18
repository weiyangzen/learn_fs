# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/Makefile

Purpose: this top-level KVM selftests makefile selects supported architectures and delegates the real build to `Makefile.kvm`.

Important APIs and variables: `top_srcdir = ../../../..`, `include $(top_srcdir)/scripts/subarch.include`, `ARCH ?= $(SUBARCH)`, an `ifeq` filter for `arm64 s390 riscv x86 x86_64 loongarch`, a compatibility rewrite from `x86_64` to `x86`, and `include Makefile.kvm`. Unsupported architectures get empty `all` and `clean` targets.

Control flow: make determines `ARCH`, normalizes x86_64 to x86, and includes the shared KVM selftest rules only when the architecture is supported. Otherwise the targets are no-ops, allowing top-level selftest builds to proceed without hard failure on unsupported hosts.

State and persistence: no direct file state is created in this makefile. Build artifacts and generated test binaries are controlled by `Makefile.kvm` and lower-level rules.

Dependencies and integration points: integrates with kernel scripts/subarch detection, top-level selftests make recursion, and architecture-specific KVM selftest source lists in `Makefile.kvm`.

Risks: architecture normalization is required because the top-level selftests interface may pass `ARCH=x86_64`, while KVM selftests expect `x86`. Adding a supported architecture requires updating this filter and the delegated build rules. Unsupported architectures silently no-op, which is intentional but can hide misconfigured builds.

Test signals: on supported architectures the presence and result of `Makefile.kvm` targets are the signal; on unsupported architectures successful no-op `all`/`clean` confirms graceful exclusion.
