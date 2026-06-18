<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/crypto/Kconfig -->
# sources/distributed-fs/ceph-client/arch/sparc/crypto/Kconfig

## Purpose
This Kconfig file exposes SPARC64 crypto-opcode accelerated cipher modules.

## Important APIs, Types, and Functions
It defines `CRYPTO_AES_SPARC64` and `CRYPTO_CAMELLIA_SPARC64`, both dependent on `SPARC64`, `KERNEL_MODE_NEON`, and their generic cipher dependencies, and both selecting the matching crypto manager support.

## Control Flow
When enabled, the symbols cause the SPARC crypto Makefile to build AES or Camellia opcode glue and assembly. Runtime module init still checks hardware capability before registering algorithms.

## State and Persistence Behavior
It persists choices in `.config` and controls which modules or built-ins are compiled. Runtime availability depends on CPU features.

## Dependencies and Integration Points
It integrates with the kernel crypto API, SPARC64 opcode detection, and module autoload through OF device aliases.

## Risks
Building the module does not guarantee the processor exposes the opcode; init must return `-ENODEV` on unsupported hardware. Missing generic cipher dependencies would leave registered modes without shared crypto infrastructure.

## Test Signals
Build with AES and Camellia enabled as modules and built-ins. On hardware with and without crypto opcodes, verify module load success/failure, algorithm registration, and crypto selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/crypto/Kconfig -->
