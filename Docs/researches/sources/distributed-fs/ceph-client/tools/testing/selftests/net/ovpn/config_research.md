# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/config

## Purpose
The OVPN `config` file declares the kernel configuration prerequisites for running the OpenVPN data-channel accelerator selftests.

## Important settings
It requires core crypto and networking support (`CONFIG_CRYPTO`, AES, GCM, CHACHA20POLY1305, `CONFIG_INET`, `CONFIG_NET`), tunnel and netfilter support (`CONFIG_NET_UDP_TUNNEL`, `CONFIG_NETFILTER`, `CONFIG_NF_TABLES`, `CONFIG_NF_TABLES_INET`), stream parsing for TCP mode, destination cache support, and the OVPN module (`CONFIG_OVPN=m`).

## Control flow
There is no executable control flow. Kselftest tooling can use this file as a requirements manifest when evaluating whether a kernel is suitable for the test directory.

## State and persistence
No runtime state is created. The file represents build-time/kernel-capability state only.

## Dependencies and integration points
The listed symbols correspond to features used by `ovpn-cli.c`, `common.sh`, and the shell tests: crypto algorithms for data-channel keys, nftables for mark filtering, UDP tunnel plumbing, TCP stream parsing, and the `ovpn` module itself.

## Risks and edge cases
If `CONFIG_OVPN` or required crypto is absent, tests skip or fail during `modprobe`/key setup. If nftables support is missing, `test-mark.sh` cannot validate socket marks. If stream parser support is missing, TCP variants are unreliable.

## Test signals
The practical signal is that `modprobe -q ovpn` succeeds and all selected OVPN shell tests can create OVPN interfaces, peers, and keys.
