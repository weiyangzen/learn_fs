# sources/distributed-fs/ceph-client/tools/testing/selftests/sgx/Makefile

## Purpose
Builds the x86_64 SGX selftest host binary and test enclave image. It gates the build with `../x86/check_cc.sh` so SGX tests are only generated when a 64-bit x86 program can be compiled.

## Important APIs, types, and functions
Defines `TEST_CUSTOM_PROGS := $(OUTPUT)/test_sgx` and `TEST_FILES := $(OUTPUT)/test_encl.elf`. Host objects are `main.o`, `load.o`, `sigstruct.o`, `call.o`, and `sign_key.o`, linked with `-lcrypto` and no executable stack. The enclave is built from `test_encl.c` and `test_encl_bootstrap.S` using freestanding static PIE flags and linker script `test_encl.lds`.

## Control flow
When `CAN_BUILD_X86_64` is true, `all` builds both the host runner and enclave ELF. Individual object rules compile host/enclave sources into `$(OUTPUT)`. `OBJCOPY` defaults to cross objcopy but is not directly used in the visible rules.

## State and persistence
Writes only build outputs under `$(OUTPUT)` and lists them in `EXTRA_CLEAN`. It does not persist runtime state.

## Dependencies and integration points
Uses kselftest `../lib.mk`, kernel headers via `tools/include`, OpenSSL libcrypto, x86 compiler checks, and SGX linker assets in the same directory.

## Risks
The freestanding enclave flags and `-Werror` make the build sensitive to compiler and OpenSSL deprecation warnings; `sigstruct.c` locally suppresses OpenSSL 3 deprecation warnings. Cross-compile environments need a matching x86_64 toolchain.

## Test signals
Successful build produces `test_sgx` and `test_encl.elf`; unsupported architecture produces no SGX test binary.
