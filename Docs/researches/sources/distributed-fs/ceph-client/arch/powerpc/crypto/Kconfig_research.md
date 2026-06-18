# sources/distributed-fs/ceph-client/arch/powerpc/crypto/Kconfig

Purpose: declares PowerPC crypto acceleration configuration choices and CPU feature dependencies.

Important APIs/types/functions: no exported symbols; behavior is expressed through build rules or linker script sections. Source size is 64 lines / 2103 bytes.

Control flow is Kconfig/Makefile selection: CPU feature symbols choose which objects are compiled, Perl generators emit assembly, and module registration code later exposes the algorithms to the crypto API.

State and persistence: State is per-transform key material, per-request IV/tweak/tag/hash state, and CPU vector/SPE enable state; persistent registration state lives in the crypto API until module exit.

Dependencies and integration: Includes/dependencies: none or build-tool implicit dependencies. Integration points are the Linux crypto API, PowerPC CPU feature checks, vector/SPE save-restore helpers, generated assembly symbols, scatterwalk/skcipher/aead walkers, and module registration.

Risks and test signals: Risks include wrong CPU feature dependencies, missing generated objects, module alias conflicts, or stale assembly generator output. Test signals are all relevant PowerPC crypto Kconfig build combinations and crypto selftest availability at boot/module load.
