<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/q_in_vni_veto.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/q_in_vni_veto.sh

Purpose: Spectrum-1-specific negative test that verifies VXLAN cannot be configured on top of an 802.1ad VLAN-aware bridge in a way unsupported by mlxsw.

Important functions/APIs: uses forwarding `lib.sh`; defines `setup_prepare`, `cleanup`, and `create_vxlan_on_top_of_8021ad_bridge`. It uses `ip link` bridge/VXLAN setup and `bridge vlan add`.

Control flow: creates an 802.1ad bridge and VXLAN device, enslaves a physical port and VXLAN, then expects `bridge vlan add ... pvid untagged` on the VXLAN to fail and include `mlxsw_spectrum` extack text.

State/dependencies: temporary bridge, VXLAN, and port master state. Risks include extack wording changes, Spectrum-version applicability, and cleanup after failure. Test signals are failure of unsupported VLAN mapping plus extack presence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/spectrum/q_in_vni_veto.sh -->
