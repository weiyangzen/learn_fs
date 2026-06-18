# sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib/xdp_dummy.bpf.c

## Purpose
This is a minimal XDP BPF object used when tests need an attachable XDP program without changing packet behavior.

## Important APIs and Functions
It defines `xdp_dummy_prog` in section `xdp` and `xdp_dummy_prog_frags` in section `xdp.frags`. Both return `XDP_PASS`. `_license` declares GPL licensing.

## Control Flow and State
There is no map state and no branching; every packet is passed unchanged in both linear and frags-capable XDP modes.

## Dependencies and Integration
It depends on BPF helper headers and is built by `lib/Makefile`/`bpf.mk`. Tests can attach it to exercise XDP attach paths or feature negotiation without packet drops or redirects.

## Risks and Test Signals
The only realistic failures are BPF compile/load/attach failures or unsupported `xdp.frags`. Runtime pass signal is unchanged traffic through an attached XDP hook.
