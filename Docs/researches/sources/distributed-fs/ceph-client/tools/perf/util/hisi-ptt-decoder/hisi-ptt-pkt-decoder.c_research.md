<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/hisi-ptt-decoder/hisi-ptt-pkt-decoder.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/hisi-ptt-decoder/hisi-ptt-pkt-decoder.c

## Purpose
This file pretty-prints HiSilicon PCIe Trace and Tuning packet bytes for dump/debug output. It understands the PTT 4DW and 8DW packet layouts and emits colored annotated dword rows.

## Important APIs, types, and functions
The public API is `hisi_ptt_pkt_desc(const unsigned char *buf, int pos, enum hisi_ptt_pkt_type type)`, which returns the decoded packet size. Internal packet layout enums name 8DW and 4DW fields. `union hisi_ptt_4dw` overlays DW0 bitfields for 4DW packets. Helpers include `hisi_ptt_print_pkt`, `hisi_ptt_8dw_kpt_desc`, `hisi_ptt_4dw_print_dw0`, and `hisi_ptt_4dw_kpt_desc`.

## Control flow
The dispatcher selects 8DW or 4DW decoding. 8DW decoding skips the check/reserved DW0 and reserved DW6 fields, printing prefix, headers, and time. 4DW decoding prints DW0 as decoded bitfields, then prints header DW1-DW3. Every printed row reads four bytes from `buf + pos` and advances by `HISI_PTT_FIELD_LENTH`.

## State and persistence
No persistent state is kept. Output goes directly to stdout using perf color helpers.

## Dependencies and integration points
It is called by `hisi-ptt.c` when `dump_trace` is enabled for AUX trace data. It depends on `color.h` and constants from `hisi-ptt-pkt-decoder.h`.

## Risks
The decoder assumes the caller rounded buffer length to complete packets and that `pos` is valid. It casts unaligned byte pointers to `uint32_t *` and uses C bitfields, which can be sensitive to alignment and compiler/endianness expectations. The function name typo `kpt` is internal but can hinder searches.

## Test signals
Use known 4DW/8DW packet byte fixtures, boundary tests for one packet, mixed invalid/truncated buffer tests in the caller, and stdout golden output for DW0 field formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/hisi-ptt-decoder/hisi-ptt-pkt-decoder.c -->
