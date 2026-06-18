# sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_event.h

Purpose: small internal header for the VMCI event subsystem.

Important APIs: declares `vmci_event_init()`, `vmci_event_exit()`, and `vmci_event_dispatch()`. Public subscription APIs come from the external VMCI API header, while this header exposes module-internal lifecycle and dispatch hooks.

Control flow/integration: module init/exit call lifecycle functions; datagram and guest receive paths call dispatch for event datagrams.

State/persistence: no state is declared here.

Risks: minimal, but all callers must pass a valid `struct vmci_datagram *` whose payload matches VMCI event layout.

Test signals: build coverage and dispatch validation with malformed datagrams.
