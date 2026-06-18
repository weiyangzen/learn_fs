<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mxl5xx_regs.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mxl5xx_regs.h

## Purpose
`mxl5xx_regs.h` is the register-address map for MaxLinear Hydra/MxL5xx devices. It gives `mxl5xx.c` symbolic names for PRCM, firmware, demod status, tuner status, transport stream, PID, BERT, AGC, AFE, watchdog, FSK, and miscellaneous hardware registers.

## Important APIs, Types, And Functions
The header defines CPU/clock/reset registers, crystal and firmware-version addresses, heartbeat/signature registers, demod and tuner status base/offset macros, status register offsets for lock/SNR/errors/frequency/input power, `HYDRA_DEMOD_STATUS_LOCK()` and `HYDRA_DEMOD_STATUS_UNLOCK()` write macros, TS control base addresses, PID table addresses, XPT/BERT registers, FPGA addresses, AGC/AFE addresses, and XPT DMD xbar base address. It has no types or functions.

## Control Flow
No standalone flow exists. Runtime code in `mxl5xx.c` reads/writes these addresses for firmware reset/download/startup, heartbeat checks, status snapshots, TS muxing, tuner-enable polling, and MPEG output programming.

## State And Persistence
The header defines hardware state locations. Register writes persist in the chip until overwritten, reset, or power cycle. The kernel does not persist these values independently.

## Dependencies And Integration Points
It is consumed by `mxl5xx.c` together with the Hydra protocol definitions. The lock/unlock macros rely on a `write_register()` helper and `MXL_YES/MXL_NO` from `mxl5xx_defs.h`, so include ordering matters.

## Risks
Incorrect addresses or offsets can corrupt unrelated hardware blocks. Some macros duplicate names (`HYDRA_HEAR_BEAT`) and many constants are raw vendor addresses; maintainability depends on preserving the original datasheet mapping. The status offset macros assume a fixed stride per demod/tuner.

## Test Signals
Hardware probe, firmware heartbeat/version reads, demod lock/statistics reads for multiple demod IDs, TS output validation, and register tracing during init/tune are the practical tests for this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mxl5xx_regs.h -->
