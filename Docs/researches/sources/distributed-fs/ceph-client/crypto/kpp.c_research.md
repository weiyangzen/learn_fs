<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/kpp.c -->
# sources/distributed-fs/ceph-client/crypto/kpp.c

Purpose: Implements the kernel crypto frontend/type plumbing for Key-agreement Protocol Primitives (KPP), such as Diffie-Hellman style algorithms.

Important APIs/types/functions: `crypto_kpp_type` defines type metadata, report/proc callbacks, init/free hooks, and layout offsets. `crypto_alloc_kpp()`, `crypto_grab_kpp()`, and `crypto_has_kpp()` expose lookup/spawn helpers. `crypto_register_kpp()`, `crypto_unregister_kpp()`, and `kpp_register_instance()` register raw algorithms and template instances. `crypto_kpp_init_tfm()` and `crypto_kpp_exit_tfm()` call algorithm-specific init/exit hooks.

Control flow: Registration calls `kpp_prepare_alg()` to set `cra_type` and KPP flags before registering with the core. Allocation uses `crypto_alloc_tfm()` with `crypto_kpp_type`. Transform init installs an exit wrapper if the algorithm has one, then calls the algorithm init hook. Instance registration requires an instance free callback before registering with the template core.

State and persistence behavior: This file stores no per-algorithm key material itself. It controls transform lifetime state through the embedded `crypto_tfm` and algorithm callbacks. KPP algorithm objects are registered in the global crypto registry.

Dependencies and integration points: Includes internal KPP APIs, cryptouser netlink reporting, `/proc/crypto` reporting, and shared crypto internal registry helpers. Consumers include key agreement implementations and templates that spawn KPP children.

Risks: Frontend layout offsets must match `struct crypto_kpp` and `struct kpp_alg`. Missing `inst->free` would leak template instances, so it is warned/rejected. Algorithm init/exit callbacks are trusted to manage private state and must be paired correctly.

Test signals: KPP algorithm registration/unregistration, `crypto_alloc_kpp()` lookup, template spawn with `crypto_grab_kpp()`, `/proc/crypto` and netlink reports, algorithms with and without init/exit hooks, and instance free callback validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/kpp.c -->
