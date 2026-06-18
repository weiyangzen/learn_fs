# sources/distributed-fs/ceph-client/drivers/media/rc/img-ir/img-ir-sharp.c

Purpose: provides the ImgTec hardware descriptor for Sharp IR. It decodes the first half of Sharp-style messages and supports command-aware hardware filtering.

Important APIs, types, and functions: `img_ir_sharp_scancode()` requires 15 bits, extracts address, command, expansion bit, and check bit, rejects messages without the expansion bit or with the check bit set because those are likely the second half of the paired message, and emits `RC_PROTO_SHARP`. `img_ir_sharp_filter()` maps address/command filters to raw bits and, when command filtering is requested, constrains `exp=1` and `chk=0` to match only the first part. The `img_ir_sharp` descriptor uses pulse-distance code type, secondary decoder mode (`decodend2`), `d1validsel`, 20 percent tolerance, 320 us pulse with 680/1680 us spaces, fixed 15-bit length, and filter support.

Control flow: selected by the parent hardware decoder for `RC_PROTO_BIT_SHARP`. The hardware decodes secondary no-leader symbols; the scancode callback filters out second-half echoes, then the parent emits keydown.

State and persistence behavior: no mutable state. The two-part Sharp message protocol is handled by rejecting the second half rather than storing pairing state.

Dependencies and integration points: depends on `img-ir-hw.h`. It mirrors the software Sharp decoder's first/second frame rules but relies on hardware symbol decoding.

Risks and edge cases: rejecting second halves avoids duplicate keydown but assumes the first half is always available and sufficient. Filter behavior changes when command mask is nonzero, so address-only filters are less constrained than command filters. No repeat descriptor is present.

Test signals: test known Sharp remotes, first/second half suppression, address-only and address+command filters, and no-leader secondary decoder timing behavior.
