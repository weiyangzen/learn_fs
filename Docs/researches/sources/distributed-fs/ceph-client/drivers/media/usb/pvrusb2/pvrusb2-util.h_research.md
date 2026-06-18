# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-util.h

Purpose: small endian packing helper header for pvrusb2 command buffers. It provides macros to decompose and compose 32-bit values in little-endian or big-endian byte order.

Important APIs, types, and functions: `PVR2_DECOMPOSE_LE(t,i,d)` writes `d` into four bytes starting at `t[i]` least-significant byte first. `PVR2_DECOMPOSE_BE(t,i,d)` writes most-significant byte first. `PVR2_COMPOSE_LE(t,i)` reads four bytes as a little-endian `u32`. `PVR2_COMPOSE_BE(t,i)` reads four bytes as a big-endian `u32`.

Control flow: macros expand inline at call sites. In this subset, `pvrusb2-hdw.c` uses the little-endian helpers for FX2 register read/write command buffers.

State and persistence: stateless macros. They mutate only the caller-provided byte array for decomposition.

Dependencies and integration points: depends on `u32` being visible at the inclusion site. Used by low-level hardware command paths that communicate with the encoder/FX2 firmware.

Risks: arguments are evaluated multiple times in some macro expressions, so callers should avoid side-effecting arguments for `t`, `i`, or `d`. No bounds checking is performed; callers must ensure at least four bytes are valid. Endianness is explicit and independent of host CPU order.

Test signals: compile low-level command users; verify register write/read byte order against USB traces; static analysis for side-effecting macro arguments and buffer bounds.
