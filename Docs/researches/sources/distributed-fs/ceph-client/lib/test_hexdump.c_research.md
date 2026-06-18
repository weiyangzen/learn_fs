
# sources/distributed-fs/ceph-client/lib/test_hexdump.c

## Purpose

This module validates `hex_dump_to_buffer()` formatting across row sizes, group sizes, ASCII/no-ASCII modes, endian-sensitive grouping, and truncated output buffers.

## Important APIs, Types, And Functions

It defines fixed binary input `data_b`, ASCII projection `data_a`, and expected strings for group sizes 1, 2, 4, and 8 in little- and big-endian order. `test_hexdump_prepare_test()` constructs the expected string. `test_hexdump()` compares full outputs. `test_hexdump_overflow()` checks return lengths and truncation behavior for every buffer size up to `TEST_HEXDUMP_BUF_SIZE`.

## Control Flow And State

Init picks random row sizes and lengths, runs normal formatting tests with and without ASCII, then exhaustively checks overflow behavior for all buffer lengths in both modes. It tracks `total_tests` and `failed_tests` in init-only data and returns `-EINVAL` if any mismatch occurs.

## Dependencies And Integration Points

The test depends on `hex_dump_to_buffer()`, random helpers, endian configuration, string/memory helpers, and module init. It is self-contained and reports via kernel logs.

## Risks And Test Signals

Random length choices provide variation but can make an exact failing case require the log for reproduction. Strong signals are `all N tests passed` or detailed `Result`/`Expect` mismatch lines including length, row size, group size, and buffer length.
