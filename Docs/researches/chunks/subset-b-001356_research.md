# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v6_0_0_pkt_open.h lines 1-4513

## Scope

This chunk covers the first 4,513 lines of `sdma_v6_0_0_pkt_open.h`, a generated-style AMDGPU SDMA packet definition header. The source file continues beyond this chunk; this report intentionally stops in the `SDMA_PKT_POLL_REGMEM` packet definition and does not cover later poll variants, atomic packets, timestamp packets, traps, GPUVM invalidation, GCR request payloads, or NOP definitions that appear after line 4513.

The chunk contains no executable functions and no C structs. Its public surface is a dense set of preprocessor constants and field-packing macros used by SDMA ring and IB emitters to construct 32-bit command words for SDMA v6.0.0-compatible engines.

## Purpose

The header defines the binary command-stream ABI for AMD SDMA packet words. It maps high-level SDMA operations such as copy, write, indirect buffer execution, fences, semaphores, VM invalidation, register writes, conditional execution, fills, and polling into fixed opcode values, sub-opcode values, packet word offsets, field masks, field shifts, and helper macros.

The core macro pattern is repeated for each field:

- `<PACKET>_<WORD>_<field>_offset` identifies the dword index in the packet.
- `<PACKET>_<WORD>_<field>_mask` constrains the accepted field value before insertion.
- `<PACKET>_<WORD>_<field>_shift` identifies the bit position inside that dword.
- `<PACKET>_<WORD>_<FIELD>(x)` packs a caller-provided value with `((x) & mask) << shift`.

This lets AMDGPU C code write packet streams with symbolic names while still emitting the exact dword layout required by firmware and hardware.

## Important APIs And Macro Families

The opening constants define the main SDMA opcodes: `SDMA_OP_NOP`, `COPY`, `WRITE`, `INDIRECT`, `FENCE`, `TRAP`, `SEM`, `POLL_REGMEM`, `COND_EXE`, `ATOMIC`, `CONST_FILL`, `PTEPDE`, `TIMESTAMP`, `SRBM_WRITE`, `PRE_EXE`, `GPUVM_INV`, `GCR_REQ`, and `DUMMY_TRAP`. These are the low eight bits of most packet headers.

Sub-opcode constants refine packet families:

- Copy sub-ops cover linear, tiled, structured, dirty-page, physical-linear, tiled-to-tiled, broadcast, large sub-window, and block-compressed variants.
- Write sub-ops distinguish linear/untiled, tiled, and block-compressed tiled writes.
- PTE/PDE sub-ops cover generation, copy, read-modify-write, and backwards copy.
- Poll sub-ops cover base poll, poll-register-write-memory, dirty-bit write memory, poll-memory-verify, and VM invalidation.
- Timestamp, memory increment, and multi-fill sub-ops are also assigned here.

`SDMA_GCR_*` macros define cache-control bitfields for global cache request packets. They express GL2 writeback/invalidate/discard/range, GL1/GLV/GLK/GLM invalidation/writeback, range controls, physical-address selection, and sequence bits. In this chunk they are helper controls, not a full GCR packet payload definition.

`SDMA_DCC_*` macros define DCC metadata packing helpers for data format, number type, read/write compression mode, and compressed/uncompressed block-size controls. These are used by copy packets that carry metadata configuration for compressed image surfaces.

## Packet Families In This Chunk

Lines 103-210 define `SDMA_PKT_COPY_LINEAR`: a basic linear memory copy packet with header flags for encryption, TMZ, CPV, backwards copy, and broadcast, plus count, source/destination swizzle/cache policy fields, and 64-bit source/destination addresses.

Lines 211-288 define `SDMA_PKT_COPY_LINEAR_BC`: a block-compressed linear copy variant with smaller count width and host-access-style `src_ha`/`dst_ha` flags instead of the cache-policy layout used by the non-BC packet.

Lines 289-450 define `SDMA_PKT_COPY_DIRTY_PAGE`: dirty-page copy support with `all`, TMZ, CPV, count, source/destination memory type, L2/LLC policy, SW/GCC/SYS/snoop/GPA controls, and 64-bit source/destination addresses.

Lines 451-624 define `SDMA_PKT_COPY_PHYSICAL_LINEAR`: physical-linear copy with an address-pair count and similar source/destination memory type, coherency, snoop, GPA, and address controls. This is sensitive because it can encode physical addressing policy directly into the packet.

Lines 625-752 define `SDMA_PKT_COPY_BROADCAST_LINEAR`: one source copied to two destination addresses. It defines separate destination-1 and destination-2 swizzle/cache policy and address fields.

Lines 753-927 define `SDMA_PKT_COPY_LINEAR_SUBWIN`: sub-window linear copy with source/destination base addresses, x/y/z coordinates, pitches, slice pitches, rectangle dimensions, element size, TMZ/CPV, and source/destination cache policy fields.

Lines 927-1113 define `SDMA_PKT_COPY_LINEAR_SUBWIN_LARGE`: a large-coordinate sub-window variant. It expands x/y/z, pitch, and slice-pitch fields into wider dword-sized or split fields for larger surfaces.

Lines 1114-1275 define `SDMA_PKT_COPY_LINEAR_SUBWIN_BC`: block-compressed sub-window linear copy with smaller z/pitch fields and HA-style source/destination flags.

Lines 1276-1455 define `SDMA_PKT_COPY_TILED`: tiled-to-linear or linear-to-tiled copy controlled by the `detile` header bit. It includes tiled base address, width/height/depth, element size, swizzle mode, dimension, mip maximum, x/y/z coordinates, linear/tile swizzle and cache policies, linear address/pitch/slice pitch, and byte count.

Lines 1456-1635 define `SDMA_PKT_COPY_TILED_BC`: block-compressed tiled copy. It uses legacy-style tiling fields such as array mode, MIT mode, tile split size, bank width/height, number of banks, macro tile aspect, and pipe config.

Lines 1636-1848 define `SDMA_PKT_COPY_L2T_BROADCAST`: linear-to-tiled broadcast with two tiled destinations, one linear source, image geometry, swizzle metadata, source/destination cache policy controls, and count.

Lines 1849-2183 define `SDMA_PKT_COPY_T2T`: tiled-to-tiled sub-window copy. It defines independent source and destination image geometry, swizzle modes, mip metadata, rectangle dimensions, source/destination cache policy controls, and DCC metadata address/config fields.

Lines 2184-2449 define `SDMA_PKT_COPY_T2T_BC`: block-compressed tiled-to-tiled copy. It uses separate source and destination BC tiling fields, rectangle dimensions, and source/destination SW controls.

Lines 2450-2747 define `SDMA_PKT_COPY_TILED_SUBWIN`: tiled sub-window copy with TMZ, DCC, CPV, and detile flags, tiled and linear coordinates, rectangle dimensions, mip metadata, cache policy controls, metadata address/config words, and a DCC address. This is the most metadata-heavy copy packet in the chunk.

Lines 2748-2958 define `SDMA_PKT_COPY_TILED_SUBWIN_BC`: block-compressed tiled sub-window copy with BC tiling fields, linear/tile coordinates, rectangle dimensions, and linear/tile SW controls.

Lines 2959-3067 define `SDMA_PKT_COPY_STRUCT`: structured-buffer copy. It carries a structured-buffer address, start index, element count, stride, linear/structured SW/cache policy fields, and a linear address.

Lines 3068-3143 define `SDMA_PKT_WRITE_UNTILED`: immediate data write to a linear destination. It has header encryption/TMZ/CPV flags, destination address, count, SW/cache policy, and the first data dword.

Lines 3144-3284 define `SDMA_PKT_WRITE_TILED`: immediate data write to a tiled destination, including image geometry, swizzle mode, dimension, mip information, x/y/z coordinates, SW/cache policy, count, and data.

Lines 3285-3431 define `SDMA_PKT_WRITE_TILED_BC`: block-compressed tiled write with BC tiling layout fields and count shifted by two bits.

Lines 3432-3528 define `SDMA_PKT_PTEPDE_COPY`: page-table/page-directory copy with source/destination addresses, mask bits for first/last transfers, count in 32-byte transfers, and header bits for TMZ, CPV, and PTE/PDE operation selection.

Lines 3529-3612 define `SDMA_PKT_PTEPDE_COPY_BACKWARDS`: backwards PTE/PDE copy with PTE size, direction, source/destination addresses, first/last transfer masks, and transfer count.

Lines 3613-3727 define `SDMA_PKT_PTEPDE_RMW`: page-table read-modify-write. The header carries memory type, coherency, system, snoop, GPA, L2/LLC, and CPV controls; the payload has address, mask, value, and number-of-PTE fields.

Lines 3728-3785 define `SDMA_PKT_REGISTER_RMW`: register read-modify-write using register address, aperture ID, mask, value, stride, and register count.

Lines 3786-3878 define `SDMA_PKT_WRITE_INCR`: write/increment packet with destination address, two mask dwords, initial values, increments, count, cache policy, and CPV.

Lines 3879-3943 define `SDMA_PKT_INDIRECT`: indirect buffer execution with VMID, privileged bit, 64-bit IB base, IB size, and CSA address. This is the packet used to chain an SDMA ring to an IB.

Lines 3944-3993 define `SDMA_PKT_SEMAPHORE`: semaphore wait/signal/mailbox packet with write-one and signal controls plus a 64-bit address.

Lines 3994-4043 define `SDMA_PKT_MEM_INCR`: memory increment packet with L2/LLC policy, CPV, and target address.

Lines 4044-4106 define `SDMA_PKT_VM_INVALIDATION`: VM invalidation packet carrying GFX/MM engine IDs, invalidate request, address-range low, invalidate acknowledge bits, address-range high, and reserved bits.

Lines 4107-4193 define `SDMA_PKT_FENCE`: memory fence/write packet with mtype, GCC, system, snoop, GPA, L2/LLC, CPV controls, 64-bit destination address, and data.

Lines 4194-4237 define `SDMA_PKT_SRBM_WRITE`: SRBM register write with byte-enable, register address, aperture ID, and data.

Lines 4238-4268 define `SDMA_PKT_PRE_EXE`: pre-execution packet with device select and execution count.

Lines 4269-4326 define `SDMA_PKT_COND_EXE`: conditional execution packet with cache policy, CPV, comparison address, reference value, and count of following dwords to execute.

Lines 4327-4396 define `SDMA_PKT_CONSTANT_FILL`: constant fill packet with destination address, fill data, count, SW/cache policy, CPV, and fill-size selector.

Lines 4397-4467 define `SDMA_PKT_DATA_FILL_MULTI`: multi-fill packet with byte stride, DMA count, destination address, byte count, cache policy, CPV, and memory-log-clear control.

Lines 4468-4513 begin `SDMA_PKT_POLL_REGMEM`: the chunk includes only its header fields, namely opcode/sub-opcode, cache policy, CPV, HDP flush, comparison function, and memory-vs-register polling selector. Address/value/mask/retry fields are in the next chunk.

## Control Flow

This file has no runtime control flow of its own. Control flow appears when AMDGPU emitters include the header and append dwords to an SDMA ring or IB.

A typical emission flow is:

1. The caller reserves ring or IB space.
2. It writes a packet header using an `*_HEADER_OP(SDMA_OP_*)` macro and usually an `*_HEADER_SUB_OP(SDMA_SUBOP_*)` macro.
3. It writes subsequent dwords in the packet-defined order, using `*_ADDR_LO`, `*_ADDR_HI`, `*_COUNT`, `*_DW_*`, or other payload macros.
4. The SDMA engine decodes those dwords asynchronously after the command stream is submitted.

The header therefore encodes ordering rules implicitly through word offsets and macro names. The compiler does not verify that callers write every required word, choose the matching opcode/sub-opcode pair, or respect packet length expectations.

## State And Persistence Behavior

The header itself has no mutable state, static storage, persistent allocation, or side effects. Its persistent behavior is indirect: packet dwords built with these macros are written into ring buffers, indirect buffers, or firmware-visible memory and later consumed by SDMA hardware.

State effects are determined by the packet selected by the caller:

- Copy and write packets mutate GPU memory or system-visible memory depending on address and cache/coherency bits.
- PTE/PDE packets mutate GPU page-table memory and can affect future address translation.
- Fence, semaphore, memory-increment, and conditional-execution packets mutate synchronization memory and influence scheduler progress.
- VM invalidation and GCR/cache-control-related fields affect translation/cache state rather than ordinary data buffers.
- SRBM/register RMW packets mutate MMIO-visible hardware registers.
- Indirect packets alter command flow by making SDMA fetch and execute another buffer.

Because macro arguments are masked rather than validated, out-of-range values are silently truncated. This is persistent in the emitted command stream and can be hard to diagnose after the fact.

## Dependencies And Integration Points

The header depends only on the C preprocessor and an including translation unit. It does not include other headers and is protected by `__SDMA_V6_0_0_PKT_OPEN_H_`.

Its integration point is the AMDGPU SDMA command emission code. In this source tree, `sdma_v7_0.c` includes this header and uses these macros to emit commands for conditional execution, indirect buffers, GCR requests, polling, fences, traps, writes, copies, PTE/PDE updates, NOP padding, and SRBM writes. Examples include `amdgpu_ring_write()` and IB writers combining `SDMA_PKT_COPY_LINEAR_HEADER_OP(...)` with operation constants such as `SDMA_OP_COPY`, `SDMA_OP_WRITE`, `SDMA_OP_POLL_REGMEM`, `SDMA_OP_FENCE`, and `SDMA_OP_PTEPDE`.

The macro set also aligns with neighboring generation-specific packet headers such as `vega10_sdma_pkt_open.h`, `tonga_sdma_pkt_open.h`, and later `sdma_v7_1_0_pkt_open.h`. Those headers expose similar symbolic packet layouts but may differ in masks, shifts, packet length, or added fields.

Primary consumers are:

- SDMA ring function implementations that emit fences, traps, waits, VM flush/cache-control packets, and register writes.
- SDMA IB emitters for buffer copies, fills, PTE/PDE updates, and NOP padding.
- GPU memory-management code paths that rely on SDMA for page-table updates and TLB/cache maintenance.
- Scheduler/fence paths that rely on fence/semaphore/poll packets to report completion.
- Virtualization or trusted-memory paths that set `tmz`, `cpv`, `gpa`, `sys`, `snoop`, and related coherency/protection fields.

## Risks And Fragile Areas

This header is a hardware ABI surface. A wrong mask, shift, opcode, sub-opcode, or word offset can produce syntactically valid C but invalid SDMA command streams, causing data corruption, GPU hangs, lost fences, bad page-table updates, or cache coherency failures.

Many macros share the generic `SDMA_PKT_COPY_LINEAR_HEADER_OP` shape across packet families, and callers sometimes use common header macros even when emitting a different op. That works only because many packet headers place `op` and `sub_op` in identical bit positions. It becomes fragile if a future packet generation moves a common field.

The packer macros silently truncate field values. This is useful for raw bitfield construction but risky for counts, coordinates, pitches, address fragments, VMIDs, aperture IDs, and cache-policy fields. Callers must validate range and alignment before packing.

Address fields are split manually into low/high dwords. Callers must preserve alignment requirements, use the correct shifted address fragment where a field omits low address bits, and avoid mixing physical, GPU virtual, and system address encodings.

Copy and write packet variants are similar but not interchangeable. BC variants often use narrower depth/count/pitch masks or shifted count fields; using non-BC dimensions in a BC packet can truncate geometry. Large-subwindow and ordinary-subwindow variants also have different coordinate widths.

Security and virtualization bits are subtle. Fields such as `tmz`, `cpv`, `gpa`, `sys`, `snoop`, `mtype`, `gcc`, `llc_policy`, and `l2_policy` must match memory placement and platform mode. Incorrect values can break encrypted-memory handling, coherent CPU/GPU access, or guest/host address interpretation.

PTE/PDE and VM invalidation packets are especially sensitive because they affect address translation. Errors here can leave stale translations, write malformed page-table entries, or invalidate the wrong engine/address range.

The chunk boundary splits `SDMA_PKT_POLL_REGMEM`. Any analysis or generated documentation that treats this chunk alone as a complete packet reference would miss the address, value, mask, interval, and retry fields that follow after line 4513.

## Test Signals

There are no unit-testable functions in this header. Useful validation is integration-oriented:

- Build coverage for all translation units that include `sdma_v6_0_0_pkt_open.h`; macro drift should fail compile when callers reference removed or renamed fields.
- SDMA ring tests should pass for engines using this header, especially basic NOP/write/fence/trap paths.
- IB copy/fill tests should verify linear copy, write, constant fill, and multi-fill packets produce expected memory contents across VRAM, GTT, and system-memory mappings.
- Tiled and BC copy tests should validate geometry, pitches, swizzle/array-mode fields, DCC metadata, and detile behavior on representative image formats.
- Fence/semaphore/poll tests should confirm completion signaling, memory polling, HDP flush behavior, retry/timeout behavior, and scheduler wakeups.
- VM/PTE tests should exercise PTE/PDE copy/RMW, backwards copy, VM invalidation, and subsequent GPU memory access to catch stale or malformed translations.
- Register-write/RMW/SRBM tests should verify the intended register aperture and byte-enable behavior under bare metal and SR-IOV where allowed.
- TMZ/CPV/GPA/coherency tests should run on platforms that support encrypted or virtualized memory paths, because field mistakes may not be visible on simple unencrypted local-memory copies.
