# sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib/py/bpf.py

## Purpose
This module provides small Python wrappers for common `bpftool` operations used by BPF/XDP selftests.

## Important APIs and Functions
`_format_hex_bytes(value)` encodes a signed 32-bit integer as little-endian hex bytes for bpftool CLI syntax. `bpf_map_set(map_name, key, value)` updates a named BPF map entry. `bpf_map_dump(map_id)` returns a dictionary of formatted array-map key/value entries from JSON output. `bpf_prog_map_ids(prog_id)` reads a BPF program's map IDs, resolves their names, and returns a name-to-ID mapping.

## Control Flow and State
All functions are synchronous wrappers around `bpftool` invocations. The only state modified is kernel BPF map state via `bpf_map_set`; dump and ID lookup are read-only from the module perspective.

## Dependencies and Integration
It depends on `bpftool` from `utils.py`, JSON output support in bpftool, and map/program names matching loaded BPF objects. XDP tests can use it to configure `map_xdp_setup` and read stats maps.

## Risks and Test Signals
`_format_hex_bytes` uses `signed=True`, so values outside signed 32-bit range can raise errors. The formatted fields returned by bpftool differ by map type and kernel/bpftool version. Successful signals are valid JSON parse results and expected map IDs or updated entries.
