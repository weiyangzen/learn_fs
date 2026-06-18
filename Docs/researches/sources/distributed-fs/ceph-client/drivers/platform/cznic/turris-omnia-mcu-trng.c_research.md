<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/cznic/turris-omnia-mcu-trng.c -->
# sources/distributed-fs/ceph-client/drivers/platform/cznic/turris-omnia-mcu-trng.c

## Purpose

This optional feature registers the Turris Omnia MCU true random number generator with the Linux hwrng framework.

## Important APIs, Types, And Functions

`omnia_trng_irq_handler()` completes `trng_entropy_ready`. `omnia_trng_read()` waits for entropy if requested, reads `OMNIA_CMD_TRNG_COLLECT_ENTROPY`, bounds the returned byte count to caller size and the 64-byte command maximum, and copies entropy. `omnia_mcu_register_trng()` clears any stale entropy condition, requests the TRNG IRQ via the GPIO IRQ helper, and registers `mcu->trng`.

## Control Flow

Registration is skipped unless `OMNIA_FEAT_TRNG` is present. Before requesting the IRQ, it performs a one-byte collect command to ensure future IRQ generation. Reads either return 0 immediately when nonblocking and no completion is available or wait for the completion, collect entropy, and retry if blocking reads return zero bytes.

## State And Persistence

The only kernel state is the hwrng object and completion. Entropy is produced by the MCU and not cached beyond one read buffer.

## Dependencies And Integration Points

It depends on the MCU GPIO interrupt layer, hwrng framework, I2C command helpers, and TRNG feature bit.

## Risks

The completion is not reinitialized before every read; completion semantics must match the MCU interrupt/collect behavior. Lost interrupts can block waiting readers. Nonblocking reads return 0 rather than an error when entropy is unavailable, as hwrng expects.

## Test Signals

Test feature absence, stale entropy clearing, IRQ completion, blocking and nonblocking reads, zero-byte retry, maximum 64-byte reads, I2C errors, and hwrng registration/unregistration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/cznic/turris-omnia-mcu-trng.c -->
