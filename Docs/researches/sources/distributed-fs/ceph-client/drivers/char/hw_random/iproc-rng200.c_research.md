# sources/distributed-fs/ceph-client/drivers/char/hw_random/iproc-rng200.c

## Purpose
This platform driver supports Broadcom iProc/STB RNG200 hardware. It enables the random bit generator, detects NIST/master-fail lockout status, resets hardware on failure, drains FIFO data, and supports system sleep suspend/resume.

## Important APIs, Types, and Functions
- `struct iproc_rng200_dev` stores hwrng and MMIO base.
- `iproc_rng200_enable_set()` toggles the generator enable field.
- `iproc_rng200_restart()` disables, clears status, resets RNG/RBG blocks, and re-enables.
- `iproc_rng200_read()` drains FIFO words/partial words with bounded idle wait and at most one reset per read.
- `iproc_rng200_init()` and `iproc_rng200_cleanup()` enable/disable hardware.

## Control Flow
Probe maps MMIO, stores driver data, sets hwrng callbacks, and registers. Reads loop until requested bytes are filled or a one-second idle timeout expires. On health failure status, the driver restarts hardware once and continues. If FIFO has data, it copies full or partial words; otherwise it returns immediately for nonblocking callers or sleeps briefly.

## State and Persistence Behavior
Hardware enable/reset/status state persists until cleanup or suspend. There is no software buffer. Suspend disables the generator and resume re-enables it.

## Dependencies and Integration Points
It depends on OF compatibles for BCM2711/7211/7278/iProc RNG200, platform MMIO, hwrng core, and system sleep PM.

## Risks
One reset per read prevents endless reset loops but can return short reads after repeated hardware failures. The wait sleep upper bound is fixed at 500 usec while idle timeout is jiffies based. Health status clearing is broad (`0xffffffff`).

## Test Signals
Test FIFO full and empty paths, partial final word copies, health failure/reset path, nonblocking returns, idle timeout, suspend/resume, and probe MMIO failure.
