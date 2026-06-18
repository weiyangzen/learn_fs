# sources/distributed-fs/ceph-client/kernel/bpf/dmabuf_iter.c

## Purpose
`dmabuf_iter.c` adds BPF iterator support for DMA-BUF objects. It supports the seq-file based `bpf_iter` target named `dmabuf` and also exposes open-coded iterator kfuncs so BPF programs can iterate `struct dma_buf` objects directly.

## Important APIs, types, and functions
`struct dmabuf_iter_priv` holds one retained `dma_buf` pointer across seq stop/start boundaries. `struct bpf_iter__dmabuf` is the BPF iterator context with metadata and nullable `struct dma_buf *`. Seq operations are `dmabuf_iter_seq_start()`, `dmabuf_iter_seq_next()`, `dmabuf_iter_seq_stop()`, and `dmabuf_iter_seq_show()`. Registration is described by `bpf_dmabuf_reg_info`. Open-coded iterator ABI is `struct bpf_iter_dmabuf` with kernel view `struct bpf_iter_dmabuf_kern`, plus kfuncs `bpf_iter_dmabuf_new()`, `bpf_iter_dmabuf_next()`, and `bpf_iter_dmabuf_destroy()`.

## Control flow
The seq iterator starts at `dma_buf_iter_begin()` for position zero. For later starts it resumes from the retained `p->dmabuf`, clears the retained slot, and ignores the numeric position. `next` advances with `dma_buf_iter_next()`. `stop` retains the current object so it cannot be destroyed before a resumed `start`; final iterator cleanup drops any retained reference. `show` builds a `bpf_iter_meta` and `bpf_iter__dmabuf` context, fetches the attached BPF iterator program, and runs it if present.

The open-coded kfunc iterator initializes its opaque state to null, returns the first dma-buf on the first `next`, advances on subsequent `next` calls, and drops the retained object in `destroy`.

## State and persistence behavior
Seq iterator state is per-open private data and may hold one extra dma-buf reference between `stop` and the next `start` or final release. The open-coded iterator state is caller-owned stack/storage with one retained dma-buf pointer. The registration itself is global after `late_initcall()`.

## Dependencies and integration points
The file depends on DMA-BUF iteration primitives (`dma_buf_iter_begin`, `dma_buf_iter_next`, `dma_buf_put`), BPF iterator registration, BTF id lookup for `struct dma_buf`, seq-file operations, and kfunc definition macros. `bpf_iter_reg_target()` registers the target with `BPF_ITER_RESCHED`, allowing long walks to reschedule.

## Risks and test signals
Primary risks are dma-buf reference leaks, stale pointers across seq stop/start, missing final stop callback behavior, BTF id registration failures, and opaque/kern iterator layout mismatch. Tests should open and read the `dmabuf` iterator with and without attached programs, stop/resume reads, release before resume, verify fdinfo text, iterate with the kfunc API until null, call destroy after partial and complete walks, and validate no leaked dma-buf refs under concurrent buffer creation/destruction.
