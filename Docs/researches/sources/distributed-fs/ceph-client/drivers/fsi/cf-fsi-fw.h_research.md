<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fsi/cf-fsi-fw.h -->
# sources/distributed-fs/ceph-client/drivers/fsi/cf-fsi-fw.h

## Purpose
`cf-fsi-fw.h` defines the ABI between the ARM-side Aspeed ColdFire FSI master driver and the ColdFire microcode image `cf-fsi-fw.bin`. It documents firmware header layout, boot configuration offsets, SRAM command/status registers, response fields, GPIO arbitration, and trace-buffer encodings.

## Important APIs, types, and functions
Important definitions include `HDR_OFFSET`, firmware signatures `SYS_SIG_SHARED` and `SYS_SIG_SPLIT`, API version `2.1`, boot config offsets for command/status area and GPIO virtual/data registers, command constants `CMD_COMMAND`, `CMD_BREAK`, `CMD_IDLE_CLOCKS`, status values such as `STAT_COMPLETE` and `STAT_ERR_MTOE`, SRAM offsets `CMD_DATA`, `RSP_DATA`, `ARB_REG`, and trace constants under `TRACEBUF`.

## Control flow
The header has no executable flow. `fsi-master-ast-cf.c` uses it to locate a matching firmware image, patch GPIO and control fields before starting the coprocessor, write command/status words in SRAM, decode completion/error status, arbitrate GPIO access, and optionally dump microcode traces.

## State and persistence behavior
It describes runtime memory shared between the host CPU and ColdFire firmware. Firmware image headers persist in the firmware blob, while SRAM command/status fields are transient and cleared/rewritten during setup and command execution.

## Dependencies and integration points
It is included by `fsi-master-ast-cf.c` and tightly coupled to `cf-fsi-fw.bin`. The register contract also integrates with Aspeed SRAM, SCU ColdFire mapping, GPIO coprocessor arbitration, and optional CVIC doorbells.

## Risks and edge cases
Offsets and status encodings are firmware ABI. Any mismatch between this header and the loaded firmware can break command submission, GPIO ownership, or trace interpretation. API major-version checks in the driver are the main guard.

## Test signals
ColdFire firmware load with both shared and split GPIO signatures, API-version validation, command/status completion, GPIO arbitration, and trace dump decoding validate this header's contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fsi/cf-fsi-fw.h -->
