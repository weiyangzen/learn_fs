# sources/distributed-fs/ceph-client/drivers/gpu/nova-core/gsp/fw.rs

## Purpose

`gsp/fw.rs` wraps generated GSP firmware ABI bindings for queue headers, message elements, LIBOS arguments, WPR metadata, heap sizing, sequencer payloads, and function/opcode enums.

## Important APIs, Types, And Functions

Important exports include `GSP_MSG_QUEUE_ELEMENT_SIZE_MAX`, `LibosParams`, `GspFwWprMeta`, `MsgFunction`, `SeqBufOpcode`, sequencer payload wrappers, `SequencerBufferCmd`, `RunCpuSequencer`, `LibosMemoryRegionInitArgument`, `MsgqTxHeader`, `MsgqRxHeader`, `GspMsgElement`, `GspArgumentsCached`, and `GspArgumentsPadded`. The `gsp_mem` submodule provides DMA pointer access and advancement helpers.

## Control Flow

`LibosParams` selects LIBOS2 for pre-GA102 and LIBOS3 for GA102+, then computes WPR heap size from OS carveout, RM base, client allocation, and framebuffer management overhead clamped to allowed bounds. `GspFwWprMeta::new()` fills boot metadata from firmware DMA handles and `FbLayout`. Enums convert raw binding values to typed variants. `SequencerBufferCmd` validates opcode before reading the matching union payload. `GspMsgElement::init()` creates message headers with version, signature, function, length, and element count.

## State And Persistence Behavior

Most wrappers are transparent ABI views over generated C layouts. `GspFwWprMeta`, LIBOS arguments, queue headers, and message elements are serialized into coherent memory consumed by firmware. `gsp_mem` read/write pointer helpers mutate shared queue state with memory fences.

## Dependencies And Integration Points

It depends on generated `r570_144` bindings, `bitfield!`, coherent DMA, alignment helpers, framebuffer layout, GSP firmware objects, command queue constants, and DMA macros. It underpins `gsp.rs`, `gsp/cmdq.rs`, `gsp/commands.rs`, and `gsp/sequencer.rs`.

## Risks And Test Signals

Risks include ABI drift with firmware version 570.144, layout/padding assumptions, union payload safety depending on opcode validation, heap-size clamp choices, pointer fence correctness, message length/element-count overflow, and enum coverage. Test by build-checking bindgen layouts, booting matching firmware, validating WPR metadata values, exercising sequencer opcodes, queue pointer wraparound, and upgrading firmware bindings with compatibility tests.
