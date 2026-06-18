# sources/distributed-fs/ceph-client/drivers/media/usb/gspca/pac_common.h

Purpose: provides shared PAC207BCA/PAC73xx helper definitions for frame-boundary detection and autogain delay policy used by PAC-family GSPCA drivers.

Important APIs/types/functions: `PAC_AUTOGAIN_IGNORE_FRAMES` defines the number of frames skipped after exposure or gain changes. `pac_sof_marker` is the five-byte fixed marker `{0xff, 0xff, 0x00, 0xff, 0x96}`. `pac_find_sof(struct gspca_dev *, u8 *sof_read, unsigned char *m, int len)` is a byte-stream state machine that returns the byte after a complete marker and preserves partial matches across packets through caller-owned `sof_read`.

Control flow: callers pass each incoming packet and a persistent marker-state byte. The scanner transitions through five match states, handles repeated `0xff` bytes without losing overlap, logs successful detection with `gspca_dbg`, resets state to zero on completion or invalid bytes, and returns `NULL` when the marker is incomplete or absent in the current chunk.

State and persistence: the header itself has no global mutable state. Persistence is externalized through `*sof_read`, which lets the including driver track markers split across isochronous packets. No allocation, storage, or hardware state is touched.

Dependencies and integration: designed for direct inclusion by GSPCA PAC drivers after `gspca.h` is visible. It depends on `struct gspca_dev`, `u8`, and `gspca_dbg`. `pac7311.c` uses it to segment PAC JPEG payloads and retrieve frame-footer luminance.

Risks: because it is a header with `static` definitions, each includer gets a private copy; that is intended but can hide duplicated logic. Correctness depends on callers initializing and preserving `sof_read` per stream and passing complete packet buffers. Any change to the marker must be coordinated with frame footer offsets in users of `pac_sof_marker`.

Test signals: tests should exercise markers wholly inside a packet, split at every byte boundary, embedded after overlapping `0xff` runs, absent markers, and reset on invalid bytes. Driver-level validation is continuous frame delivery without dropped first frames after stream start.
