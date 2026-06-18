
# `sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/macsec.py`

## Purpose
Tests MACsec hardware offload API behavior, netdevsim limits, offload state/feature reflection, and VLAN-over-MACsec data path behavior with local offload and remote software MACsec.

## Important APIs, Types, And Functions
- `_require_ip_macsec()`, `_require_ip_macsec_offload()`, and `_require_macsec_offload()` gate iproute2 and device feature support.
- `_setup_macsec_sa()`, `_setup_macsec_devs()`, `_setup_vlans()`, and `_setup_vlan_ips()` build matching local/remote MACsec and VLAN topology.
- `test_offload_api()` creates SecYs, adds SAs/SCs, and toggles offload through rtnetlink and genetlink.
- `test_max_secy()` and `test_max_sc()` are nsim-only limit tests.
- `test_offload_state()`, `test_vlan()`, and `test_vlan_toggle()` verify state, feature snapshots, VLAN propagation, and ping behavior.

## Control Flow
`main()` creates `NetDrvEpEnv` and runs the MACsec cases. Tests use a PID-derived interface-name prefix to avoid collisions. Offload tests create devices, defer deletion, perform ip/macsec operations, and assert expected command failures or feature states.

## State And Persistence
Creates MACsec interfaces, TX/RX secure associations, VLAN interfaces, addresses, and remote software MACsec peers. Deferred `ip link del` calls clean up both local and remote devices.

## Dependencies And Integration Points
Depends on `ip macsec`, iproute2 offload syntax, `macsec-hw-offload` ethtool feature, `NetDrvEpEnv`, remote endpoint commands, and optionally netdevsim debugfs VLAN state.

## Risks
The fixed MACsec key and port/SCI values are test-only. Offloaded netdevsim lacks datapath handling, so ping checks are skipped for offloaded nsim cases. Feature dictionary equality assumes stable ethtool JSON ordering/content.

## Test Signals
Pass signals include rejected offload disable while SAs exist, expected max SecY/SC failures on nsim, matching offload state strings and feature snapshots, VLAN debugfs presence matching offload state, and successful ping when datapath is expected.
