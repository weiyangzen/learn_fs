# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-designware-pcidrv.c

## Purpose
PCI front end for DesignWare I2C controllers on Intel Medfield/Merrifield/BayTrail/Haswell/CherryTrail/Elkhart Lake and AMD Navi GPUs. It maps PCI resources, applies platform timing quirks, and delegates controller operation to the shared DesignWare core.

## Important APIs, Types, And Functions
`struct dw_scl_sda_cfg` holds legacy timing constants. `struct dw_pci_controller` describes bus numbering, flags, setup callback, and clock-rate callback. Setup helpers include `mfld_setup()`, `mrfld_setup()`, `navi_amd_setup()`, and clock callbacks. Probe/remove are `i2c_dw_pci_probe()` and `i2c_dw_pci_remove()`.

## Control Flow
PCI probe enables the device, maps BAR0, allocates `dw_i2c_dev`, allocates IRQ vectors, fills clock/base/device/IRQ/flag fields, runs optional controller setup, parses firmware timing, configures DesignWare mode, applies legacy timing constants, initializes adapter metadata, and calls `i2c_dw_probe()`. For AMD Navi GPUs it also creates a CCGX UCSI I2C client. Runtime PM autosuspend is enabled after registration. Remove disables the controller, forbids runtime PM, gets the device, and unregisters the adapter.

## State And Persistence
Controller selection and timing constants are static tables. Per-device state is `dw_i2c_dev` in PCI driver data plus optional UCSI client stored in `dev->slave`. Runtime PM state persists while bound.

## Dependencies And Integration Points
Depends on PCI core, IRQ vectors, power-supply software node for dGPU scope, `i2c-ccgx-ucsi.h`, runtime PM, and shared DesignWare namespaces. PCI IDs are the primary binding mechanism.

## Risks
Some legacy controllers use hard-coded bus numbers and HCNT/LCNT values. AMD Navi runs polling mode and uses a special transfer quirk. UCSI client creation failure must unregister the adapter. PCI IRQ allocation and BAR mapping failures need clean devm/pcim rollback.

## Test Signals
Test all PCI ID groups for bus numbering, IRQ vector setup, adapter registration, timing constants, AMD Navi UCSI creation and polling transfers, runtime autosuspend, and remove after active PM.
