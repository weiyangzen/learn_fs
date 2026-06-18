# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/bench_bpf_crypto.c

## Purpose

This benchmark measures BPF crypto helper throughput for encryption and decryption using a selected kernel crypto cipher and buffer length.

## Important APIs, Types, and Functions

CLI options are `--crypto-len` and `--crypto-cipher`. State lives in `input` and `ctx` with `crypto_bench` skeleton and selected program FD. Functions include `crypto_parse_arg()`, `crypto_validate()`, `crypto_setup()`, `crypto_encrypt_setup()`, `crypto_decrypt_setup()`, `crypto_measure()`, and `crypto_producer()`.

## Control Flow and Data Flow

Setup opens the skeleton, writes cipher/key/auth settings into BSS, creates random-ish input, sets rodata length, loads the skeleton, and runs the BPF setup program once through `bpf_prog_test_run_opts()`. Producers repeatedly run the selected encrypt or decrypt program with `.repeat = 64`; measurement atomically drains the BSS hit counter.

## State and Persistence Behavior

The crypto transform setup and counters live in the BPF program/skeleton for the benchmark process. Input buffer memory persists for producers. No files are stored.

## Dependencies and Integration Points

It depends on `crypto_bench.skel.h`, libbpf, `bpf_prog_test_run_opts()`, kernel BPF crypto kfunc/helper availability, and the kernel crypto API implementation for the requested cipher.

## Risks and Edge Cases

Argument parsing references `ctx.skel->bss->dst` before setup has opened the skeleton; this relies on compile-time type information through the skeleton pointer expression but would be fragile if rewritten. Cipher names longer than `MAX_CIPHER_LEN` are rejected, but BSS copy uses a 128-byte destination. Unsupported crypto helpers or ciphers fail during setup.

## Test Signals

Expected output is hit throughput for `crypto-encrypt` and `crypto-decrypt`; setup failures identify unsupported ciphers, invalid lengths, BPF load failure, or setup-program status errors.
