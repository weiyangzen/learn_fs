# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_c62x/adf_c62x_hw_data.c

## Purpose
This file initializes Gen2 C62x PF hardware metadata. It is structurally similar to the C3xxx file but describes up to five accelerators, ten AEs, C62x BAR IDs, C62x SKU rules, fixed arbiter maps, SR-IOV thread mapping dimensions, clock measurement range, and firmware names.

## Important APIs, Types, And Functions
Public functions are `adf_init_hw_data_c62x()` and `adf_clean_hw_data_c62x()`. Important helpers include `get_accel_mask()`, `get_ae_mask()`, `get_ts_clock()`, `measure_clock()`, `get_misc_bar_id()`, `get_etr_bar_id()`, `get_sram_bar_id()`, `get_sku()`, `adf_get_arbiter_mapping()`, and `configure_iov_threads()`.

## Control Flow
Initialization populates class/instance, bank/ring geometry, accelerator/AE counts, Gen2 ring service map, IRQ callbacks, Gen2 error correction/capabilities/CSR/DC/PFVF ops, BAR ID callbacks, SKU logic, firmware names, admin/arbiter callbacks, Gen2 interrupts, FLR reset, SSM watchdog, SR-IOV disable, config, clock measurement, heartbeat, and arbiter mapping. AE mask calculation disables two AEs per disabled accelerator derived from fuses/straps.

## State And Persistence Behavior
The mutable state is the runtime `hw_data` object and static C62x class instance count. Fuse/strap-derived masks and measured clock persist in memory for the device lifetime.

## Dependencies And Integration Points
It depends on Gen2 config, CSR, PF/VF, admin, clock, heartbeat, common driver, firmware loader, and compression operations. It is called by the C62x PCI driver.

## Risks
SKU detection depends solely on AE count: 8 maps to SKU2 and 10 to SKU4. Wrong fuse/strap or BAR constants affect the whole device. Static thread-to-arbiter maps must match firmware scheduling assumptions.

## Test Signals
Probe should report expected SKU for 8/10 AEs, measure AE clock within 533-800 MHz, load `qat_c62x` firmware, register algorithms, support SR-IOV thread mapping, and survive reset/heartbeat checks.
