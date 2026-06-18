# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/ingenic/ingenic_ecc.c

Purpose: this is the common Ingenic ECC provider layer used by the Ingenic NAND controller and the JZ4740/JZ4725B/JZ4780 ECC engine drivers. It abstracts SoC-specific ECC calculation/correction operations behind `struct ingenic_ecc_ops` and handles DT phandle lookup, clock lifetime, register mapping, and driver data setup.

Important APIs, types, and functions: exported entry points are `ingenic_ecc_calculate()`, `ingenic_ecc_correct()`, `of_ingenic_ecc_get()`, `ingenic_ecc_release()`, and `ingenic_ecc_probe()`. `ingenic_ecc_get()` resolves a provider `device_node` to a `platform_device`, verifies driver data is ready, enables the provider clock, and returns the `struct ingenic_ecc`.

Control flow: SoC ECC platform drivers use `ingenic_ecc_probe()` as their probe function or call it from a wrapper. That probe allocates the shared state, fetches match-data ops, maps the MMIO resource, disables the hardware, gets the clock, initializes the mutex, stores `dev`, and publishes drvdata. The NAND controller calls `of_ingenic_ecc_get()` against its node; the helper first checks `ecc-engine`, then deprecated `ingenic,bch-controller`, then enables the provider clock and returns it. Calculate/correct calls simply dispatch through the provider ops.

State and persistence: `struct ingenic_ecc` persists the device pointer, ops, base register mapping, clock handle, and mutex. Clock enable state is reference-like: get enables, release disables and drops the provider device reference. Per-operation mutable state belongs to provider-specific registers and is serialized by the provider mutex.

Dependencies and integration points: the file depends on OF platform lookup, common clock APIs, platform resources, module exports, and `ingenic_ecc.h`. It is linked into the main `ingenic_nand` object when `CONFIG_MTD_NAND_INGENIC_ECC` is enabled, while provider modules supply the actual ops via OF match data.

Risks: `clk_prepare_enable()` return value is ignored in `ingenic_ecc_get()`, so clock-enable failure would not be reported to the NAND controller. Provider lookup returns `-EPROBE_DEFER` until drvdata exists, so boot ordering affects NAND probe. There is no module reference acquisition around provider ops beyond `get_device()`, so provider unbind behavior depends on platform-driver lifetime expectations.

Test signals: useful tests are provider probe with valid/invalid match data, DT lookup through both `ecc-engine` and deprecated phandle names, clock enable/disable balance across NAND bind/remove, probe deferral when provider is absent, and provider calculation/correction dispatch.
