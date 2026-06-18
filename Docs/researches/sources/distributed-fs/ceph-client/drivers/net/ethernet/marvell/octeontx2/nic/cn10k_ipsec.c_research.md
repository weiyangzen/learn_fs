# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/cn10k_ipsec.c

## Purpose

`cn10k_ipsec.c` implements CN10K outbound ESP crypto offload through XFRM device offload and the CPT engine. It attaches/configures a CPT LF, allocates its instruction queue, validates XFRM states, writes outbound SA context into hardware, adds CPT/NIX scatter-gather descriptors for offloaded packets, and transmits packets by flushing CPT instructions through LMTST.

## Important APIs, Types, And Functions

- `DEFINE_STATIC_KEY_FALSE(cn10k_ipsec_sa_enabled)` is declared in the header and controlled when SAs exist.
- CPT LF lifecycle helpers attach/detach resources, allocate/free/configure CPT LF, allocate/init/free IQ memory, enable/disable IQ, and clean the CPT path.
- `cn10k_cpt_device_set_inuse()/available()/unavailable()` serialize direct CPT operations through an atomic state machine.
- `cn10k_outb_write_sa()` issues a CPT write-SA instruction and flushes the CPT context cache.
- `cn10k_outb_prepare_sa()` converts an XFRM AES-GCM state into `struct cn10k_tx_sa_s`.
- `cn10k_ipsec_validate_state()` accepts only outbound ESP AES-GCM-ICV16, transport/tunnel, IPv4/IPv6, crypto-mode, seqiv, no ESN, no encap, no TFC.
- XFRM ops `cn10k_ipsec_add_state()` and `cn10k_ipsec_del_state()` manage SA qmem and `x->xso.offload_handle`.
- `cn10k_ipsec_ethtool_init()` toggles CPT offload setup/cleanup.
- `cn10k_ipsec_init()` installs `xfrmdev_ops` and HW ESP feature bits.
- `otx2_sqe_add_sg_ipsec()` prepares paired CPT SG and NIX SG subdescriptors and DMA mappings.
- `cn10k_ipsec_transmit()` builds and flushes an outbound IPsec CPT instruction for a packet.

## Control Flow

Feature initialization checks the PCI device, computes 128-byte-aligned SA size, creates a workqueue, installs XFRM ops, advertises `NETIF_F_HW_ESP`, and marks CPT unavailable. Enabling through ethtool/probe attaches CPT resources, allocates a CPT LF, allocates/initializes IQ memory, configures inline outbound IPsec for the PF pcifunc, stores the CPT enqueue IO address, sets the IPsec-enabled flag, and marks CPT available. Disabling refuses while SAs exist, then disables IQ, clears queue registers, frees IQ, frees/detaches the CPT LF, and marks unavailable.

Adding an outbound state validates XFRM attributes, allocates qmem for the SA, writes a prepared SA into memory, sends a CPT write-SA instruction, stores the qmem pointer in `offload_handle`, enables the static key for the first SA, and increments `outb_sa_count`. Deletion writes a disabled SA context back to CPT, frees qmem, decrements the count, and queues work to disable the static key and update netdev features when the last SA disappears.

Transmit first verifies offload is enabled, finds the XFRM state from the skb security path, checks mode and SA handle, calculates payload/auth/IV offsets, points the CPT result to per-SQ response memory, encodes major opcode `OUTB_IPSEC`, dptr/rptr as the SG gather list before the NIX SQE, cptr as the SA IOVA, and NIXTX location/size in word 0. It reports bytes to the netdev queue, advances SQ head, and flushes the CPT instruction through LMTST.

## State And Persistence

Per-PF IPsec state is `pf->ipsec`: CPT IO address, atomic CPT state, IQ DMA memory, SA size, outbound SA count, static-key work, and workqueue. Each offloaded XFRM state owns qmem containing the hardware SA context, referenced through `x->xso.offload_handle`. Per-SQ state includes doubled SQE/CPT-SG ring and CPT response qmem from `otx2_common.c`. Hardware state persists in CPT LF registers, IQ DMA memory, CPT context cache/SA memory, and NIX/CPT inline configuration until cleanup or reset.

## Dependencies And Integration Points

The file depends on Linux XFRM offload, crypto AEAD/GCM metadata, the OTX2 mailbox/resource API, qmem, LMTST, NIX SQE structures, CPT register definitions, and common DMA mapping helpers. It integrates with `otx2_common.c` for SQ memory layout and DMA directions, with transmit code through `otx2_sqe_add_sg_ipsec()` and `cn10k_ipsec_transmit()`, and with ethtool feature control.

## Risks

- In `cn10k_outb_cptlf_iq_disable()`, `nq_ptr` and `dq_ptr` are both extracted with `CPT_LF_Q_GRP_PTR_DQ_PTR`; this looks suspicious because `NQ_PTR` has a separate mask.
- `cn10k_cpt_device_set_inuse()` busy-waits with `mdelay(1)` and no timeout while the state is `IN_USE`.
- `skb_unshare()` in `otx2_dma_map_skb_frag()` can replace a local skb pointer but does not update the caller's skb ownership, which deserves scrutiny on IPsec DMA error paths.
- Only inbound add returns unsupported; feature advertising must not imply inbound offload.
- SA count/static key updates are not obviously protected by a lock.
- Deleting a state writes a disabled SA and frees qmem even if CPT write fails.
- Transmit drop frees the skb; callers must not also free it.

## Test Signals

XFRM selftests for outbound ESP AES-GCM IPv4/IPv6 tunnel and transport, negative validation for unsupported algorithms/modes/ESN/encap/inbound, ethtool offload enable/disable with active SAs, CPT response timeout injection, SA add/delete loops, high-rate offloaded TX, DMA mapping failure tests, and reset/unload cleanup are essential.
