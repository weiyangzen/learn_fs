# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_sh_mask.h lines 67203-67286

## Purpose

This chunk is the final slice of the generated AMD DCN 4.2.0 register shift/mask header. It contains compile-time preprocessor constants for HDA audio stream descriptor fields, specifically the tail of `AZSTREAM6_1_OUTPUT_STREAM_DESCRIPTOR_*` and the complete `AZSTREAM7_1_OUTPUT_STREAM_DESCRIPTOR_*` block, followed by the header guard close.

The macros describe bit positions and masks for DCN audio output stream descriptor registers. Runtime AMDGPU Display Core and DMUB code pairs these constants with the matching address definitions in `dcn_4_2_0_offset.h` and with register helper macros to reset, start, format, locate, and monitor HDMI/DisplayPort audio DMA streams. This source path is under a `ceph-client` mirror, but the content is AMDGPU display hardware metadata and does not implement distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no C functions, structs, enums, variables, includes, callbacks, locks, allocation paths, or direct MMIO operations in this range. The exported interface is the generated macro convention:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset for encoding or decoding a hardware register field.
- `<REGISTER>__<FIELD>_MASK`: bit mask used to isolate, preserve, clear, or update that field.

The `AZSTREAM6_1` portion starts mid-register at `OUTPUT_STREAM_DESCRIPTOR_FORMAT__BITS_PER_SAMPLE__SHIFT`; the preceding line outside this chunk contains `NUMBER_OF_CHANNELS__SHIFT`. This chunk then completes the `AZSTREAM6_1_OUTPUT_STREAM_DESCRIPTOR_FORMAT` masks and covers the BDL lower pointer, BDL upper pointer, and link-position alias fields.

The `AZSTREAM7_1` portion covers the full output stream descriptor set:

- `CONTROL_AND_STATUS`: stream reset/run controls, interrupt enables for completion/FIFO/descriptor errors, stripe control, traffic priority, stream number, completion status, FIFO error, descriptor error, and FIFO-ready status.
- `LINK_POSITION_IN_CURRENT_BUFFER`: 32-bit playback/DMA position within the current buffer.
- `CYCLIC_BUFFER_LENGTH`: 32-bit cyclic buffer length field.
- `LAST_VALID_INDEX`: 8-bit last valid Buffer Descriptor List index.
- `FIFO_SIZE`: 16-bit FIFO size.
- `FORMAT`: channel count, bits per sample, sample base divisor, sample base multiple, and sample base rate fields.
- `BDL_POINTER_LOWER_BASE_ADDRESS`: lower Buffer Descriptor List base address bits, with low 7 unimplemented/alignment bits.
- `BDL_POINTER_UPPER_BASE_ADDRESS`: upper 32 bits of the Buffer Descriptor List address.
- `LINK_POSITION_IN_CURRENT_BUFFER_ALIAS`: 32-bit alias for link position reporting.

## Control Flow

This header has no runtime control flow. It contributes constants to driver control paths that perform the actual sequence:

1. DCN 4.2.0 code includes `dcn_4_2_0_offset.h` and `dcn_4_2_0_sh_mask.h`.
2. Register-list and helper macros token-paste register and field names into offset, mask, and shift tables.
3. Runtime audio/display code programs stream descriptor registers through read-modify-write helpers such as `REG_SET`, `REG_UPDATE`, `REG_GET`, or related ASIC-specific wrappers.
4. Hardware consumes the programmed fields to reset or run the audio stream, select format and stream number, locate the cyclic DMA buffer through the BDL pointer, expose link position, and report completion/FIFO/descriptor status.

The macros do not encode required sequencing. Consumers must still follow HDA/audio stream programming order: quiesce or reset a stream before changing descriptors, program buffer length and BDL address with the required alignment, set format and stream number consistently with the audio engine, enable interrupts deliberately, start the stream, and handle status or error bits according to hardware semantics.

## State And Persistence Behavior

The header itself stores no state and persists nothing to disk. The underlying hardware registers represent live stream state:

- Control fields such as `STREAM_RESET`, `STREAM_RUN`, interrupt enables, stripe control, traffic priority, and stream number persist in the hardware register until changed, reset, power-gated, or reinitialized.
- Format fields persist as the active audio stream sample/channel encoding while the stream is configured.
- Buffer fields persist the DMA ring geometry: cyclic buffer length, last valid descriptor index, and lower/upper BDL base address.
- Link-position fields expose transient playback position counters or aliases.
- Completion, FIFO error, descriptor error, and FIFO-ready status fields are hardware state observations and may be sticky, transient, read-only, write-one-to-clear, or self-clearing depending on the register specification.

These generated masks do not indicate reset values, read/write permissions, clearing rules, or firmware ownership. Driver code must rely on the hardware specification and existing AMDGPU sequencing for safe access.

## Dependencies And Integration Points

The direct dependency is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_offset.h`, which defines the matching register addresses and base indices. In that offset header, `AZSTREAM6_1` descriptor registers map to the `0x4b7050` range with the alias at `0x4b7851`, while `AZSTREAM7_1` maps to the `0x4b7058` range with the alias at `0x4b7859`; both use base index `3`.

The same shift/mask header is included by DCN 4.2 integration code such as:

- `display/dmub/src/dmub_dcn42.c`, which initializes DMUB register access tables from generated offsets, shifts, and masks.
- `display/dc/irq/dcn42/irq_service_dcn42.c`, which depends on generated register metadata for DCN 4.2 interrupt programming.
- `display/dc/gpio/dcn42/hw_factory_dcn42.c` and `display/dc/gpio/dcn42/hw_translate_dcn42.c`, which include the same ASIC register headers for DCN 4.2 GPIO/HPD/AUX translation.
- DCN 4.2 resource construction and audio/display paths that rely on consistent generated register naming across repeated AZ stream instances.

The repeated `AZSTREAM6_1` and `AZSTREAM7_1` field layouts are an integration contract: generic audio stream setup code can reuse common descriptor logic only if each instance's field names, masks, shifts, and offset-header entries stay synchronized.

## Risks And Edge Cases

- A wrong shift or mask can compile cleanly while programming the wrong hardware bits, causing silent audio stream failures.
- This chunk begins in the middle of `AZSTREAM6_1_OUTPUT_STREAM_DESCRIPTOR_FORMAT`; final per-register completeness checks must merge with the previous chunk before concluding whether the format field set is complete.
- BDL lower-address programming uses low 7 unimplemented bits and an address mask of `0xFFFFFF80L`. Callers must preserve alignment requirements and avoid treating the lower address as an arbitrary 32-bit value.
- `FIFO_SIZE` and `FORMAT` share the same offset in the companion header for each stream instance, so callers must use field masks carefully rather than whole-register writes that clobber unrelated fields.
- Completion, FIFO error, descriptor error, and FIFO-ready fields have status semantics that are not visible in this header. Misinterpreting status bits as normal writable fields can lose interrupts, fail to clear errors, or create repeated interrupts.
- Stream reset/run and descriptor programming are sequencing-sensitive. Updating BDL address, cyclic buffer length, last valid index, or format while a stream is running can race the audio DMA engine.
- The file is generated hardware ABI metadata. Manual edits can diverge from AMD's register database, silicon documentation, firmware assumptions, and the paired offset header.
- The final `#endif` means this is the end of the full header. Accidental edits near this boundary can break every translation unit including `dcn_4_2_0_sh_mask.h`.

## Test Signals

Useful validation signals for this chunk include:

- Build AMDGPU Display Core with DCN 4.2 support enabled. Missing or renamed macros should surface through compile failures in DMUB, IRQ, GPIO, resource, or audio/display register-table code.
- Mechanically compare all complete fields in this chunk against `dcn_4_2_0_offset.h` and AMD's generated DCN 4.2.0 register database; `AZSTREAM6_1` and `AZSTREAM7_1` should preserve the expected repeated descriptor layout.
- Check that every `__SHIFT` in this chunk has a corresponding `_MASK`, accounting for the known chunk-boundary exception where `AZSTREAM6_1_OUTPUT_STREAM_DESCRIPTOR_FORMAT__NUMBER_OF_CHANNELS__SHIFT` is immediately before line 67203.
- Exercise HDMI/DisplayPort audio playback paths that use the later stream descriptors, including stream start/stop, reset, format changes, channel-count changes, and suspend/resume reinitialization.
- Test DMA buffer setup with different cyclic buffer sizes and BDL lengths, including validation that lower address alignment and upper address handling work on systems using addresses above 4 GiB.
- Enable and observe completion, FIFO error, and descriptor error interrupt paths. Kernel logs, audio underruns, stream stalls, and repeated interrupt reports are high-signal indicators of bad status or enable masks.
- Read link-position registers during playback and compare monotonic/progress behavior against expected audio DMA movement.

## Cross-Chunk Notes

The previous chunk owns the beginning of the `AZSTREAM6_1` descriptor block, including `CONTROL_AND_STATUS`, link position, cyclic buffer length, last valid index, FIFO size, and the first `FORMAT` shift line. This chunk completes `AZSTREAM6_1`, owns all of `AZSTREAM7_1`, and closes `dcn_4_2_0_sh_mask.h`. The final per-file research document should reconcile this tail chunk with earlier chunks before making whole-file claims about all DCN 4.2.0 audio stream descriptor instances.
