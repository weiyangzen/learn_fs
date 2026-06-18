<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/spdk/crc_internal.h -->
# sources/distributed-fs/ceph/src/rgw/spdk/crc_internal.h

Purpose: Provides compile-time feature detection for optional CRC acceleration backends in the vendored SPDK CRC code.

Important APIs, types, and functions: Defines `SPDK_HAVE_ISAL` when `SPDK_CONFIG_ISAL` is set, `SPDK_HAVE_ARM_CRC` on ARMv8 CRC-capable builds, and `SPDK_HAVE_SSE4_2` on x86_64 SSE4.2 builds. It includes the associated ISA-L, ARM ACLE, or x86 intrinsics headers.

Control flow: Included before CRC implementation code so compile-time macros select optimized or fallback implementations.

State and persistence: No state or persistence.

Dependencies and integration points: Depends on compiler target macros and optional external ISA-L headers. Original SPDK config include is disabled in this local copy.

Risks and test signals: Incorrect feature macros can break cross-compiles or include unavailable intrinsic headers. Build matrix should cover x86_64, aarch64, ISA-L enabled/disabled, and fallback builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/spdk/crc_internal.h -->
