# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_cs.c

## Purpose

`radeon_cs.c` implements Radeon command submission for DRM userspace. It copies and validates command-stream chunks, resolves GEM relocations, validates and reserves BOs, allocates indirect buffers, synchronizes reservations across rings, schedules legacy or VM IBs, updates VM page tables, handles reset retry signaling, and exposes packet/relocation parsing helpers used by ASIC-specific CS validators.

## Important APIs, Types, and Functions

- `struct radeon_cs_buckets` and helpers implement stable priority buckets for relocation validation ordering.
- `radeon_cs_parser_init()` copies userspace chunk descriptors/data, records IB, CONST_IB, RELOCS, and FLAGS chunks, selects flags/ring/priority, and validates ring parser compatibility.
- `radeon_cs_get_ring()` maps UAPI ring IDs to internal GFX, compute, DMA, UVD, and VCE rings.
- `radeon_cs_parser_relocs()` looks up GEM BOs, assigns domains, rejects CPU domains, constrains userptr and dma-buf BOs, handles UVD/AGP/IGP VRAM forcing, gathers VM BOs, and validates the BO list.
- `radeon_cs_ib_fill()` allocates and fills IB/const-IB memory from userspace or pre-copied data.
- `radeon_cs_ib_chunk()` parses and schedules non-VM IBs; `radeon_cs_ib_vm_chunk()` parses, updates VM page tables, syncs, and schedules VM IBs.
- `radeon_bo_vm_update_pte()` updates VM page-directory and BO mappings, clears freed/invalid entries, syncs page-table update fences, and reserves fence slots.
- `radeon_cs_ioctl()` is the ioctl entry point coordinating exclusive-lock checks, reset handling, parser setup, validation, tracing, submission, cleanup, and lockup conversion.
- Packet helpers `radeon_cs_packet_parse()`, `radeon_cs_packet_next_is_pkt3_nop()`, `radeon_cs_dump_packet()`, and `radeon_cs_packet_next_reloc()` support ASIC parsers.

## Control Flow

`radeon_cs_ioctl()` takes the device exclusive read lock, rejects submissions when acceleration is down, handles in-progress reset, initializes a parser, fills the IB, validates relocations, emits a tracepoint, schedules non-VM and/or VM work, finalizes parser resources, releases the lock, and converts `-EDEADLK` into GPU reset plus `-EAGAIN` when possible.

Parser initialization copies the userspace chunk pointer array, then each chunk descriptor. Relocation and flags data are copied immediately; IB data is usually copied later into an allocated IB, except AGP pre-copy cases. Flags may enable VM, select a ring, and set priority. Relocation parsing treats each relocation as four dwords, resolves handles, sets placement constraints, sorts by priority, validates placements, and optionally appends VM BOs.

Non-VM submission runs the ASIC CS parser, syncs reservation fences into the IB sync object, records UVD/VCE usage, and schedules the IB. VM submission parses const and regular IBs, locks the file-private VM, updates page tables for the temporary IB BO and relocations, syncs fences, and schedules const+regular IBs on supported SI+ hardware.

## State and Persistence Behavior

Most parser memory is per-ioctl and freed by `radeon_cs_parser_fini()`: chunks, relocs, VM BO arrays, tracker state, GEM refs, and IBs. Successful submissions persist fences into BO reservation objects and can persist BO placement changes. VM submissions persist updated VM mappings and page-table state. UVD/VCE usage notifications affect video-block power-management tracking.

## Dependencies and Integration Points

The file depends on DRM/GEM lookup and references, TTM BO placement, dma-resv fences, `drm_exec`, user copy helpers, mmap locking for userptr validation, Radeon rings, IB scheduling/freeing, VM update code, BO validation, sync helpers, GPU reset, tracepoints, UVD/VCE usage tracking, and the Radeon CS UAPI structs and packet encodings.

## Risks and Edge Cases

- This is an untrusted ioctl path; chunk lengths, pointers, relocation indices, and packet counts are security-sensitive.
- Relocation chunks assume four dwords per relocation, so malformed lengths and trailing dwords need careful handling by validators.
- Parser-init failures rely on zero-initialized fields and robust cleanup of partial state.
- Priority bucket output ordering depends on subtle list-splice behavior.
- `radeon_cs_packet_next_reloc()` assumes relocation packet indices align with four-dword entries after basic bounds checks.
- VM submissions fail if BOs are not already registered in the file-private VM and must unwind page-table/sync errors cleanly.
- `-EDEADLK` triggers reset and `-EAGAIN`, requiring userspace resubmission.

## Test Signals

Coverage should include invalid chunks, missing or zero-length IBs, copy faults, invalid ring IDs, unsupported VM flags, relocation handle failures, CPU-domain rejection, userptr GTT enforcement, dma-buf VRAM exclusion, UVD/AGP/IGP domain forcing, VM page-table failures, non-VM and VM parser failures, const-IB scheduling, fence attachment only on success, packet bounds/type parsing, PKT3 NOP relocation parsing, reset conversion, and runtime lock behavior.
