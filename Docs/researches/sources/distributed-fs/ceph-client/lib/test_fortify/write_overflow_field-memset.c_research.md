
# sources/distributed-fs/ceph-client/lib/test_fortify/write_overflow_field-memset.c

## Purpose

This negative test checks field-specific destination overflow detection for `memset()`.

## Important APIs, Control Flow, And State

`TEST` is `memset(instance.buf, 0x42, sizeof(instance.buf) + 1)`, a one-byte overrun of the struct field.

## Dependencies, Risks, And Test Signals

It targets the fortified `memset()` field-size path. The expected compile signal is `__write_overflow_field`, proving adjacent struct members are protected from constant-size overwrites.
