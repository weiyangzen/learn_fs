# sources/distributed-fs/ceph-client/drivers/nvmem/sc27xx-efuse.c

Purpose: Spreadtrum SC27xx PMIC eFuse read-only NVMEM provider using parent regmap and hardware spinlock synchronization.

Important APIs/types/functions: `struct sc27xx_efuse_variant_data` selects PMIC module-enable register. `sc27xx_efuse_lock()` combines a mutex with raw hardware spinlock. `sc27xx_efuse_read()` enables the controller, waits standby, programs block index, starts read, waits done, reads data, clears done, and disables the controller.

Control flow: probe gets parent regmap, reads base from `reg`, obtains a hwspinlock ID and requests it, initializes mutex and variant data, and registers a byte-granular read-only NVMEM sized as 32 two-byte blocks. Reads serialize across local and remote subsystems before touching PMIC registers.

State/persistence: eFuse contents persist in PMIC hardware. Driver state tracks regmap, base, hwspinlock, mutex, and variant register offsets.

Dependencies/integration: compatibles `sprd,sc2731-efuse` and `sprd,sc2730-efuse`; depends on parent regmap, OF hwspinlock binding, and NVMEM fixed cells.

Risks: reads are limited to at most one two-byte block; larger NVMEM requests return `-EINVAL`. The block-index check uses `>` rather than `>=`, so index 32 passes the local test even though max count is 32; NVMEM size should prevent that offset. Remote synchronization depends on the hwspinlock being shared correctly.

Test signals: hwspinlock timeout, standby/read-done poll timeout, variant module-enable address selection, one-byte and two-byte reads with offset shifts, and invalid-size rejection.
