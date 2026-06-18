# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/Makefile

## Purpose

The NIC `Makefile` defines how Marvell RVU Ethernet PF, VF, and representor drivers are built and which optional objects are included for DCB, MACsec, and XFRM/IPsec offload support.

## Important APIs, Types, And Functions

- `obj-$(CONFIG_OCTEONTX2_PF)` builds `rvu_nicpf.o` and `otx2_ptp.o`.
- `obj-$(CONFIG_OCTEONTX2_VF)` builds `rvu_nicvf.o` and `otx2_ptp.o`.
- `obj-$(CONFIG_RVU_ESWITCH)` builds `rvu_rep.o`.
- `rvu_nicpf-y` includes PF core, common, tx/rx, ethtool, flows, TC, CN10K/CN20K, DMAC filters, devlink, QoS, and AF_XDP objects.
- `rvu_nicvf-y` includes `otx2_vf.o`.
- `rvu_rep-y` includes NIC-side `rep.o`.
- Conditional additions include `otx2_dcbnl.o`, `cn10k_macsec.o`, and `cn10k_ipsec.o`.
- `ccflags-y` adds the AF directory include path so NIC code can include AF ABI headers such as `rvu.h`, `rvu_trace.h`, `mbox.h`, and `npc.h`.

## Control Flow

Build control is driven by Kconfig symbols. Enabling the PF driver pulls common hardware support and both CN10K/CN20K specialization objects into the PF module. Enabling optional features links additional implementation files into the PF object so runtime capability checks can expose hardware features only when kernel frameworks are available.

## State And Persistence

The file has no runtime state. It determines which symbols exist in the resulting kernel/module. Feature absence changes runtime behavior through missing objects and inline stubs in headers such as `cn10k_ipsec.h`.

## Dependencies And Integration Points

It integrates the NIC directory with the AF header directory. It depends on Kconfig symbols `CONFIG_OCTEONTX2_PF`, `CONFIG_OCTEONTX2_VF`, `CONFIG_RVU_ESWITCH`, `CONFIG_DCB`, `CONFIG_MACSEC`, and `CONFIG_XFRM_OFFLOAD`. The object list must align with exported symbols used by PF/VF/representor source files.

## Risks

- `otx2_ptp.o` is listed for both PF and VF objects; build-system behavior must avoid duplicate or unintended linkage depending on how objects are combined.
- Optional code paths must have correct stubs when objects are not built.
- Adding source files without updating this list silently omits functionality.
- Include path dependence on the AF directory means header ABI churn can break NIC builds.

## Test Signals

Build matrix coverage for PF-only, VF-only, PF+VF, representor, DCB, MACsec, and XFRM offload configurations is the primary signal. Module load/probe tests should confirm optional feature symbols are present only when configured.
