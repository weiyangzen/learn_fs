# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cpu_mask.c

## Purpose
Unit-tests CPU mask string parsing/formatting helpers from libbpf internals against a table of valid and invalid CPU-list strings.

## Important APIs, types, and functions
Uses `parse_cpu_mask_str()` from `bpf/libbpf_internal.h`. `validate_mask()` compares parsed boolean mask arrays to expected strings. Test cases include ranges, commas, whitespace/duplicates, and invalid syntax.

## Control flow and state
The test iterates static cases, calls parser, and validates either failure or per-CPU booleans. State is local allocated/filled mask arrays; no persistence.

## Dependencies and integration points
Depends on libbpf internal parser and BTF include ordering only. Integrated as `test_cpu_mask()`.

## Risks and test signals
Risks are parser behavior changes and case naming mismatch. Passing signals are successful parse for valid cases, rejected invalid inputs, and exact expected mask bits.
