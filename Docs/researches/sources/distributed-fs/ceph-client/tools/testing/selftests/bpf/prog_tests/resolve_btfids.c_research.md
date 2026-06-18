# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/resolve_btfids.c

## Purpose
Unit-tests userspace BTF ID symbol resolution logic used by kernel tooling, mapping symbol records to BTF type ids. The source was read as a complete 168-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `__resolve_symbol()`, `resolve_symbols()`, `test_resolve_btfids()`.
- Includes and fixtures: `#include <linux/err.h>`, `#include <string.h>`, `#include <bpf/btf.h>`, `#include <bpf/libbpf.h>`, `#include <linux/btf.h>`, `#include <linux/kernel.h>`, `#include <linux/btf_ids.h>`, `#include "test_progs.h"`.
- Generated skeletons/objects referenced: none in this C file; it uses raw object/helper loading or framework macros.
- Primary APIs and types: `btf__parse()`, `btf__find_by_name_kind()`, `__resolve_symbol()`, `resolve_symbols()`, `struct btf_id`, `ERR_PTR` helpers, and libbpf BTF APIs.

## Control Flow
The test constructs symbol requests, resolves each against BTF by name/kind, writes ids into result structures, and checks error behavior for missing or incompatible symbols.

## State and Persistence Behavior
State is local arrays of symbols/ids and a parsed BTF object. No kernel BPF program is loaded.

## Dependencies and Integration Points
Depends on libbpf BTF parser, kernel/user BTF data available to the fixture, and `linux/btf_ids.h` structure definitions.

## Risks and Edge Cases
BTF contents differ across kernels/configs; symbol-kind mismatches can be environment-specific; error-pointer handling must not be confused with raw ids.

## Test Signals
Pass/fail is determined by successful resolution of expected symbols and expected errors for unresolved entries. Named assertion/check labels observed in the source include: `id_check`, `ID %d not found in test_symbols\n`.
