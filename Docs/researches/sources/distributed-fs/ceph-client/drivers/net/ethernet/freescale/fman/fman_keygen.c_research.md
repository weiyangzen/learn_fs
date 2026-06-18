# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/fman_keygen.c

## Purpose

`fman_keygen.c` initializes and programs the FMan KeyGen hardware, specifically the scheme and port binding machinery used here for RX hashing/spreading across frame queues. It provides a small exported interface for global KeyGen initialization and per-port hash scheme setup.

## Important APIs, Types, And Functions

The file defines KeyGen register layouts (`struct fman_kg_scheme_regs`, `struct fman_kg_pe_regs`, `struct fman_kg_regs`), software scheme state (`struct keygen_scheme`), and driver state (`struct fman_keygen`). Exported functions are `keygen_init()` and `keygen_port_hashing_init()`.

Internal helpers include `keygen_write_ar_wait()` for indirect action-register operations, builders for scheme/port/classification-plan action words, `keygen_write_sp()`, `keygen_write_cpp()`, `keygen_write_scheme()`, `get_free_scheme_id()`, `get_scheme()`, `keygen_bind_port_to_schemes()`, and `keygen_scheme_setup()`.

## Control Flow

`keygen_init()` allocates driver state, stores the MMIO base, writes global defaults, clears global default values, iterates over all 64 hardware ports to clear scheme and classification-plan bindings, enables all scheme interrupts, and sets the global enable bit. FMan core calls this during `fman_init()` after the parser/BMI/QMI blocks are initialized.

`keygen_port_hashing_init()` validates a nonzero 24-bit base FQID and power-of-two hash size, finds a free scheme, clears its software state, fills hard-coded IPv4/L4/IPsec SPI extraction/hash configuration, writes the scheme through indirect registers, marks it used, then binds the hardware port to the scheme.

## State And Persistence Behavior

Software state tracks 32 schemes in memory and whether each is used, its bound hardware port, base FQID, hash queue count, symmetric hash flag, hash shift, and match vector. Hardware state is persisted in KeyGen registers and port entries until reset or overwritten. No explicit free/unbind API exists in this subset, so schemes are effectively one-way allocations after initialization.

## Dependencies And Integration Points

The file depends on Linux IO and slab allocation, and on `fman_keygen.h`. It is integrated by `fman.c`, which passes the KeyGen register offset and stores the returned handle. Port/RX code outside this subset can call `keygen_port_hashing_init()` through the exported symbol to enable hash distribution for a hardware port.

## Risks And Edge Cases

`keygen_write_ar_wait()` busy-waits without a timeout, so hardware that never clears GO can hang the caller. The hash configuration is hard-coded and notes that symmetric hash is disabled because spreading did not work in tests. There is no rollback if scheme setup succeeds but port binding fails, leaving a used unbound scheme. This snapshot contains an apparent duplicated partial line in `keygen_scheme_setup()` around `KG_SCH_DEF_USE_KGSE_DV_1`, which should be caught by compilation.

## Test Signals

Compile tests should validate the apparent malformed line. Unit-style hardware mocks should test action-register error handling, scheme exhaustion, invalid FQID and non-power-of-two hash sizes, successful register programming fields, and binding failure behavior. Runtime tests should verify packets distribute over the configured queue range and that reset/reprobe clears stale scheme bindings.
