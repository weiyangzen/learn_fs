# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/ingenic/ingenic_ecc.h

Purpose: this internal header defines the common interface between the Ingenic NAND controller, the shared ECC provider layer, and the SoC-specific ECC/BCH engines.

Important APIs, types, and functions: `struct ingenic_ecc_params` carries ECC step size, bytes, and strength. Public declarations include `ingenic_ecc_calculate()`, `ingenic_ecc_correct()`, `ingenic_ecc_release()`, `of_ingenic_ecc_get()`, and `ingenic_ecc_probe()` when `CONFIG_MTD_NAND_INGENIC_ECC` is enabled. Disabled-config stubs return `-ENODEV` or no-op. `struct ingenic_ecc_ops` defines provider callbacks, and `struct ingenic_ecc` stores device, ops, MMIO base, clock, and mutex.

Control flow: consumers include this header and treat ECC providers uniformly. When hardware ECC support is compiled out, calls compile but fail cleanly through stubs. When enabled, provider drivers initialize a `struct ingenic_ecc` through `ingenic_ecc_probe()` and expose ops to the NAND controller through the DT phandle lookup path.

State and persistence: the header itself has no runtime state, but it defines the persistent in-memory ECC provider state and the per-call parameter contract used by all three SoC engines.

Dependencies and integration points: the header depends on Linux error, mutex, type, and compiler definitions, plus forward declarations for clocks, devices, platform devices, and DT nodes. It is a local driver-internal ABI; changes must be coordinated across `ingenic_nand_drv.c`, `ingenic_ecc.c`, and the JZ ECC provider files.

Risks: the compile-out stubs make missing hardware ECC support look like a runtime `-ENODEV` rather than a build failure. The parameter structure is intentionally generic, so provider-specific limits must be enforced in provider reset/config code rather than in the common API. The include guard name contains `INTERNAL`, which accurately signals local use but does not prevent accidental wider inclusion.

Test signals: build coverage should include `CONFIG_MTD_NAND_INGENIC_ECC=y/m/n`. Runtime tests should validate that each provider honors the same size/bytes/strength contract and that disabled builds fail the NAND hardware-ECC path predictably.
