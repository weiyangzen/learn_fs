# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_sriov.h

## Purpose

`ice_sriov.h` declares the SR-IOV interface used by the ice driver and provides no-op or `-EOPNOTSUPP` stubs when `CONFIG_PCI_IOV` is disabled. It also defines VF register constants, polling constants, and VF resource sizing limits shared with SR-IOV implementation and callers.

## Important APIs, Types, And Functions

- Register/status constants include `VF_DEVICE_STATUS`, `VF_TRANS_PENDING_M`, `ICE_PCI_CIAD_WAIT_COUNT`, and `ICE_PCI_CIAD_WAIT_DELAY_US`.
- VF resource constants define minimum queue pairs, non-queue MSI-X vector count, common MSI-X sizing tiers, minimum interrupt count, and VF reset retry/sleep limits.
- When PCI IOV is enabled, declarations cover VF lifecycle, SR-IOV configure, MAC/VLAN/bandwidth/trust/link/spoof/stat netdev hooks, VFLR handling, LAN overflow handling, MDD reporting, MSI restoration, MSI-X resource sysfs hooks, virtchnl pattern validation, and single Tx queue disable.
- When PCI IOV is disabled, inline stubs preserve call sites while returning unsupported or doing nothing.

## Control Flow

The header has compile-time control flow through `#ifdef CONFIG_PCI_IOV`. Enabled builds call real SR-IOV implementation in `ice_sriov.c` and related VF files. Disabled builds compile callers against stubbed operations that cannot enable or administer VFs.

## State And Persistence

The header does not own state. It defines constants used for VF resource allocation and reset polling, and prototypes for functions that mutate PF/VF runtime and hardware state.

## Dependencies And Integration Points

It includes `virt/fdir.h`, `ice_vf_lib.h`, and `virt/virtchnl.h`, and exposes entry points to PCI/sysfs SR-IOV, netdev VF administration, VF reset handling, MDD reporting, VF queue control, and virtchnl validation code.

## Risks

- Disabled-build stubs must match real signatures. Signature drift can break non-IOV builds or hide missing call-site guards.
- Resource constants encode policy for MSI-X and queue sizing; changing them affects VF capability advertised to guest drivers.
- Functions declared here span several subsystems, so include-order or type-dependency changes can have broad build impact.

## Test Signals

Build testing should cover both `CONFIG_PCI_IOV=y` and disabled configurations. Runtime tests for enabled builds should exercise every declared netdev VF hook, SR-IOV sysfs configuration, VFLR processing, MDD logging, MSI restore, MSI-X resize, and queue-disable integration.
