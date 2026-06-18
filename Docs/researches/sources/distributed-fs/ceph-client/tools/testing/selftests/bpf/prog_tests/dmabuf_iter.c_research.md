# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/dmabuf_iter.c

## Purpose
Tests BPF dma-buf iterator programs, including default iterator output, no infinite reads, large output from many buffers, and open-coded iterator use.

## Important APIs, types, and functions
Uses `dmabuf_iter.skel.h`, `/dev/udmabuf`, `/dev/dma_heap/system`, `memfd_create()`, `UDMABUF_CREATE`, `DMA_HEAP_IOCTL_ALLOC`, `DMA_BUF_SET_NAME_B`, `bpf_iter_create()`, `getline()`, map updates/lookups, and `bpf_prog_test_run_opts()`. `create_udmabuf()` and `create_sys_heap_dmabuf()` create named buffers. `DmabufInfo` parses iterator output fields.

## Control flow and state
The test opens/loads skeleton, seeds a hash map with expected buffer names, creates two test dma-bufs, attaches iterator programs, runs subtests, optionally creates 100 additional system-heap buffers, then destroys all FDs and skeleton. State includes global dma-buf FDs/sizes/names, BPF map keyed by names, iterator FDs/files, and parsed output.

## Dependencies and integration points
Requires dma-buf kernel support, `/dev/udmabuf`, `/dev/dma_heap/system`, ioctl support, BPF iterator support, and generated skeleton. Integrated as `test_dmabuf_iter()`.

## Risks and test signals
Device availability is the biggest risk. Passing signals are iterator reads eventually returning zero, expected named udmabuf and system heap buffers found with correct size/exporter, large output exceeding 4096 bytes with many buffers, and open-coded iteration marking map entries found.
