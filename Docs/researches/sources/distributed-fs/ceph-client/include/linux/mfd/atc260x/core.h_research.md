## sources/distributed-fs/ceph-client/include/linux/mfd/atc260x/core.h

Purpose: This is the shared core interface for Actions Semi ATC260x PMIC MFD drivers. It ties variant register headers to a common `struct atc260x` runtime object and declares the match/probe entry points used by bus-specific front ends.

Important APIs, types, and constants: `enum atc260x_type` distinguishes ATC2603A, ATC2603C, and ATC2609A; `enum atc260x_ver` encodes silicon revisions A through H. `struct atc260x` stores parent device, regmap, regmap IRQ chip and data, a custom regmap mutex pointer, MFD cells, parent IRQ, chip type/version/name, revision register, and optional initialization register table. The exported functions are `atc260x_match_device()` and `atc260x_device_probe()`.

Control flow: A bus driver allocates/fills `struct atc260x`, creates a regmap, calls `atc260x_match_device()` to pick variant-specific cells, IRQ chip, revision register, and regmap configuration, then calls `atc260x_device_probe()` to initialize registers, IRQs, and MFD children.

State and persistence: Runtime state is in `struct atc260x`; hardware state is in the PMIC registers selected by the variant headers. The `init_regs` pointer represents boot-time register programming, not persistent kernel storage.

Dependencies and integration points: It includes the ATC2603C and ATC2609A variant headers, uses regmap/regmap-irq, MFD cells, device model, mutexes, and bus front ends.

Risks: Variant matching is central; a wrong `ic_type` or `rev_reg` will expose the wrong register map and child cells. Custom regmap locking must be consistent across all child accesses.

Test signals: Unit or probe tests should confirm each compatible string selects the expected `ic_type`, `ic_ver`, cell list, IRQ chip, and regmap config. Runtime validation includes child device creation, regmap IRQ registration, and init register writes.
