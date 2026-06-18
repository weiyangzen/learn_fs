# sources/distributed-fs/ceph-client/net/xfrm/xfrm_state_bpf.c

## Purpose

`xfrm_state_bpf.c` exposes unstable BPF kfuncs that let XDP programs look up an XFRM state by mark, destination address, SPI, protocol, address family, and network namespace, then release the acquired state reference. The file is intentionally marked unstable, so compatibility can change.

## Important APIs, Types, and Functions

`struct bpf_xfrm_state_opts` is the BPF-visible options structure. It contains an `error` out parameter, `netns_id`, mark, destination address, SPI, protocol, and family. `BPF_XFRM_STATE_OPTS_SZ` fixes the expected size.

`bpf_xdp_get_xfrm_state()` validates `opts__sz`, validates `netns_id`, resolves either the current XDP device namespace or a namespace by ID, calls `xfrm_state_lookup()`, drops the namespace reference when needed, sets `opts->error` on failures, and returns a referenced `struct xfrm_state *` or NULL.

`bpf_xdp_xfrm_state_release()` releases a state returned by the lookup helper using `xfrm_state_put()`. The BTF kfunc set marks lookup as `KF_RET_NULL | KF_ACQUIRE` and release as `KF_RELEASE`. `register_xfrm_state_bpf()` registers the kfunc ID set for `BPF_PROG_TYPE_XDP`.

## Control Flow

At XFRM global initialization, `xfrm_init()` calls `register_xfrm_state_bpf()`. Later, verified XDP programs can call `bpf_xdp_get_xfrm_state()`. The helper derives the current netns from `xdp->rxq->dev`, optionally switches to a namespace ID, performs the SAD lookup, and returns with a held state reference. The verifier requires that all acquired references are released by `bpf_xdp_xfrm_state_release()`.

## State and Persistence Behavior

The file does not create persistent XFRM state. Its main state effect is reference ownership: successful lookup increments an XFRM state refcount via `xfrm_state_lookup()`, and release decrements it. Errors are communicated through the caller-provided `opts->error` field.

## Dependencies and Integration Points

Dependencies include BPF kfunc infrastructure, BTF IDs, XDP context internals, net namespace lookup by ID, and the exported `xfrm_state_lookup()` API from `xfrm_state.c`. It is registered from the XFRM init path in `xfrm_policy.c`.

## Risks and Edge Cases

The ABI is size-sensitive. The helper permits only the exact options size after confirming that the `error` field is writable; mismatched sizes return `-EINVAL`. Namespace ID handling must drop references on all paths after `get_net_ns_by_id()`. Because the returned pointer is a live kernel object, verifier acquire/release annotations are essential to prevent leaks.

Lookup semantics mirror SAD lookup and do not check policy authorization by themselves. XDP programs using this helper must treat a found SA as state information, not as a complete policy decision.

## Test Signals

BPF selftests should load XDP programs that call lookup and release on existing and missing SAs, pass current netns and explicit netns IDs, test invalid `opts__sz` and `netns_id`, and verify the verifier rejects paths that leak acquired state references. Runtime signals include expected `opts->error` values `-EINVAL`, `-ENONET`, and `-ENOENT`.
