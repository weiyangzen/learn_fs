<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/crypto/crop_devid.c -->
# sources/distributed-fs/ceph-client/arch/sparc/crypto/crop_devid.c

## Purpose
This small C fragment supplies Open Firmware module device IDs for SPARC crypto-opcode modules.

## Important APIs, Types, and Functions
It defines `crypto_opcode_match[]` with compatible string `sun4v-cwq` and exports it through `MODULE_DEVICE_TABLE(of, crypto_opcode_match)`.

## Control Flow
The file is included directly by AES and Camellia glue sources, so each module receives the same OF device table. Module autoload can then match firmware nodes advertising the crypto work queue/opcode capability.

## State and Persistence Behavior
The only state is a constant device-id table compiled into the module metadata.

## Dependencies and Integration Points
It depends on Linux OF module-device-table support and is integrated by textual inclusion from crypto glue files.

## Risks
Because it is included rather than linked separately, changes affect multiple modules. An incorrect compatible string would prevent module autoload even though manual loading could still work.

## Test Signals
Check `modinfo` aliases for AES and Camellia modules and verify OF-based autoload on systems exposing `sun4v-cwq`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/crypto/crop_devid.c -->
