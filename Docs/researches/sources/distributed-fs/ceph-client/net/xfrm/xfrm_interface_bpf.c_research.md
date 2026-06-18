# sources/distributed-fs/ceph-client/net/xfrm/xfrm_interface_bpf.c

Purpose: `xfrm_interface_bpf.c` exposes unstable TC-BPF kfuncs for reading and writing XFRM metadata on skbs. It supports xfrm interfaces in collect-metadata mode, letting BPF programs steer packets by `if_id` and underlying link.

Important APIs: `struct bpf_xfrm_info` contains `if_id` and `link`. `bpf_skb_get_xfrm_info()` copies metadata from `skb_xfrm_md_info()` into BPF-provided memory. `bpf_skb_set_xfrm_info()` allocates or reuses a per-CPU `METADATA_XFRM` destination, stores metadata and original dst, and replaces `skb_dst`. `register_xfrm_interface_bpf()` registers the kfunc set for `BPF_PROG_TYPE_SCHED_CLS`.

Control flow: Set rejects skbs that already have metadata dst, lazily initializes `xfrm_bpf_md_dst` with `metadata_dst_alloc_percpu()` and `cmpxchg()`, uses the current CPU metadata destination, preserves original dst with a hold, and installs the metadata dst on the skb. Get fails with `-EINVAL` if no metadata exists.

State and persistence: The global per-CPU metadata dst pointer persists after first allocation. Each skb can carry temporary XFRM metadata and a held original dst until consumed by xfrm interface transmit logic.

Dependencies and integration: It depends on BTF kfunc registration, TC classifier BPF, metadata dst infrastructure, and `xfrm_interface_core.c` collect-md transmit path, which reads `skb_xfrm_md_info()`.

Risks: The interface is explicitly unstable. Incorrect dst reference handling can leak or use-after-free routes. Per-CPU metadata reuse assumes skb metadata lifetime is controlled by dst referenceing. Set rejects existing metadata to avoid overwriting unrelated tunnel metadata.

Test signals: Build with BTF/module BTF combinations, load TC-BPF programs using the kfuncs, test get-without-metadata failure, set-then-xmit on collect-md xfrm interface, original dst restoration in transmit, and verifier/BTF registration failures.
