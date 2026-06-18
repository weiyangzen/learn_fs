# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_vf_lib_private.h

## Purpose
Declares private VF library helpers intended only for virtualization translation units that are compiled under `CONFIG_PCI_IOV`. It separates internal SR-IOV implementation functions from the broader public VF API in `ice_vf_lib.h`.

## Important APIs
Exports initialization/teardown (`ice_initialize_vf_entry()`, `ice_deinitialize_vf_entry()`), queue disable, VF init checks, errno-to-virtchnl translation, port-info lookup, spoofchk apply, trust and link helpers, control-VSI setup/release/invalidation, host configuration initialization, and LAN VSI invalidation/release.

## Control Flow and State
The header contains a compile-time warning if included without `CONFIG_PCI_IOV`, reinforcing that these helpers do not have fallback stubs. Callers are expected to be in SR-IOV-only object lists and to use these functions while holding the relevant VF locks documented by the implementation.

## Dependencies and Integration Points
Includes `ice_vf_lib.h`; used by virtchnl queue, FDIR, VF management, and other SR-IOV-only code paths that need internal lifecycle helpers.

## Risks
Including this header from always-built code breaks the intended build contract. Exposing too much through the private header also increases coupling to VF reset and VSI internals.

## Test Signals
Build matrix should cover `CONFIG_PCI_IOV=y` and `n`, ensuring no always-built `.c` file includes this private header. Runtime tests should validate that private helpers are only called under expected VF locks and state gates.
