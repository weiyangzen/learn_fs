# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/fman_keygen.h

## Purpose

`fman_keygen.h` exposes the minimal KeyGen API used by FMan core and port code. It keeps both `struct fman_keygen` and `struct fman_kg_regs` opaque while declaring initialization and per-port hashing configuration.

## Important APIs, Types, And Functions

The header forward-declares `struct fman_keygen` and `struct fman_kg_regs`. It declares `keygen_init(struct fman_kg_regs __iomem *keygen_regs)` and `keygen_port_hashing_init(struct fman_keygen *keygen, u8 hw_port_id, u32 hash_base_fqid, u32 hash_size)`.

## Control Flow

FMan core calls `keygen_init()` during hardware initialization and stores the returned handle. Later code can call `keygen_port_hashing_init()` to allocate a scheme and bind it to a hardware port for RX queue spreading.

## State And Persistence Behavior

No state lives in the header. The opaque handle represents software scheme ownership and points at persistent hardware registers programmed by the implementation.

## Dependencies And Integration Points

The header depends on Linux IO annotations and integer types. It is included by `fman.c` and any port code that configures RX hashing.

## Risks And Edge Cases

The API has no destroy, unbind, or scheme-release function, so users cannot recover a scheme through this interface after failed or obsolete configuration. The hash-size and FQID constraints are only documented/enforced by the implementation.

## Test Signals

Compile tests should cover users with sparse/IO annotations. Integration tests should verify callers do not pass a NULL KeyGen handle and that invalid hash parameters return errors without consuming schemes.
