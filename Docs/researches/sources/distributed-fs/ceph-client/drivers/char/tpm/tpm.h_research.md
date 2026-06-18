<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm.h -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm.h

## Purpose
Defines the internal TPM driver contract: shared constants, TPM1 capability layouts, TPM2 property constants, global class/device exports, and prototypes linking chip lifecycle, command, eventlog, sysfs, TPM1, TPM2, sessions, and resource-manager code.

## Important APIs, Types, And Functions
Important definitions include `TPM_MINOR`, `TPM_BUFSIZE`, `TPM_NUM_DEVICES`, timeout enums, TPM1 error/warning codes, `TPM2_SPACE_BUFFER_SIZE`, TPM1 capability structures/unions, TPM capability enums, TPM2 property enums, `TPM_MAX_RNG_DATA`, class/device globals, and prototypes for `tpm_transmit()`, `tpm_chip_alloc/register/unregister()`, TPM1/TPM2 command helpers, TPM2 space helpers, event-log setup, and dev common init/exit.

## Control Flow
The header does not execute code except for `tpm_msleep()` and config stubs. It establishes which implementation files can call each other and which symbols are exported to transport drivers and other kernel code.

## State And Persistence
The structures describe persistent chip state consumed elsewhere, especially TPM1 capability data, TPM2 resource-manager buffer size, and global TPM class/device number state declared here and defined in implementation files.

## Dependencies And Integration Points
Included by nearly every TPM source file in this subset and by bus drivers. It pulls in Linux device, module, TPM, eventlog, synchronization, delay, and architecture CPU matching headers.

## Risks And Edge Cases
Wire-format structures are packed and endian-qualified; layout drift would break TPM command parsing. Constants such as buffer sizes and RNG limits are baked into multiple callers. Prototype changes can break modules outside this immediate directory.

## Test Signals
Compile all TPM configurations, run sparse/endian checks on packed structures, validate TPM1/TPM2 command parsers against wire-format fixtures, and exercise APIs from transport drivers and in-kernel TPM consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm.h -->
