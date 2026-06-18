# sources/distributed-fs/ceph-client/drivers/misc/vmw_vmci/vmci_doorbell.h

Purpose: declares internal doorbell ioctl, checkpoint, privilege, bitmap, and host-notify contracts.

Important types/APIs: `struct vmci_dbell_notify_resource_info` is used by host ioctl paths to create, destroy, or notify a doorbell/queue-pair-like resource. `struct dbell_cpt_state` stores checkpointed doorbell mapping data and is explicitly checkpoint-compatible. Prototypes expose host notification, privilege lookup, notification bitmap registration, and bitmap scanning.

Control flow/integration: host ioctl code passes `vmci_dbell_notify_resource_info` into context doorbell create/destroy/notify helpers. Guest probe registers a notification bitmap, and interrupt processing scans it through this header's API.

State/persistence: `dbell_cpt_state` is persistent checkpoint ABI. Other declarations describe volatile doorbell resources.

Risks: changing `dbell_cpt_state` breaks checkpoint compatibility. `vmci_dbell_get_priv_flags()` is security-sensitive because context doorbell notification relies on it before cross-context delivery.

Test signals: checkpoint binary compatibility, ioctl copy layout, and bitmap scan behavior with mocked bitmap data.
