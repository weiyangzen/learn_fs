# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_c3xxx/adf_c3xxx_hw_data.c

## Purpose
This file initializes hardware metadata for C3xxx Gen2 QAT PF devices. It computes accelerator and AE masks from fuse/softstrap registers, defines fixed arbiter thread mapping, identifies SKU, measures AE clock, configures SR-IOV thread ownership, and wires common Gen2 lifecycle callbacks into `struct adf_hw_device_data`.

## Important APIs, Types, And Functions
The exported functions are `adf_init_hw_data_c3xxx()` and `adf_clean_hw_data_c3xxx()`. Important helpers include `get_accel_mask()`, `get_ae_mask()`, `get_ts_clock()`, `measure_clock()`, BAR ID callbacks, `get_sku()`, `adf_get_arbiter_mapping()`, and `configure_iov_threads()`.

## Control Flow
Initialization sets class/instance, 16 ETR banks, 16 rings per bank, 3 accelerators, 6 AEs, Gen2 ring layout, IRQ callbacks, error correction, mask/capability callbacks, BAR callbacks, admin/arbiter hooks, firmware names, Gen2 PF/VF ops, SSM watchdog, SR-IOV disable, Gen2 config, clock measurement, heartbeat counters, and DC/CSR ops. AE mask calculation disables two AEs for each disabled accelerator.

## State And Persistence Behavior
The file mutates only runtime `hw_data` and the static C3xxx class instance count. Fuse/strap-derived masks persist in `hw_data` for the bound device lifetime.

## Dependencies And Integration Points
It depends on Gen2 config, Gen2 CSR and hardware-data helpers, Gen2 PF/VF ops, admin communication, common QAT clock measurement, heartbeat, and firmware loader paths using `qat_c3xxx.bin` and `qat_c3xxx_mmp.bin`.

## Risks
Fuse/strap interpretation drives both accelerator mask and AE mask; a wrong shift or disabled-accelerator propagation misrepresents hardware. Clock measurement accepts a min/max range and affects heartbeat timing. Static arbiter maps must match firmware thread roles.

## Test Signals
Probe on C3xxx hardware should report SKU4 for 6 AEs, load firmware, register algorithms, measure clock within range, run heartbeat checks, support SR-IOV thread configuration, and survive reset/arbiter restart.
