# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_vf_isr.c

## Purpose
`adf_vf_isr.c` implements interrupt resources for QAT virtual functions. It enables MSI, handles VF interrupt source bits for bundle and PF-to-VF messages, schedules bottom halves, and coordinates asynchronous VF shutdown/restart when the PF reports a restart.

## Important APIs, Types, And Functions
Exported functions are `adf_enable_pf2vf_interrupts()`, `adf_disable_pf2vf_interrupts()`, `adf_pf2vf_handle_pf_restarting()`, `adf_vf_isr_resource_alloc()`, `adf_vf_isr_resource_free()`, `adf_flush_vf_wq()`, `adf_init_vf_wq()`, and `adf_exit_vf_wq()`. Important internals are `adf_isr()`, `adf_pf2vf_bh_handler()`, `adf_setup_pf2vf_bh()`, `adf_setup_bh()`, `adf_request_msi_irq()`, and `adf_dev_stop_async()`. `struct adf_vf_stop_data` carries deferred stop work.

## Control Flow
Resource allocation enables one MSI vector, initializes the PF2VF tasklet and VF2PF lock, initializes the transport bank response tasklet, and requests the IRQ. The top-half reads `ADF_VINTSOU`, masks it with `ADF_VINTMSK`, disables PF2VF interrupts and schedules the PF2VF tasklet when a PF message arrives, and disables bundle interrupts plus schedules bank 0 response handling when ring responses arrive. The PF2VF bottom half receives and handles messages and re-enables PF2VF interrupts if handling is complete. A PF-restarting message clears PF-running status and queues work that notifies restart, calls `adf_dev_down()`, re-enables PF2VF interrupts, notifies restart completion, and frees work data.

## State And Persistence Behavior
The global `adf_vf_stop_wq` persists from module init to exit. Per-device VF state includes tasklets, the IRQ name, IRQ enabled flag, VF2PF lock, and status bits. MSI affinity is hinted to a CPU derived from accelerator ID. No persistent storage is used.

## Dependencies And Integration Points
The file depends on PCI MSI APIs, tasklets, workqueues, PF/VF message helpers, transport bank response handling, accelerator lifecycle helpers (`adf_dev_down`, restart notifications), and CSR access to the PMISC BAR. It is the VF-specific bridge between hardware interrupt sources and QAT common transport/service callbacks.

## Risks
Top-half masking is essential; failure to disable PF2VF or bundle sources can reschedule already pending work. VF restart handling runs asynchronously and interacts with device teardown, so lifetime of `accel_dev` and workqueue flushing matters. Only bank 0 is scheduled for bundle interrupts in this VF path, which must match VF hardware exposure. Error unwinding in resource allocation must reverse tasklet/MSI setup exactly.

## Test Signals
VF probe should allocate MSI and request IRQ. PF2VF messages should be handled once and re-enable interrupts. Ring completions should drain through `adf_response_handler()`. Restart tests should show VF down/restart-complete notification, no workqueue leaks, and clean IRQ free on remove.
