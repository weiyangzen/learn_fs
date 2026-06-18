# sources/distributed-fs/ceph-client/lib/xz/xz_dec_test.c

## Purpose
Optional developer module exposing a character device `xz_dec_test` that accepts `.xz` input, decodes it with the in-kernel decoder, discards output, and logs CRC32/status diagnostics.

## APIs and control flow
Defines file operations `xz_dec_test_open`, `xz_dec_test_release`, and `xz_dec_test_write`, plus module init/exit. Init allocates an `XZ_PREALLOC` decoder with 1 MiB dictionary and registers a dynamic character device. Open enforces one active user, resets decoder/buffers/CRC. Write copies user input into a 1 KiB buffer, calls `xz_dec_run`, updates CRC over produced bytes, and reports status. Release reports truncation if the stream did not finish.

## State, dependencies, and integration
Global module state includes `device_major`, `device_is_open`, decoder `state`, decoder `ret`, fixed input/output buffers, an `xz_buf`, and running CRC. Dependencies include VFS char devices, usercopy, kernel CRC32, and `linux/xz.h`.

## Risks and test signals
Single-open global state is sufficient for a test module but not a general device pattern. It logs to the kernel log and treats trailing data as garbage, so it should not be production-enabled. Test with known `.xz` files, matching CRCs, truncated/corrupt/unsupported files, and trailing garbage.
