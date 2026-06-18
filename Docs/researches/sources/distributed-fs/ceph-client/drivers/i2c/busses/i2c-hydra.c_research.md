# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-hydra.c

Purpose: Apple Hydra Mac I/O PCI I2C adapter using bit-banged access to CachePD lines. It is a small legacy driver that maps the Hydra register block and registers a single `i2c-algo-bit` adapter.

Important APIs/types/functions: global `hydra_bit_data` defines `setsda`, `setscl`, `getsda`, `getscl`, `udelay`, and timeout callbacks. `hydra_adap` is the global adapter. `hydra_probe()` maps PCI BAR 0, reserves the CachePD region, clears output-enable bits, and calls `i2c_bit_add_bus()`. `hydra_remove()` clears lines, unregisters the adapter, unmaps BAR memory, and releases the region.

Control flow: setting SDA/SCL high releases the corresponding output-enable bit; setting low clears the data bit and enables the output driver. Reads sample CachePD data bits. Probe uses the Apple Hydra PCI ID, reserves only the CachePD register window, maps the BAR, initializes line state to released, and publishes the adapter.

State and persistence: state is mostly global: the adapter, algorithm data, and mapped Hydra pointer stored in `hydra_bit_data.data`. Hardware state persists in CachePD output-enable and line bits. There is no per-device allocation, PM, or multi-instance isolation.

Dependencies and integration: depends on PCI device matching for Apple Hydra, `asm/hydra.h`, MMIO accessors, `i2c-algo-bit`, and legacy Mac hardware definitions.

Risks: global adapter/data makes the driver effectively single-instance. It does not call `pci_enable_device()`, which may be acceptable for this legacy platform but is unusual. Resource reservation and BAR mapping are manual. Electrical behavior depends on correct interpretation of output-enable bits as open-drain line release.

Test signals: PCI probe on Apple Hydra hardware, line release after probe/remove, successful bit-bang transfers through `i2c_bit_add_bus()`, timeout behavior from `i2c-algo-bit`, and module unload cleanup.
