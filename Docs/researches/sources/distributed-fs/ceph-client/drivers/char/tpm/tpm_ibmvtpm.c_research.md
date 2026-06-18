# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_ibmvtpm.c

## Purpose
Implements IBM Power virtual TPM support over VIO CRQ queues and hypervisor calls, registering a TPM chip backed by an RTCE DMA buffer.

## Important APIs, Types, And Functions
Core operations are `tpm_ibmvtpm_send()`, `tpm_ibmvtpm_recv()`, `tpm_ibmvtpm_status()`, and `tpm_ibmvtpm_req_canceled()`. CRQ lifecycle helpers include `ibmvtpm_send_crq()`, `ibmvtpm_crq_send_init()`, `ibmvtpm_crq_get_version()`, `ibmvtpm_crq_get_rtce_size()`, `ibmvtpm_crq_send_init_complete()`, `ibmvtpm_reset_crq()`, `ibmvtpm_crq_get_next()`, `ibmvtpm_crq_process()`, and `ibmvtpm_interrupt()`.

## Control Flow
Probe allocates a TPM chip, driver state, one CRQ page, maps it for DMA, registers or resets the hypervisor CRQ, requests the VIO IRQ, enables interrupts, initializes waitqueues and locks, sends init/version/RTCE-size CRQs, waits for RTCE buffer allocation, sets TPM2 flag for compatible `IBM,vtpm20`, and registers the chip. Send waits for any in-flight command, copies the command into RTCE buffer under lock, marks processing, sends a CRQ pointing to the DMA handle, and retries once after `H_CLOSED` by resuming CRQ. Interrupt processing walks CRQ responses, handles init negotiation, allocates/maps RTCE buffer, records version, records response length, clears processing, and wakes waiters. Recv copies the RTCE response and clears it.

## State And Persistence
Runtime state includes CRQ ring index, DMA mappings, RTCE buffer and size, response length, version, waitqueues, spinlock, and processing flag. Persistent vTPM state is owned by the hypervisor/server side.

## Dependencies And Integration Points
Depends on Power VIO, `plpar_hcall_norets()` Hcalls, DMA mapping, IRQ handling, and TPM core registration. PM hooks send prepare-to-suspend and re-enable/init CRQ on resume.

## Risks And Edge Cases
Command completion races with Hcall return, so `tpm_processing_cmd` is set before sending CRQ. Error paths must unmap DMA and free pages exactly once. `tpm_ibmvtpm_send()` returns zero even after some CRQ send failures after clearing the processing flag, which is worth scrutiny. Probe waits only one second for RTCE buffer response.

## Test Signals
CRQ init handshake, version and RTCE-size responses, DMA mapping failure, H_CLOSED retry on send, suspend/resume, interrupt-driven command completion, TPM2 compatible matching, and cleanup after partial probe failures.
