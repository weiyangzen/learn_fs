# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu_ucode_xfer_vi.h

## Purpose

`smu_ucode_xfer_vi.h` defines the Volcanic Islands SMU DRAM table of contents used for firmware component transfer. It describes a fixed-size TOC containing entries for SMU, SDMA, CP, GMCON, RLC, VBIOS, metadata, and related payloads. It is a layout header rather than an implementation.

## Important APIs, types, and constants

`SMU_DRAMData_TOC_VERSION` identifies the TOC format. `SMU_DIGEST_SIZE_BYTES`, `SMU_FB_SIZE_BYTES`, and `SMU_MAX_ENTRIES` set digest, firmware buffer, and entry-count limits. `MAX_IH_REGISTER_COUNT` bounds interrupt-handler register restore metadata.

The `UCODE_ID_*` constants enumerate supported firmware components. IDs 0 through 14 cover major firmware blobs and metadata; IDs 32 through 36 cover RLC scratch/SRM, MEC storage, and VBIOS parameters; `UCODE_META_DATA 0xFF` identifies metadata payloads. The low `UCODE_ID_*_MASK` macros map the first 13 entries to a bitmask used by callers to select components.

`UCODE_FLAG_UNHALT_MASK` marks entries whose firmware should be unhalted after load. `struct SMU_Entry` is the per-component descriptor: ID, version, image address, metadata address, data size, flags, and register-entry count. The structure has explicit `__BIG_ENDIAN` member ordering for the paired 16-bit fields. `struct SMU_DRAMData_TOC` stores version, number of entries, and a 12-entry array.

## Control flow

There is no executable control flow in the header. Runtime transfer code builds a `SMU_DRAMData_TOC`, populates each `SMU_Entry`, points the SMU at the DRAM buffer, and issues firmware load messages. Firmware then walks the entries and performs the selected component loads or register restore operations.

## State and persistence behavior

The TOC is transient DRAM state used during firmware loading or restore. The persistent effects are loaded firmware images, restored interrupt-handler registers, VBIOS parameter availability, and any firmware unhalt operations triggered by entry flags. The structure itself is replaced whenever the driver prepares a new transfer.

## Dependencies and integration points

The header depends on the including driver path for integer definitions and endian macros. It integrates with VI SMU firmware loading, CGS firmware lookup, PSP/SMU boot sequencing, and register restore metadata generation. Consumers must provide valid GPU-visible addresses split into high/low words.

The endianness branch is important because the SMU consumes a specific memory representation. Host and firmware byte order must agree after any CPU-to-firmware conversions performed by the caller.

## Risks

`SMU_MAX_ENTRIES` is 12 even though more than 12 IDs are defined. Callers must decide which IDs are represented in a given TOC and avoid overflowing the array. The 16-bit field ordering under `__BIG_ENDIAN` is easy to miss during refactoring.

Address and size fields are trusted by firmware. A bad address split, stale metadata address, incorrect register count, or missing `UNHALT` flag can fail boot, leave engines halted, or restore wrong hardware state. Bitmask constants do not cover every defined ID, so code that assumes mask coverage for all IDs can skip high-numbered payloads.

## Test signals

Useful validation includes VI ASIC boot, firmware reload after suspend/resume, successful SDMA/CP/RLC bring-up, and no SMU load error responses. Table-generation tests should verify entry count, endian layout, address alignment, data sizes, register metadata counts, and behavior when optional payload IDs are absent.
