# sources/distributed-fs/ceph-client/drivers/s390/cio/cio.h

## Purpose
This header defines core s390 CIO hardware data structures and the internal subchannel API used by CSS, CCW-device, CHSC, CMF, and low-level I/O code.

## Important APIs, Types, and Functions
It defines packed `struct pmcw`, `struct schib_config`, `struct schib`, `enum sch_todo`, and `struct subchannel`. `struct subchannel` carries the hardware id, locks, subchannel type, path masks, current SCHIB, desired ISC, SSD info, Linux device, bound CSS driver, slow-path todo work, target config, and DMA mask. It declares low-level CIO operations for start/resume/halt/clear/cancel, config commit/update, subchannel enable/disable, transport-mode I/O, airq init, console probing, and per-CPU `cio_irb`.

## Control Flow
The header contributes no runtime logic except compile-time console stubs. Implementations use `struct subchannel.config` as the desired state and `schib` as the last observed hardware state, with `enum sch_todo` controlling CSS slow-path work priority.

## State and Persistence
All structures model volatile hardware/kernel state. No data is persisted. Packing/alignment are part of the hardware ABI and DMA-visible contract.

## Dependencies and Integration Points
It depends on architecture CIO, FCX, SCHID, TPI, CHPID, and Linux device/mod_devicetable types, plus `chsc.h` for SSD info. It is the central type contract for nearly every file in this subset.

## Risks and Test Signals
Risk areas include packed bitfield layout, mismatches between desired config and hardware SCHIB, subchannel lifetime/reference handling, and assuming console stubs are safe when `CONFIG_CCW_CONSOLE` is off. Test signals are full s390 CIO build coverage, subchannel registration/probe, MSCH config verification, transport-mode callers, and lockdep coverage around `subchannel.lock` and `reg_mutex`.
