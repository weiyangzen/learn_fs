# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/gen6_ppgtt.c

## Purpose
Implements Sandy Bridge/Ivy Bridge/Haswell-era per-process GTT support: page-directory allocation, scratch setup, PDE flushing through GGTT, PTE insertion/clearing, pin/unpin, and platform enable programming.

## APIs And Control Flow
Exports `gen6_ppgtt_enable()`, `gen7_ppgtt_enable()`, `gen6_ppgtt_pin()`, `gen6_ppgtt_unpin()`, and `gen6_ppgtt_create()`. Creation initializes VM callbacks, scratch page/table state, and a top PD VMA in GGTT. VA allocation installs page tables from a stash and flushes PDEs if bound. Insert writes DMA-backed PTEs from sg iterators; clear resets entries to scratch and marks empty PTs for cleanup. Pinning places the PD object high in GGTT and binds PDEs.

## State, Dependencies, Integration, Risks, And Tests
Persistent state includes `struct gen6_ppgtt`, PD, scratch objects, PD GGTT VMA, `pd_addr`, `pp_dir`, pin count, PT used counts, and unused-PT scan flag. Dependencies include GGTT allocation, page-table DMA helpers, runtime PM, uncore registers, and VM reservation locking. It integrates as VM callbacks and platform PPGTT enable code. Risks are cached PDE limitations, barrier/posting-read ordering, pin-count races, and stale unused PTs. Signals include creation failures, page-table leaks, stale mappings, GPU page faults, and register misconfiguration.
