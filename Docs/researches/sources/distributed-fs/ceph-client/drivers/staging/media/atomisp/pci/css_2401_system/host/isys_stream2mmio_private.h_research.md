# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/host/isys_stream2mmio_private.h

Purpose: provides Stream2MMIO state capture, printing, and MMIO register access helpers.

Important APIs/types/functions: local register IDs define eight registers per SID. NCI helpers are `stream2mmio_get_state()`, `stream2mmio_get_sid_state()`, `stream2mmio_print_sid_state()`, and `stream2mmio_dump_state()`. DLI helpers are `stream2mmio_reg_load()` and `stream2mmio_reg_store()`.

Control flow: state capture loops from SID0 to `N_STREAM2MMIO_SID_PROCS[ID]`, reading each SID's ack, pixel width, addresses, stride, item count, and blocking flag. Loads compute a bank offset of `STREAM2MMIO_REGS_PER_SID * sid_id`; stores accept a flat register index.

State and persistence: stores mutate hardware. Captured state is transient.

Dependencies and integration: depends on public Stream2MMIO declarations, controller bases, device access, assertions, and print support. It feeds diagnostics and IBUF/stream routing code.

Risks and test signals: `stream2mmio_reg_load()` asserts controller ID but not SID or reg bounds, and store takes a flat `reg` rather than SID/reg pair. Tests should verify controller-specific SID limits, address arithmetic, and blocked-input behavior when no command is pending.
