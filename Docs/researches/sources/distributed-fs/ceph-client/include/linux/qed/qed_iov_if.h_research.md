# sources/distributed-fs/ceph-client/include/linux/qed/qed_iov_if.h

Purpose: declares the SR-IOV hypervisor-facing operation table that lets a PF driver configure and manage child VFs.

Important APIs/types/functions: `struct qed_iov_hv_ops` contains callbacks for `configure`, `set_mac`, `set_vlan`, `get_config`, `set_link_state`, `set_spoof`, `set_rate`, and `set_trust`. It includes `qed_if.h` for `struct qed_dev` and Linux VF info types via that dependency.

Control flow: when SR-IOV is enabled, the Ethernet ops table can expose `qed_iov_hv_ops` to the PF-side netdev. Administrative operations from iproute2/sysfs/netdev call these callbacks to create VFs, assign MAC/VLAN, query VF config, force link state, enable/disable spoof checking, set min/max rates, and mark VFs trusted.

State and persistence: VF configuration is runtime PF/firmware state and may be reflected in hardware bulletin/config structures. It is not stored by this header. Some settings may survive until PF reset or VF teardown depending on core implementation.

Dependencies and integration points: integrates QED Ethernet SR-IOV support with Linux netdev VF administration (`ifla_vf_info`) and the optional `CONFIG_QED_SRIOV` pointer in `qed_eth_ops`.

Risks: incorrect VF IDs, trust/spoof settings, or rate limits can compromise isolation or traffic shaping. MAC/VLAN operations must coordinate with VF driver state and firmware bulletin updates. Optional availability depends on SR-IOV config.

Test signals: create/destroy VFs, set/query VF MAC and VLAN, force link up/down/auto, spoof-check toggles, min/max rate limits, trust mode, VF reset while PF settings change, and negative tests for out-of-range VF IDs.
