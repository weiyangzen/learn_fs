# sources/distributed-fs/ceph-client/drivers/scsi/qlogicfas.c

## Purpose
`qlogicfas.c` is the ISA-board wrapper for QLogic FAS408 SCSI controllers. It handles module parameters, I/O-port reservation, IRQ registration, SCSI host allocation, and SCSI mid-layer registration while delegating command execution and hardware protocol details to `qlogicfas408.c`.

## Important APIs, Types, And Functions
The central probe helper is `__qlogicfas_detect()`, which validates `iobase`/`irq`, reserves 16 I/O ports, calls `qlogicfas408_detect()`, initializes the chip with `qlogicfas408_setup()`, allocates a `Scsi_Host`, fills `struct qlogicfas408_priv`, requests the IRQ, adds the host, and scans it. `qlogicfas_detect()` iterates up to `MAX_QLOGICFAS` module-parameter slots and chains detected `qlogicfas408_priv` objects in `cards`. `qlogicfas_release()` removes a host and frees IRQ, port, and host resources. The `qlogicfas_driver_template` wires `qlogicfas408_info`, `qlogicfas408_queuecommand`, `qlogicfas408_abort`, `qlogicfas408_host_reset`, and `qlogicfas408_biosparam` into the SCSI mid-layer.

## Control Flow
Module init calls `qlogicfas_detect()`. For each configured pair of `iobase[]` and `irq[]`, detection reserves the region, probes the chip, reads chip type, chooses initiator ID 7 when the template has `this_id < 0`, programs the FAS408 registers, allocates the SCSI host private area, installs the interrupt handler, registers with `scsi_add_host()`, and starts `scsi_scan_host()`. A failed step unwinds in reverse order. Module exit walks `cards` and calls `qlogicfas_release()` for each host.

## State And Persistence
Runtime state is per-adapter `struct qlogicfas408_priv`: base port, IRQ, initiator ID, interrupt type, current command pointer, info string, owning host, and next pointer. Global state is the `cards` list plus module parameter arrays. The driver writes no persistent configuration; hardware configuration is inferred from caller-provided module parameters and volatile chip registers.

## Dependencies And Integration Points
This file depends on legacy ISA I/O port APIs, IRQ registration, SCSI host allocation/scanning/removal, and the shared FAS408 core in `qlogicfas408.h`. User integration is through module parameters `iobase=` and `irq=`. It also depends on `qlogicfas408_ihandl()` being safe under the SCSI host lock taken by the shared interrupt wrapper.

## Risks And Edge Cases
Autoprobing is not attempted: missing or invalid module parameters yield no devices. The exit loop follows `priv->next` after `qlogicfas_release()` calls `scsi_host_put()`, so correctness depends on the private memory remaining readable until the loop advances. The driver has `can_queue = 1`, but command serialization still relies on the shared core's `qlcmd` polling. IRQ and I/O resource cleanup paths are narrow and should be checked when probe fails after partial initialization.

## Test Signals
Useful signals include module load with no parameters returning `-ENODEV`, successful load for known `iobase`/`irq`, busy I/O-port rejection, failed chip probe cleanup, SCSI scan after `scsi_add_host()`, interrupt-driven command completion through the FAS408 core, abort/reset behavior via the template handlers, and unload freeing IRQ and I/O region without stale hosts.
