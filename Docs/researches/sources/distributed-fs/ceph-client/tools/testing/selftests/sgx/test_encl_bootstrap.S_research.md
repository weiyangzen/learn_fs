# sources/distributed-fs/ceph-client/tools/testing/selftests/sgx/test_encl_bootstrap.S

## Purpose
Defines the enclave TCS pages, SSA pages, stacks, entry sequence, dynamic TCS entry, and EEXIT path for the SGX test enclave.

## Important APIs, types, and functions
Uses raw ENCLU encoding. Defines `.tcs` data for two initial TCS pages, `encl_entry`, `encl_dyn_entry`, `encl_entry_core`, SSA storage, and two stacks. Calls C function `encl_body`.

## Control flow
On enclave entry, the bootstrap derives the stack address from the TCS base in `rbx`, switches to the enclave stack, saves the caller return address after EENTER, calls `encl_body`, restores the caller stack, loads the EEXIT target into `rbx`, and executes ENCLU[EEXIT]. `encl_dyn_entry` supports dynamically created TCS pages whose stack is directly before the TCS.

## State and persistence
TCS, SSA, and stack pages are enclave pages initialized in the ELF and then measured/loaded by host code. Runtime stack and SSA state persist within enclave memory.

## Dependencies and integration points
Linked into `test_encl.elf` and relied on by `main.c` TCS tests and `test_encl.c` handlers.

## Risks
Bootstrap intentionally omits production-grade register cleansing and ABI initialization. TCS field offsets, stack derivation, and ENCLU register conventions must remain exact.

## Test signals
`tcs_entry` validates both initial TCS pages; `tcs_create` validates the dynamic entry path after creating a new TCS.
