# sources/distributed-fs/ceph-client/drivers/reset/spacemit/reset-spacemit-k3.c

Purpose: SpacemiT K3 reset table driver for MPMU, APBC, APMU, and DCIU domains using the common CCU reset implementation.

Important APIs/types/functions: K3 domain arrays map `spacemit,k3-resets.h` reset IDs to syscon register offsets and assert/deassert masks. `K3_AUX_DEV_ID()` creates auxiliary IDs named `spacemit_ccu.k3-*-reset`; each carries a `ccu_reset_controller_data` pointer. The auxiliary driver probes through `spacemit_reset_probe()`.

Control flow: parent K3 CCU auxiliary devices instantiate per-domain reset controllers. Assert/deassert behavior is common regmap mask writing.

State and persistence: hardware CCU bits persist reset state; software only provides static tables and auxiliary driver registration.

Dependencies and integration: K3 syscon headers, reset dt-bindings, auxiliary bus, common SpacemiT reset code, and parent CCU.

Risks and test signals: the large APMU table is binding-sensitive; sparse or duplicated IDs would expose wrong masks. Test each domain auxiliary device, table count vs binding end values, CPU/UCIE/PCIe reset polarity, and all build modes.
