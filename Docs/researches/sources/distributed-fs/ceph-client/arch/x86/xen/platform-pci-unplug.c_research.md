# sources/distributed-fs/ceph-client/arch/x86/xen/platform-pci-unplug.c

Purpose: Handles Xen HVM platform PCI unplug protocol and reports whether PV disk/NIC devices should be considered available alongside or instead of emulated devices.

Important APIs/types/functions: `check_platform_magic()` validates Xen platform I/O port magic/protocol and sends Linux product/version identifiers. Exported predicates include `xen_has_pv_devices()`, `xen_has_pv_nic_devices()`, `xen_has_pv_disk_devices()`, and `xen_has_pv_and_legacy_disk_devices()`. `xen_unplug_emulated_devices()` performs the actual unplug. `parse_xen_emul_unplug()` parses the early `xen_emul_unplug=` parameter.

Control flow and state: Static `xen_emul_unplug` accumulates user/default requested unplug bits; `xen_platform_pci_unplug` records the final post-unplug state. PV/PVH domains always report PV devices; HVM depends on platform PCI availability, user flags, and frontend/platform-driver build-time requirements. Defaults unplug NICs/disks only when matching PV frontends and platform PCI support are compiled. PVH skips unplug because it has no emulated devices.

Dependencies and integration points: It depends on Xen platform I/O ports, frontend availability helpers (`xen_must_unplug_*`), Xen domain predicates, early boot parameters, and HVM guest initialization.

Risks and test signals: Wrong unplug decisions can leave duplicate disk/NIC drivers or remove the boot disk before PV frontend is available. Test signals include HVM boot with blkfront/netfront built-in or modular, `xen_emul_unplug=never/unnecessary/all/...`, host blacklist behavior, unknown protocol warnings, PVH no-op, and correct `xen_has_pv_*` answers for driver probing.
