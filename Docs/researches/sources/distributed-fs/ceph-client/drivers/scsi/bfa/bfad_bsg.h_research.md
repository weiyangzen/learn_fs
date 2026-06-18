# sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfad_bsg.h

## Purpose
`bfad_bsg.h` defines the private userspace/kernel ABI for BFAD vendor-specific FC BSG commands. It enumerates all `IOCMD_*` operation codes and declares the command/result payload structures consumed by `bfad_bsg.c`.

## Important APIs, Types, and Functions
The leading enum assigns stable numeric command IDs for IOC, IOCFC, port, lport/rport/vport, fabric, rate-limit, FCPIM, ITNIM, PCI function, adapter mode, BBCR, FAA, CEE, SFP, flash, diagnostics, PHY, debug, boot, trunk, QoS, VF, LUN masking, D-port, throttle, TFRU, FRUVPD, and FC pass-through commands. Nearly every structure begins with `bfa_status_t status` and `u16 bfad_num`, then command-specific identifiers and payloads. Important structures include `bfa_bsg_ioc_info_s`, `bfa_bsg_ioc_attr_s`, `bfa_bsg_port_stats_s`, `bfa_bsg_lport_get_rports_s`, `bfa_bsg_rport_*`, `bfa_bsg_flash_s`, `bfa_bsg_debug_s`, `bfa_bsg_fcpim_lunmask_s`, `bfa_bsg_tfru_s`, `bfa_bsg_fruvpd_s`, and `bfa_bsg_fcpt_s`. `struct bfa_bsg_data` is packed and carries a byte length plus a userspace pointer for FC pass-through control data. `bfad_chk_iocmd_sz` validates composite command sizes.

## Control Flow
The header itself has no execution flow, but it defines the layout expected by `bfad_im_bsg_vendor_request` and `bfad_im_bsg_els_ct_request`. Vendor command buffers are passed inline through BSG scatterlists and may include trailing payload bytes immediately after the command structure. FC pass-through uses `bfa_bsg_data` in the request header to point to a separate userspace `bfa_bsg_fcpt_s` block.

## State and Persistence
The structs describe both transient read/write state and persistent operations. Name, port, flash, boot, ethboot, PHY update, FRU/VPD, QoS, trunking, LUN mask, and debug control commands can change device or driver state. Query structs return snapshots of BFA/FCS state and hardware statistics. The ABI embeds fixed maximum buffer sizes for TFRU and FRUVPD transfers.

## Dependencies and Integration Points
It includes `bfa_defs.h` and `bfa_defs_fcs.h`, so the ABI exposes BFA-defined WWN, MAC, stats, adapter, port, diagnostic, QoS, boot, and LUN-mask types. `bfad_bsg.c` relies on the structure sizes exactly when checking payload lengths and copying data.

## Risks
This is an ABI header: changing enum ordering, field order, packing, or fixed sizes breaks userspace tools. Many structs contain native C types and `u64` pointers, making 32-bit userspace compatibility and endian assumptions important. Inline buffers such as `BFA_MAX_FRUVPD_TRANSFER_SIZE` require careful payload-size validation in callers.

## Test Signals
ABI tests should assert structure sizes, enum values, packed `bfa_bsg_data` layout, and command size checks across architectures. Userspace tools should be tested against mismatched payload lengths and unsupported command IDs to confirm stable failure status.
