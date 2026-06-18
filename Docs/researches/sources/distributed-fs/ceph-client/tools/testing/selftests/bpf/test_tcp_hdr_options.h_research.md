<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_tcp_hdr_options.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_tcp_hdr_options.h

## Purpose
This header provides shared structures, constants, and BPF-side helpers for tests that parse and write experimental TCP header options from `BPF_PROG_TYPE_SOCK_OPS` programs.

## Important APIs, Types, And Functions
- `struct bpf_test_option` is the packed experimental option payload containing flags, max delayed-ACK value, and random byte.
- `OPTION_*` enums and `OPTION_F_*` macros define resend, max-delack, and random test flags.
- `struct hdr_stg` stores per-socket state in `bpf_sk_storage`.
- `struct linum_err` records source line and error code for a local port in `lport_linum_map`.
- TCP flag and option constants define expected header encodings.
- Under `BPF_PROG_TEST_TCP_HDR_OPTIONS`, BPF map `lport_linum_map`, `tcp_hdrlen()`, `skops_tcp_flags()`, callback-flag setters/clearers, and `RET_CG_ERR()` are compiled for BPF programs.

## Control Flow
The header has no standalone entry point. BPF sockops programs include it to enable parse/write header callbacks, inspect `skb_tcp_flags`, update callback flags on `struct bpf_sock_ops`, and return `CG_ERR` through `RET_CG_ERR()` while recording line-specific diagnostics.

## State And Persistence
Shared state lives in BPF maps and socket storage created by consuming programs. `RET_CG_ERR()` persists the first error per local port with `BPF_NOEXIST` and clears header callback flags to avoid repeated processing after an error.

## Dependencies And Integration Points
It depends on BPF sockops context definitions, `SEC(".maps")`, `bpf_map_update_elem()`, `bpf_sock_ops_cb_flags_set()`, and TCP option layout shared with user-space validators.

## Risks And Edge Cases
The packed structs and max header constants must match kernel TCP option limits. Callback flag handling is delicate; leaving parse/write flags enabled after an error can cause noisy follow-on failures. `RET_CG_ERR()` assumes a `skops` variable is in scope.

## Test Signals
Consumers validate map entries, line numbers, and TCP option effects. Failures typically show incorrect option bytes, missing callback invocation, unexpected `CG_ERR`, or entries in `lport_linum_map`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_tcp_hdr_options.h -->
