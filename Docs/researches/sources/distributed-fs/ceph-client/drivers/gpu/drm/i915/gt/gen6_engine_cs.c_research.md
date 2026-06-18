# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/gen6_engine_cs.c

## Purpose
Implements gen6/gen7/Haswell command streamer helpers for render and non-render engines: PIPE_CONTROL flushes, MI_FLUSH_DW flushes, breadcrumbs, batch starts, and IRQ masking.

## APIs And Control Flow
Exports `gen6_emit_flush_rcs/xcs/vcs()`, `gen7_emit_flush_rcs()`, `gen6_emit_bb_start()`, `hsw_emit_bb_start()`, gen6/gen7 breadcrumb emitters, and gen6/HSW IRQ helpers. Gen6 render flushes emit Sandy Bridge PIPE_CONTROL workarounds first, then apply flush/invalidate bits. XCS/VCS use `MI_FLUSH_DW`. Gen7 render flushes force CS stall and post-sync writes, with an extra stall before state-cache invalidation. Breadcrumbs write seqnos and trigger user interrupts.

## State, Dependencies, Integration, Risks, And Tests
State changes are ring contents, HWS seqnos, scratch writes, request tails, and interrupt masks. Dependencies include GPU command encodings, ring helpers, GT scratch, gen5/gen6 IRQ infrastructure, and batch-start helpers. These functions populate engine ops for SNB/IVB/HSW-era hardware. Risks are ordering-sensitive PIPE_CONTROL workarounds, stale seqnos/cache data, and reserved breadcrumb size mismatches. Signals include request hangs, stale readback, missing interrupts, invalid tails, and render-cache invalidation failures.
