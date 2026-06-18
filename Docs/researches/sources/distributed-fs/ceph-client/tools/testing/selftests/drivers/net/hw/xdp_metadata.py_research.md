
# `sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/xdp_metadata.py`

## Purpose
Tests device-bound XDP metadata kfunc support, specifically `bpf_xdp_metadata_rx_hash()`, by loading a BPF object, sending traffic, and reading BPF maps populated by the program.

## Important APIs, Types, And Functions
- `_load_xdp_metadata_prog()` loads all programs from `xdp_metadata.bpf.o` with `bpftool prog loadall ... xdpmeta_dev`, pins them, attaches one with `ip link set ... xdpdrv pinned`, and returns program/map IDs.
- `_send_probe()` uses `socat` to send a TCP or UDP probe.
- `test_xdp_rss_hash()` is variant-expanded over TCP and UDP and inspects `map_rss`.

## Control Flow
For each protocol, the test reads netdev info and skips unless `xdp-rx-metadata-features` contains `hash`. It loads and attaches `xdp_rss_hash`, writes the selected port into `map_xdp_setup`, sends a remote probe, dumps the RSS map, and asserts packet count, zero errors, nonzero hash value, and L4 hash type bit.

## State And Persistence
Creates and deletes `/sys/fs/bpf/xdp_metadata_test` pins and attaches XDP driver mode to the tested NIC. Deferred cleanup removes the pin directory and turns XDP off.

## Dependencies And Integration Points
Depends on compiled `xdp_metadata.bpf.o`, `xdp_dummy`-style net lib BPF helpers, `bpftool`, `bpf_map_set`, `bpf_map_dump`, `bpf_prog_map_ids`, `NetdevFamily.dev_get()`, remote `socat`, and driver support for XDP RX hash metadata.

## Risks
The test assumes BPF map names (`map_xdp_setup`, `map_rss`) and key constants match the C BPF object. Attaching XDP driver mode can disrupt existing XDP state and is restored by a broad `xdpdrv off`.

## Test Signals
Pass requires at least one packet observed by the BPF program, zero error count, nonzero RSS hash, and hash type containing the L4 bit.
