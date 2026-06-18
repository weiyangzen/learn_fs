<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_select_reuseport_common.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_select_reuseport_common.h

## Purpose
This header defines shared constants and wire/data structures for reuseport selection tests. It is consumed by user-space and BPF-side code to agree on test outcomes, control commands, and packet metadata validation fields.

## Important APIs, Types, And Functions
- `enum result` names BPF/user-visible outcomes such as inner-map failure, skb data failure, selection failure, miscellaneous drop, pass, and pass-with-select failure.
- `struct cmd` carries `reuseport_index` and `pass_on_failure` settings into a BPF map or test command path.
- `struct data_check` stores expected IP protocol, skb addresses, ports, Ethernet protocol, bind-in-any flag, length, and hash. The zero-length `equal_check_end` marker separates fields that should be compared for equality from trailing metadata.

## Control Flow
The header has no executable control flow. Test programs populate `struct cmd` to drive selection behavior and compare populated `struct data_check` data against observed skb metadata to decide which `enum result` bucket is incremented.

## State And Persistence
No storage is defined here. State persists only when these structures are embedded in BPF maps or user-space test buffers.

## Dependencies And Integration Points
It depends only on `<linux/types.h>` and integrates with select-reuseport BPF programs and user-space harnesses elsewhere in the BPF selftest tree.

## Risks And Edge Cases
Layout is part of the ABI between BPF and user space; reordering fields, changing widths, or moving `equal_check_end` can silently break map value comparisons. Address array sizing must match IPv4/IPv6 expectations in consuming tests.

## Test Signals
Failures show up as mismatched result counters or data-check comparisons in reuseport tests, commonly mapped to `DROP_ERR_*` or `PASS_ERR_SK_SELECT_REUSEPORT`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_select_reuseport_common.h -->
