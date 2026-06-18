<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/xstate.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/xstate.h

## Purpose

`xstate.h` provides shared data structures and inline helpers for x86 extended-state selftests. It abstracts XSAVE buffer layout, feature metadata, CPUID discovery, and low-level XSAVE/XRSTOR operations.

## Important APIs, Types, and Functions

The header defines `enum xfeature`, `xfeature_names`, `struct xsave_buffer`, `struct xstate_info`, `xsave()`, `xrstor()`, `get_xbuf_size()`, `get_xstate_info()`, `alloc_xbuf()`, `clear_xstate_header()`, `set_xstatebv()`, `get_fpx_sw_bytes()`, `get_fpx_sw_bytes_features()`, `set_rand_data()`, and the exported `test_xstate()` declaration.

## Control Flow and State

There is no standalone control flow. Inline helpers use CPUID leaf 0xd to compute XSAVE area size and per-feature offsets, allocate 64-byte aligned buffers, manipulate the XSAVE header, and fill feature data with nonzero randomized words. State lives in caller-owned buffers.

## Dependencies and Integration Points

It depends on `<stdint.h>`, kselftest helpers, compiler support for inline x86 assembly, CPUID, XSAVE/XRSTOR, and signal-frame `_fpx_sw_bytes` layout. `xstate.c` is the main consumer.

## Risks and Test Signals

Risks include feature-number drift with kernel definitions, wrong XSAVE offsets, insufficient alignment, and random data accidentally representing init state. Successful `xstate.c` runs validate that these helpers match kernel ABI expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/xstate.h -->
