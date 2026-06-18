# sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_irq.h

Purpose: declares the IOSM IRQ/doorbell interface used by PCIe, protocol, PM, and imem layers.

Important APIs: forward-declares `struct iosm_pcie` and exposes `ipc_doorbell_fire`, `ipc_release_irq`, and `ipc_acquire_irq`. These functions hide BAR register layout and PCI MSI setup from higher layers.

Control flow role: `ipc_doorbell_fire` is called for IPC state requests, HPDA head-pointer updates, PSI boot notification, and PM sleep/active control. `ipc_acquire_irq` is called during PCI resource setup; `ipc_release_irq` is called during teardown and resource unwind.

State/dependencies: no persistent state in the header; all state is carried by `iosm_pcie`. The prototypes depend on `u32` being available through include context, normally via local PCIe/protocol headers. Risks are mostly integration risks: include ordering, misuse before BAR mapping, and firing doorbells after resources release. Test signals include compile coverage from `iosm_ipc_pcie.c`, `iosm_ipc_pm.h`, `iosm_ipc_protocol.h`, and imem boot paths plus runtime smoke tests that exercise each doorbell type.
