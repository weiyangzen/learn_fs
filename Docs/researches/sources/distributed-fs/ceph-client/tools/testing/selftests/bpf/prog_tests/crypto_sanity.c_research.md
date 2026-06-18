# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/crypto_sanity.c

## Purpose
Tests BPF crypto helper setup plus TC egress encryption/decryption sanity against Linux AF_ALG AES-ECB output.

## Important APIs, types, and functions
Uses `crypto_sanity.skel.h`, `crypto_basic.skel.h`, AF_ALG sockets (`socket(AF_ALG)`, `bind`, `setsockopt(ALG_SET_KEY)`, `accept`, `sendmsg` with `ALG_SET_OP`), `bpf_tc_hook_create()`, `bpf_tc_attach()`, `bpf_prog_test_run_opts()`, and network namespace helpers. `do_crypt_afalg()` computes reference ciphertext/plaintext.

## Control flow and state
`test_crypto_basic()` delegates to generated basic tests. `test_crypto_sanity()` creates a netns, configures IPv6 loopback, initializes AF_ALG, seeds BPF BSS key/algo/authsize, runs setup program, attaches encrypt TC program, sends UDP plaintext, compares BPF destination buffer against AF_ALG encryption, detaches, attaches decrypt program, sends ciphertext, and compares decrypted output. State includes netns, AF_ALG FDs, TC hook/filter state, skeleton BSS/data, and UDP sockets.

## Dependencies and integration points
Requires `ip` tooling, netns privilege, AF_ALG skcipher `ecb(aes)`, TC BPF support, loopback device, and generated skeletons. Integrated as two selftest entry points.

## Risks and test signals
Risks include unavailable crypto algorithm, namespace setup failure, TC hook cleanup, and fixed block-size assumptions. Passing signals are zero BSS status after setup/encrypt/decrypt and byte equality with AF_ALG reference output.
