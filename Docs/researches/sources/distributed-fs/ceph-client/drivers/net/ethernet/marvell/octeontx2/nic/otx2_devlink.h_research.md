# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_devlink.h

`otx2_devlink.h` is the small declaration header for devlink integration. It defines `struct otx2_devlink`, which stores the generic `struct devlink *dl` and the owning `struct otx2_nic *pfvf`, and declares `otx2_register_dl` and `otx2_unregister_dl`.

The header is included by `otx2_common.h` so `struct otx2_nic` can carry `pfvf->dl`. PF probe registers devlink after TC setup and unregisters it in error unwind and remove paths. The header has no persistent state; validity is bounded by successful registration and unregister.

Dependencies are mostly include-order based: `struct devlink` and `struct otx2_nic` must be visible through surrounding headers. The risk is lifecycle misuse, especially calling unregister without a successful register or dereferencing `pfvf->dl` after unregister. Test signals are successful build, visible devlink params after probe, and no lifetime errors on probe-failure unwind or module removal.
