<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/esp_scsi.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/esp_scsi.h

## Purpose

`esp_scsi.h` defines the hardware register map, bitfields, commands, status/interrupt values, timing formulas, chip revisions, private SCSI command state, target/LUN state, front-end operation contract, main `struct esp`, state-machine constants, and exported entry points for the generic ESP SCSI core.

## Important APIs, Types, and Definitions

The header defines ESP register offsets such as `ESP_TCLOW`, `ESP_FDATA`, `ESP_CMD`, `ESP_STATUS`, `ESP_INTRPT`, `ESP_SSTEP`, `ESP_FFLAGS`, `ESP_CFG1` through `ESP_CFG4`, HME/FAS aliases, and `SBUS_ESP_REG_SIZE`. It defines config bits, command opcodes (`ESP_CMD_FLUSH`, `RC`, `RS`, `TI`, `ICCSEQ`, `MOK`, `SATN`, `SELA`, `SELAS`, `SA3`, `DMA`), SCSI phase masks (`ESP_DOP`, `DIP`, `CMDP`, `STATP`, `MOP`, `MIP`), interrupt bits, sequence-step values, FIFO flags, clock conversion constants, and sync defaults.

Core types are `struct esp_cmd_priv` for per-command scatterlist residue, `enum esp_rev` for ordered chip capability levels, `struct esp_cmd_entry` for queued/active command state and autosense metadata, `struct esp_lun_data` for tag/non-tagged command tracking, `struct esp_target_data` for negotiated and desired transfer settings, `struct esp_event_ent` for diagnostic event log entries, `struct esp_driver_ops` for platform callbacks, and `struct esp` for the main controller instance.

Exported declarations are `scsi_esp_template`, `scsi_esp_register()`, `scsi_esp_unregister()`, `scsi_esp_intr()`, `scsi_esp_cmd()`, and `esp_send_pio_cmd()`.

## Control Flow and Design Role

The header encodes the front-end driver recipe in comments: allocate a host with `scsi_esp_template`, fill `struct esp`, hook `esp->ops`, set capability flags, map registers and DMA, map the command block, register the interrupt handler, populate SCSI ID/clock/bus properties, perform pre-programming DMA setup, set drvdata if needed, and call `scsi_esp_register()`. The core C file then uses these definitions to drive hardware commands and SCSI phase transitions.

State-machine constants in `struct esp` and macros define the legal software events and selection states used by `esp_process_event()` and `__esp_interrupt()`. Register bit definitions must match hardware exactly because front-end `esp_read8()`/`esp_write8()` calls use these offsets and values directly.

## State and Persistence Behavior

The header itself stores no state, but it defines all persistent runtime state for the core. `struct esp` persists for the lifetime of a host adapter. `struct esp_target_data` persists per target and survives across commands until reset or SPI transport reconfiguration. `struct esp_lun_data` persists per SCSI device and tracks outstanding tags. `struct esp_cmd_entry` persists while a command is queued, active, disconnected, or autosensing. Timing fields (`cfreq`, `cfact`, `ccycle`, `ctick`, `neg_defp`, min/max periods) persist after registration and chip probing.

## Dependencies and Integration Points

The header assumes Linux SCSI core types, scatterlists, DMA addresses, completions, list heads, MMIO pointers, and IRQ return types are available through includers. It is included by `esp_scsi.c` and platform front-end drivers. The most important integration boundary is `struct esp_driver_ops`: incorrect implementation of register access, IRQ pending, DMA setup, DMA drain/invalidate, reset, or DMA error reporting breaks the core state machine.

## Risks and Edge Cases

Many constants are chip ABI. Incorrect bit definitions, enum ordering, or structure field interpretation can produce hardware commands with wrong phases or corrupt negotiation state. `ESP_MAX_TARGET`, `ESP_MAX_LUN`, and `ESP_MAX_TAG` bound arrays directly. `ESP_CMD_PRIV(cmd)` assumes the SCSI host template reserved `cmd_size = sizeof(struct esp_cmd_priv)`. Front-end drivers must honor the setup checklist, especially command block DMA mapping and accurate SCSI ID mask. PIO support requires `fifo_reg` and virtual-address transfer assumptions that are not valid for normal DMA front-ends.

## Test Signals

Signals include successful compile of front-end drivers against `struct esp_driver_ops`, host allocation with the expected command-private size, correct register access on 1-byte and wider register spacing front-ends, target counts within `ESP_MAX_TARGET`, tag allocation within `ESP_MAX_TAG`, SPI transport attributes reflecting negotiated width/period/offset, reset clearing state constants, and front-end conformance to the registration checklist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/esp_scsi.h -->
