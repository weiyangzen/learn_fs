<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/arm64/gic_v3_its.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/arm64/gic_v3_its.h

Purpose: this header declares guest-side helpers for initializing and programming a GICv3 ITS command queue in KVM selftests.

Important APIs, types, and functions: `its_init()` configures collection table, device table, and command queue base/size. Command helpers emit `MAPD`, `MAPC`, `MAPTI`, `INVALL`, and `SYNC` operations: `its_send_mapd_cmd()`, `its_send_mapc_cmd()`, `its_send_mapti_cmd()`, `its_send_invall_cmd()`, and `its_send_sync_cmd()`.

Control flow: declarations only. Implementations serialize ITS commands into the guest command queue and are used after redistributors and ITS tables are allocated.

State, persistence, and dependencies: no direct state. Dependencies include `gpa_t`, `u32`, `bool`, and table sizing conventions from the surrounding selftest headers. It is integrated by LPI/ITS tests such as `vgic_lpi_stress.c`.

Risks and edge cases: callers must provide correctly aligned and sized ITS tables and command queue memory. Incorrect device IDs, event IDs, collection IDs, or missing sync commands can make `KVM_SIGNAL_MSI` fail translation.

Test signals: successful downstream LPI tests show that mappings and invalidations created through these helpers are accepted by the emulated ITS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/arm64/gic_v3_its.h -->
