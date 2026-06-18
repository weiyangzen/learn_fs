<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/hisi-ptt-decoder/hisi-ptt-pkt-decoder.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/hisi-ptt-decoder/hisi-ptt-pkt-decoder.h

## Purpose
This header defines the small packet-decoder ABI for HiSilicon PTT trace dumps: packet type identifiers, packet sizes, field width constants, and the decode/print function prototype.

## Important APIs, types, and functions
Constants include `HISI_PTT_8DW_CHECK_MASK`, `HISI_PTT_IS_8DW_PKT`, `HISI_PTT_MAX_SPACE_LEN`, and `HISI_PTT_FIELD_LENTH`. `enum hisi_ptt_pkt_type` distinguishes 4DW and 8DW packets. `hisi_ptt_pkt_size[]` maps packet types to 16 and 32 bytes. The declared function is `hisi_ptt_pkt_desc`.

## Control flow
Consumers inspect packet headers, choose an enum value, use `hisi_ptt_pkt_size[type]` for alignment/iteration, and call `hisi_ptt_pkt_desc` for formatted output.

## State and persistence
The header defines a non-const `static int hisi_ptt_pkt_size[]` in every translation unit that includes it. This is per-TU state, although it is intended as immutable lookup data.

## Dependencies and integration points
It relies on Linux `GENMASK` being available from includers before macro use; the `.c` files include `<linux/bitops.h>` before this header. It integrates with `hisi-ptt.c` and the decoder implementation.

## Risks
The array should ideally be `static const` to prevent accidental writes. The `HISI_PTT_FIELD_LENTH` typo is part of the local API. The header itself does not include `<linux/bitops.h>`, so standalone inclusion can fail.

## Test signals
Build the decoder and `hisi-ptt.c` together, assert packet sizes match 4DW/8DW expectations, and compile a standalone include test if the header is made more public.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/hisi-ptt-decoder/hisi-ptt-pkt-decoder.h -->
