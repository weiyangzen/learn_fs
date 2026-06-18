<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm-buf.c -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm-buf.c

## Purpose
Provides helper routines for constructing and parsing page-sized TPM command buffers and TPM2B sized buffers.

## Important APIs, Types, And Functions
Exports `tpm_buf_init()`, `tpm_buf_reset()`, `tpm_buf_init_sized()`, `tpm_buf_reset_sized()`, `tpm_buf_destroy()`, `tpm_buf_length()`, `tpm_buf_append()`, scalar append helpers, `tpm_buf_append_handle()`, and scalar read helpers `tpm_buf_read_u8/u16/u32()`.

## Control Flow
Initialization allocates one page and writes the TPM header or a TPM2B size prefix. Append checks for prior overflow, bounds writes to `PAGE_SIZE`, copies data, advances the length, and updates either the command header length or TPM2B length. Read helpers advance a caller-supplied offset and set a boundary-error flag if the requested range exceeds the buffer length.

## State And Persistence
Each `struct tpm_buf` owns a page until `tpm_buf_destroy()`. Buffer flags record overflow or boundary errors, length tracks valid bytes, and `handles` counts command handles for TPM2 session construction.

## Dependencies And Integration Points
Used throughout TPM1, TPM2, TPM2 sessions, and TPM2 resource-manager code. It depends on big-endian TPM wire formats and exported Linux TPM command structures.

## Risks And Edge Cases
Append overflow is sticky and silent after the first warning, so callers must avoid continuing with malformed commands. Read boundary failures return zero values and set a flag, which can hide parsing errors if callers do not validate final status. `tpm_buf_append_handle()` rejects TPM2B buffers only by logging.

## Test Signals
Unit-style tests for append length updates, overflow behavior at `PAGE_SIZE`, TPM2B size updates, endian scalar writes/reads, handle counting, and parser behavior when offsets cross buffer boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm-buf.c -->
