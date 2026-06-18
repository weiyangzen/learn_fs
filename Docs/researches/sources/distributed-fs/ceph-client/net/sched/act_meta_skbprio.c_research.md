# sources/distributed-fs/ceph-client/net/sched/act_meta_skbprio.c

## Purpose

`act_meta_skbprio.c` is the IFE metadata codec for `skb->priority`. It allows traffic-control priority metadata to be exported in an IFE frame and restored on the receiving path.

## Important APIs, types, and functions

`ife_prio_ops` is the registered `struct tcf_meta_ops` with `metaid = IFE_META_PRIO`, `metatype = NLA_U32`, and name `skbprio`. `skbprio_check()` uses `ife_check_meta_u32()`, `skbprio_encode()` serializes `skb->priority` through `ife_encode_meta_u32()`, and `skbprio_decode()` writes the network-order decoded value back to `skb->priority`. The module entry points are `ifeprio_init_module()` and `ifeprio_cleanup_module()`.

## Control flow

The module participates only when the IFE action asks for `skbprio` metadata. The IFE core owns netlink parsing, metadata buffer allocation, and packet encapsulation; this file supplies the priority-specific get/check/encode/decode callbacks.

## State and persistence

There is no action instance state here. The only persistent kernel object is the globally registered metadata operations table. Runtime state is the per-packet `skb->priority`, which commonly feeds qdisc class selection and socket priority behavior after decode.

## Dependencies and integration points

The module depends on common IFE helpers from `net/tc_act/tc_ife.h` and the tc action UAPI IDs from `tc_ife.h`. It integrates with the qdisc/classifier stack through the meaning of `skb->priority`; any later classful qdisc, filter, or socket-priority logic observes the restored value.

## Risks and edge cases

The ops table omits explicit `.release` and `.validate` callbacks unlike the mark and tc_index codecs, relying on generic u32 helper behavior through `.alloc` and `.get`. The data path is small, but wrong byte order or accepting malformed metadata would cause priority/class selection drift that may be hard to detect except by observing queue placement.

## Test signals

Validate module autoload with the `skbprio` IFE metadata alias and use tc filters before and after an IFE hop to prove priority preservation. Tests should exercise zero and nonzero priorities, classful qdisc selection from restored priority, and malformed metadata rejection in the shared IFE parser.
