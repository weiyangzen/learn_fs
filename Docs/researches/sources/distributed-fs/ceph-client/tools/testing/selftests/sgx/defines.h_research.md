# sources/distributed-fs/ceph-client/tools/testing/selftests/sgx/defines.h

## Purpose
Shared SGX selftest definitions for page sizing, compiler attributes, kernel SGX UAPI inclusion, and host/enclave operation payloads.

## Important APIs, types, and functions
Defines `PAGE_SIZE`, `PAGE_MASK`, `__aligned`, `__packed`, `__used`, and `__section`. Includes SGX architecture and UAPI headers. `enum encl_op_type` enumerates operations executed inside the enclave: buffer get/put, arbitrary address get/put, no-op, `EACCEPT`, `EMODPE`, and TCS initialization. The `struct encl_op_*` payloads share `struct encl_op_header`.

## Control flow
This header has no executable flow; `main.c` populates operation structs and `test_encl.c` dispatches by `header.type`.

## State and persistence
Operation structures carry transient command state across enclave entry. `ret` in `struct encl_op_eaccept` is written by enclave code and read by host tests.

## Dependencies and integration points
Central contract between host test code, enclave C code, and assembly bootstrap. It also imports kernel SGX constants such as page types and ENCLU function encodings.

## Risks
The host/enclave ABI depends on exact struct layout and 64-bit fields. Header path depth is tied to this Linux source tree layout.

## Test signals
Every SGX runtime test indirectly validates these definitions when operation dispatch succeeds and expected magic values or ENCLU return codes are observed.
