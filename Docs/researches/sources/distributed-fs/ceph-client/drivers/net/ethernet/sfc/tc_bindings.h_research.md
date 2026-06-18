# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/tc_bindings.h

Purpose: declares the SFC TC binding interface used by netdev setup, representors, indirect block registration, and netdev notifiers. It is compiled only when `CONFIG_SFC_SRIOV` is enabled.

Important APIs/types: exports `efx_tc_setup_block()`, `efx_tc_setup()`, `efx_tc_indr_setup_cb()`, `efx_tc_netdev_event()`, and `efx_tc_block_unbind()`. It forward-declares `struct efx_rep` and includes `net_driver.h`; with SR-IOV disabled it provides a no-op `efx_tc_netdev_event()` returning `NOTIFY_DONE`.

State and integration: this header creates the compile-time boundary between the core driver and SR-IOV/representor TC code. No state is persisted here.

Risks and tests: call sites must be guarded by the same config assumptions, because most declarations disappear when SR-IOV is disabled. Build coverage should include `CONFIG_SFC_SRIOV=y/m` and disabled configurations.
