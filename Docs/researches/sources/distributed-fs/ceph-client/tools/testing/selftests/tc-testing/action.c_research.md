# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/action.c

## Purpose
Defines two tiny eBPF programs used by tc BPF action tests.

## Important APIs, Types, And Functions
`action_ok()` is placed in ELF section `action-ok` and returns `TC_ACT_OK`. `action_ko()` is placed in `action-ko`, writes `0` to `skb->data`, and returns `TC_ACT_OK`. `_license` is placed in the `license` section as `"GPL"`.

## Control Flow
The compiled object is loaded by `tc action bpf object-file ... section action-ok/action-ko`. The valid action returns OK without modifying the packet; the invalid one performs a verifier-hostile write to skb metadata.

## State And Persistence
No userspace state. Loaded eBPF program state is kernel-managed by tc/BPF.

## Dependencies And Integration Points
Depends on `<linux/bpf.h>` and `<linux/pkt_cls.h>`, and integrates with `bpf.json` tests through `$EBPFDIR/action-ebpf`.

## Risks
The intentionally invalid program must remain rejected by the verifier; verifier behavior changes could alter expected tc exit codes. Build flags outside this file determine whether sections and license are preserved.

## Test Signals
`bpf.json` should accept `action-ok`, reject or not install `action-ko`, and show expected action metadata in `tc action get`.
