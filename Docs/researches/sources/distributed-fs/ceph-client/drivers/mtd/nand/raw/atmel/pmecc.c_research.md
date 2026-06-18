# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/atmel/pmecc.c

Purpose: implements the Atmel PMECC hardware-assisted BCH ECC engine and PMERRLOC error-location helper. It exposes a reusable ECC engine for NAND controller clients using either a standalone `ecc-engine` phandle or legacy resources embedded in a NAND node.

Important APIs/types/functions: private state uses `struct atmel_pmecc`, `struct atmel_pmecc_caps`, `struct atmel_pmecc_user`, and `struct atmel_pmecc_gf_tables`. Exported APIs include `devm_atmel_pmecc_get`, `atmel_pmecc_create_user`, `atmel_pmecc_enable`, `atmel_pmecc_disable`, `atmel_pmecc_wait_rdy`, `atmel_pmecc_correct_sector`, `atmel_pmecc_correct_erased_chunks`, and `atmel_pmecc_get_generated_eccbytes`.

Control flow: probe maps PMECC/PMERRLOC resources, optionally configures PMECC clocking, disables interrupts, and resets hardware. User creation normalizes requested geometry, allocates/caches Galois-field tables, and lays out BCH scratch arrays. Read/write users enable PMECC under a mutex, wait for ready, then extract ECC bytes or correct sectors by generating syndromes, computing sigma, using PMERRLOC roots, and flipping bits.

State and persistence: engine state is MMIO mappings, caps, and a mutex. Global GF tables are lazily shared for 512B and 1024B sectors. Per-user state caches register values, ECC bytes per sector, ISR bits, and scratch arrays.

Dependencies/integration: platform/OF lookup, MMIO polling, raw NAND constants, and the Atmel NAND controller. Exports symbols for module clients.

Risks/test signals: invalid geometry, GF table races, PMERRLOC timeout, root-degree mismatch, bit-position bounds, and lock/unlock discipline. Test BCH correction counts, uncorrectable errors, erased-chunk policy, legacy/phandle acquisition, and timeout paths.
