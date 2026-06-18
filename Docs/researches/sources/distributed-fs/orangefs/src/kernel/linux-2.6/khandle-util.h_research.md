# sources/distributed-fs/orangefs/src/kernel/linux-2.6/khandle-util.h

Purpose: Provides `k2s`, the shared debug-formatting helper that converts a `PVFS_khandle` into a printable string for gossip logging.

Important APIs and functions: `k2s(PVFS_khandle *khandle, char *s)` is the only function in this header. For handles that look like the legacy 64-bit encoding, it rearranges selected bytes into `struct ihash` and prints the integer form. For 128-bit handles, it emits a UUID-like uppercase hexadecimal string with dashes. Callers are expected to allocate at least `HANDLESTRINGSIZE` bytes, as declared in `khandle.h`.

Control flow: The function scans bytes 4 through 11; if they are all zero it treats the handle as the 64-bit legacy layout, otherwise as a full 128-bit handle. The 64-bit path copies bytes 0-3 and 12-15 into an `ihash` union and formats `ihash.ino`. The 128-bit path converts each byte into two hex digits using a local lookup table and inserts dashes after selected byte positions.

State and persistence: No persistent state. It writes only into the caller-provided output buffer and reads the supplied handle. The function is used primarily in logging paths, so failures would affect diagnostics more than filesystem semantics unless a NULL pointer is passed.

Dependencies and integration points: Depends on `PVFS_khandle`, `struct ihash`, and `HANDLESTRINGSIZE` definitions from the surrounding OrangeFS kernel headers. Integrated broadly by `dir.c`, `file.c`, `inode.c`, `namei.c`, and other modules for consistent handle diagnostics.

Risks: This is an implementation in a header, not a `static inline`; including it in multiple translation units would create duplicate global definitions unless the build includes it in exactly one C file or uses special rules. It uses `sprintf` repeatedly with no length argument and assumes `s` is valid and large enough. It assumes a particular 64-bit handle encoding and byte ordering. The UUID dash positions appear to insert after byte indexes 4, 6, 8, and 10, which differs from the canonical 4-2-2-2-6 byte grouping described in the comment if interpreted literally from zero-based indexes.

Test signals: Unit-test formatting for legacy 64-bit handles, full 128-bit handles, all-zero handles, and boundary byte values. Build-test inclusion patterns to catch duplicate symbol issues. Run with small or NULL buffers only under defensive/fuzz tests to confirm callers enforce `HANDLESTRINGSIZE`.
