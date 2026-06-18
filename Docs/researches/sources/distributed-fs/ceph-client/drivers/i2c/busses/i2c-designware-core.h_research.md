# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-designware-core.h

## Purpose
Shared definitions for the DesignWare I2C driver family. It provides register offsets, bit definitions, abort codes, model/access flags, the `dw_i2c_dev` state object, exported function prototypes, and small inline helpers used by common, master, slave, PCI, platform, and arbitration glue.

## Important APIs, Types, And Functions
`struct dw_i2c_dev` is the central type, carrying device/regmap/MMIO pointers, clocks, reset, master/slave state, transfer pointers and counters, errors, IRQ, flags, adapter, timing values, FIFO depths, lock callbacks, recovery info, and model quirks. Important macros include `DW_IC_*` register offsets, interrupt masks, abort bits, `STATUS_*`, `ACCESS_*`, `MODEL_*`, `DW_IC_MASTER`, and `DW_IC_SLAVE`. Inline helpers include `__i2c_dw_enable()`, `__i2c_dw_disable_nowait()`, interrupt mask read/write wrappers, and `i2c_dw_configure()`.

## Control Flow
The header defines the contract among the family: front-end drivers allocate/fill `dw_i2c_dev`, call `i2c_dw_fw_parse_and_configure()`, `i2c_dw_configure()`, and `i2c_dw_probe()`, while common code calls master/slave hooks for mode-specific behavior. Compile-time conditionals provide slave and BayTrail/AMD PSP hooks only when enabled.

## State And Persistence
The header itself has no runtime state, but it defines all persistent in-memory state used by DesignWare adapters across probe, transfer, PM, and removal. `sw_mask` and `status` are software mirrors for hardware state.

## Dependencies And Integration Points
Includes Linux I2C, completion, regmap, PM, IRQ, and type headers. It is the integration point between generic DesignWare common code and platform-specific modules, including AMD UCSI, Wangxun, BayTrail, AMD PSP, and optional slave support.

## Risks
Any change to `dw_i2c_dev` or bit definitions can affect all front ends. `ACCESS_POLLING` changes interrupt mask semantics. Conditional prototypes must match Kconfig combinations. Hardware constants encode assumptions from the DesignWare databook and platform quirks.

## Test Signals
Compile coverage across platform, PCI, polling, slave-enabled, BayTrail, AMD PSP, AMD Navi GPU, and Wangxun configurations is the primary signal. Runtime tests should confirm interrupt mask behavior is identical in polling and IRQ modes where intended.
