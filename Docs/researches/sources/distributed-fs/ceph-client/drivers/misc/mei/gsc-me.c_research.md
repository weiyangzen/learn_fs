# sources/distributed-fs/ceph-client/drivers/misc/mei/gsc-me.c

## Purpose
`gsc-me.c` is the auxiliary MEI hardware driver for Intel Graphics System Controller devices exposed by i915 or xe. It maps GSC MMIO, configures interrupts or polling, registers a MEI device, starts firmware handshaking, and implements system/runtime PM.

## Important APIs, Types, and Functions
Key functions are `mei_gsc_probe()`, `mei_gsc_remove()`, `mei_gsc_read_hfs()`, `mei_gsc_set_ext_op_mem()`, system sleep callbacks, runtime PM callbacks, and the auxiliary ID table for `i915.mei-gsc`, `i915.mei-gscfi`, and `xe.mei-gscfi`.

## Control Flow
Probe selects a MEI hardware config, initializes `mei_device`, maps the supplied BAR, stores IRQ/read-status hooks, programs external operation memory when present and sets `pxp_mode` to init, then either starts a polling thread or requests a threaded IRQ. It registers MEI, enables runtime PM, starts MEI firmware handshake, sets autosuspend, and returns even if startup handshake fails after registration. Remove stops MEI, stops polling if used, disables PM/interrupts, frees IRQ when used, and deregisters.

## State and Persistence
State is in `mei_device`, `mei_me_hw`, mapped MMIO, IRQ or polling thread state, runtime PM state, external operation memory registers, and `pxp_mode`.

## Dependencies and Integration Points
Depends on `mei_aux_device` supplied by graphics drivers, MEI ME hardware helpers, runtime PM, kthreads, IRQ handlers, and trace register logging.

## Risks
Startup intentionally tolerates firmware handshake failure for status visibility, so later clients must handle partially initialized firmware. Polling-thread lifecycle and runtime PM active flags must remain balanced. External operation memory must be reprogrammed on resume before restart.

## Test Signals
Signals are successful auxiliary binding from i915/xe, MMIO mapping, IRQ or polling operation, MEI registration, firmware status sysfs visibility after handshake failure, PXP memory-ready progression, suspend/resume restart, runtime autosuspend only when writes are idle, and clean remove.
