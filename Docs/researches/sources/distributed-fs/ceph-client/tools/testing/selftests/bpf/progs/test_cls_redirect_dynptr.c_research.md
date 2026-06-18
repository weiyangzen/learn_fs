<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_cls_redirect_dynptr.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_cls_redirect_dynptr.c

Purpose: Dynptr-based variant of the Cloudflare TC redirect classifier.

Important APIs/types/functions: Defines metrics map and functions paralleling `test_cls_redirect.c`, but uses dynptr packet access and `iphdr_info` helpers where appropriate.

Control flow: Control flow matches the non-dynptr classifier: parse, classify, accept/drop, encapsulate, redirect, and update metrics.

State and persistence: Persistent state is `metrics_map`; packet mutations happen through dynptr/skb helpers.

Dependencies and integration: Depends on dynptr support in skb/tc context, checksum helpers, and shared GRE/GUE header definitions.

Risks: Dynptr bounds, packet mutation invalidation, and parity with direct-access implementation are risks.

Test signals: Tests compare verdicts, metrics, and packet bytes against the non-dynptr classifier.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_cls_redirect_dynptr.c -->
