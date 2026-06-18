<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sym53c8xx_2/sym_defs.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/sym53c8xx_2/sym_defs.h

## Purpose
`sym_defs.h` defines the hardware vocabulary for the Symbios/LSI SCSI processor driver: chip feature flags, the memory-mapped register layout, SCRIPTS instruction encodings, table formats, SCSI phase constants, message constants, PPR options, and SCSI status aliases.

## Important APIs, Types, And Functions
Important data types are `struct sym_chip`, which describes a supported chip ID/revision/name/features and timing capabilities; `struct sym_reg`, a packed-by-layout representation of the chip register file; `struct sym_tblmove`, used by indirect move SCRIPTS entries; and `struct sym_tblsel`, used by table-driven selection. Feature flags include `FE_WIDE`, `FE_ULTRA*`, `FE_LDSTR`, `FE_RAM`, `FE_64BIT`, `FE_NOPM`, `FE_CRC`, `FE_C10`, `FE_DAC`, and others. Instruction macros include `SCR_MOVE_*`, `SCR_SEL_*`, `SCR_WAIT_*`, `SCR_SET`, `SCR_CLR`, `SCR_COPY`, register operation macros, load/store macros, `SCR_JUMP`/`SCR_CALL`/`SCR_INT`, condition macros, and phase/message/status aliases.

## Control Flow
The header has no runtime control flow, but the constants directly generate the firmware SCRIPTS arrays in `sym_fw1.h`/`sym_fw2.h`. The C code also uses `REG()` offsets and feature bits to program registers, patch scripts, and choose firmware. Runtime SCRIPTS control flow is encoded as 32-bit opcodes built by these macros.

## State And Persistence Behavior
No state is stored here. It defines register offsets and bit meanings for live chip state and shared script structures. Persistent hardware/NVRAM data is handled elsewhere.

## Dependencies And Integration Points
The header depends on SCSI protocol constants from the kernel and on structure offsets matching the chip manuals. It is consumed by firmware definitions, relocation code, and the high-level driver implementation. `sym_fw_bind_script()` depends on the top nibble and relocation forms generated from these macros.

## Risks
Risks are especially high because a wrong register offset or opcode bit can produce invalid DMA, SCSI bus hangs, or incorrect script relocation. `struct sym_reg` must match real MMIO layout. Feature flags must match silicon quirks, and SCRIPTS macros must preserve exact instruction lengths expected by firmware struct arrays.

## Test Signals
Test signals include compile-time firmware generation, script relocation, supported chip probing by feature flags, register programming on multiple revisions, wide/sync/PPR negotiation, phase mismatch handling, SCSI reset/interrupt status decoding, load/store firmware on `FE_LDSTR` chips, generic firmware on older chips, and hardware or emulator validation of SCRIPTS opcode streams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sym53c8xx_2/sym_defs.h -->
