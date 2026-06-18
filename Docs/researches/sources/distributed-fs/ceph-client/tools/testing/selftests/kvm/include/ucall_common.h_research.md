# Research: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/ucall_common.h

# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/ucall_common.h

Purpose: architecture-neutral guest-to-host ucall framework. It defines common ucall commands, payload layout, guest assertion/printf/done/sync helpers, and host-side retrieval APIs.

Important APIs/types/functions: commands `UCALL_NONE`, `UCALL_SYNC`, `UCALL_ABORT`, `UCALL_PRINTF`, `UCALL_DONE`, `UCALL_UNHANDLED`, `UCALL_MAX_ARGS`, `UCALL_BUFFER_LEN`, `struct ucall`, and common macros/functions for `GUEST_SYNC`, `GUEST_DONE`, `GUEST_ASSERT`, guest abort/printf, ucall initialization, and host-side ucall retrieval.

Control flow and state: guest code fills a `struct ucall` with command, args, and optional text, then calls the architecture adapter from `ucall.h`. Host code observes the configured exit reason, maps the guest payload, and dispatches on `cmd`. State is transient per ucall plus architecture-specific transport setup such as MMIO address.

Dependencies and integration: includes `test_util.h` and architecture `ucall.h`. It is used by nearly all guest-running KVM selftests as the common control channel.

Risks: payload layout is shared across guest and host; changing it requires synchronized decoder updates. Buffer length caps can truncate guest printf. Tests must handle `UCALL_ABORT` and `UCALL_UNHANDLED` distinctly from normal completion.

Test signals: every guest assertion, sync, printf, and done event validates this layer. Unexpected exit reason, invalid command, or malformed payload is the typical failure mode.
