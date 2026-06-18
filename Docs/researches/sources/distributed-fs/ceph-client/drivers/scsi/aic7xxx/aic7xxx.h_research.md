# sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic7xxx.h

## Purpose

`aic7xxx.h` is the OS-neutral core header for the older AHC/AIC7xxx SCSI controller family. It defines hardware constants, chip/feature/bug/flag enums, SCB layouts, scatter/gather formats, target-mode structures, negotiation state, SEEPROM layout, `struct ahc_softc`, PCI/EISA identity structures, and public core function prototypes.

## Important APIs, Types, and Functions

- Target/path macros derive target, channel, LUN, target masks, and TCL values from SCB fields and controller features.
- Constants define target/LUN limits, maximum transfer size, SCB limits, target-mode command FIFO size, and reset delays.
- Enums `ahc_chip`, `ahc_feature`, `ahc_bug`, and `ahc_flag` describe controller model, capabilities, silicon workarounds, and runtime configuration flags.
- `struct hardware_scb` mirrors the controller SCB layout, including CDB/status/target-mode shared area, data pointer/count, S/G pointer, control, SCSI ID, LUN, tag, rate/offset, and long CDB storage.
- `struct ahc_dma_seg`, `struct sg_map_node`, `enum scb_flag`, `struct scb`, and `struct scb_data` define host-side SCB and DMA/S/G state.
- Target-mode structures include `struct target_cmd`, `struct ahc_tmode_event`, and `struct ahc_tmode_tstate`.
- Negotiation structures include `struct ahc_transinfo`, `struct ahc_initiator_tinfo`, `struct ahc_syncrate`, and `struct ahc_phase_table_entry`.
- `struct seeprom_config` defines the 32-word serial EEPROM layout and many bit fields for per-target and adapter policy.
- `struct ahc_softc` is the central controller state object, combining bus handles, SCB queues, bus-specific/platform data, target state, features/bugs/flags, message buffers, DMA maps, init level, PCI cacheline, identity/name, and user negotiation masks.
- Prototypes cover PCI/EISA attach, SCB management, initialization, reset, error recovery searches, transfer negotiation, target mode, debug, and SEEPROM acquisition.

## Control Flow and State

The file itself has no executable flow, but it documents the core state machine used by AHC implementations. Commands are represented as host SCBs pointing at DMA-safe hardware SCBs. SCBs move through free, pending, queued, disconnected, active, recovery, sense, target, and completion states, with hardware firmware updating shared SCB fields for residuals and status. The `ahc_softc` aggregates queue pointers, sequencer state, message buffers, target negotiation tables, and bus/platform hooks so OS-specific files can attach the same core to PCI, EISA, or VL hardware.

The residual comments are an important behavioral contract: the sequencer and host interpret `sgptr`, `residual_sg_ptr`, `datacnt`, `SG_FULL_RESID`, `SG_LAST_SEG`, and `SG_RESID_VALID` together. This affects how completions calculate underflow and residual data.

## State and Persistence Behavior

Runtime state is in `struct ahc_softc`, `struct scb_data`, and per-target negotiation tables. Persistent adapter policy is represented by `struct seeprom_config`, which is loaded from serial EEPROM or BIOS scratch by bus-specific code and influences transfer width, sync, disconnect, tagging, termination, BIOS, and reset behavior.

## Dependencies and Integration Points

The header depends on generated `aic7xxx_reg.h` and OS-supplied platform typedefs for bus space, DMA, platform data, and I/O context. It integrates with AHC core C files, PCI/EISA front ends, Linux/BSD OSM layers, and the 93Cx6 SEEPROM helper. It is related to but distinct from AIC79xx/AHD headers; this subset includes it because the EEPROM helper is for the older AHC path.

## Risks

- Hardware SCB layout is byte-position sensitive; field reordering or packing changes would break DMA communication with firmware.
- Many feature and bug flags are silicon-specific; incorrect combinations can cause data corruption or failed recovery.
- Target/channel macros assume specific bit layouts from register definitions and twin-channel feature flags.
- `struct seeprom_config` bit definitions overlap between adapter generations/cards; consumers must apply the right interpretation.
- Public prototypes form a broad ABI within the driver; platform/core drift can compile but fail at runtime if state invariants change.

## Test Signals

- Compile the AHC driver variants using this header with target mode enabled and disabled.
- Exercise SCB allocation/queue/completion, residual calculation, S/G DMA, transfer negotiation, bus reset, and SEEPROM read/parse flows.
- Validate generated register headers match the structure and macro assumptions.
