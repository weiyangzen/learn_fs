# sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfad_bsg.c

## Purpose
`bfad_bsg.c` implements the driver-private FC BSG interface. It is an ioctl-like command dispatcher for adapter, port, lport/rport, vport, FCP initiator, diagnostics, flash, PHY, boot, QoS, trunking, LUN masking, FRU/VPD, debug, and FC ELS/CT pass-through operations.

## Important APIs, Types, and Functions
The main exported entry points are `bfad_im_bsg_request` and `bfad_im_bsg_timeout`. Vendor commands enter `bfad_im_bsg_vendor_request`, are copied from request scatterlists into a linear buffer, and then dispatched by `bfad_iocmd_handler`. That handler maps `IOCMD_*` values to many `bfad_iocmd_*` helpers. ELS/CT pass-through enters `bfad_im_bsg_els_ct_request`, which consumes a userspace `bfa_bsg_fcpt_s`, resolves lport/rport context, maps request and response buffers through coherent DMA via `bfad_fcxp_map_sg`, sends through `bfa_fcxp_send`, and completes from `bfad_send_fcpt_cb`.

## Control Flow
Vendor request flow is simple: allocate `payload_kbuf`, `sg_copy_to_buffer`, dispatch, copy the updated command/result block to reply scatterlists, fill `fc_bsg_reply`, and call `bsg_job_done` on success. The dispatcher has broad categories: IOC enable/disable/getattr/stats; port enable/disable/config/stats; LPORT/RPORT/VPORT/Fabric queries; rate limiting and FCPIM stats; PCI function and adapter mode management; CEE/SFP/flash/diagnostic/PHY operations; debug trace/core/log controls; boot/ethboot/preboot; trunk/QoS/VF; LUN mask and throttle; TFRU/FRUVPD. Many handlers lock `bfad_lock`, issue a BFA module call, unlock, and wait on a `bfad_hal_comp`. Variable payload handlers verify `payload_len == sizeof(header) + expected_buffer_size` with `bfad_chk_iocmd_sz`.

ELS/CT flow uses `bfa_bsg_data` embedded after `fc_bsg_request` to copy a control block from an arbitrary user pointer. It verifies local port existence and online state, optionally resolves a remote port for RPT commands, allocates DMA request/response buffers, sends an FCXP, waits for completion, populates CT/ELS reply status, copies DMA response into the BSG reply scatterlist, copies the updated control block back to userspace, and completes the job only on `BFA_STATUS_OK`.

## State and Persistence
Handlers mutate live driver and firmware state: IOC enable/disable state, adapter/port names, port topology/speed/ALPA/max frame size, BBCR, rate limiting, QoS, trunking, flash partitions, boot/PXE configuration, LUN masking, queue-scan flags, profiling state, port logs, trace state, firmware core offsets, and FRU/VPD contents. Runtime stats are read or cleared in BFA/FCS structures. Persistent writes occur indirectly through BFA flash/FRU helpers for boot config, ethboot config, flash parts, PHY firmware, and FRUVPD/TFRU data.

## Dependencies and Integration Points
This file depends on the BSG ABI in `bfad_bsg.h`, BFAD core state in `bfad_drv.h`, IM helpers in `bfad_im.h`, Linux BSG scatterlist helpers, usercopy, PCI DMA APIs, and almost every BFA service module. It is wired into the FC transport template from `bfad_attr.c`.

## Risks
The surface is privileged and very broad. Some commands use direct userspace pointers (`bfa_bsg_data.payload`) in addition to BSG scatterlists, so compat, bounds, and TOCTOU issues need attention. Several handlers perform unbounded waits on firmware completions. Many commands trust structure fields for buffer sizes after only aggregate payload-length checks; integer overflow and large allocation behavior should be scrutinized. `bfad_iocmd_lunmask` calls SCSI host operations while holding `bfad_lock`, and `bfad_reset_sdev_bflags` takes `host_lock`, so lock ordering matters. Flash/PHY/FRU write commands can persistently alter adapter state.

## Test Signals
Test with representative BSG vendor commands for each category, malformed payload lengths, zero counts, unknown WWNs/VF IDs, offline ports, firmware failure completions, and large buffer sizes. ELS/CT tests should validate HST versus RPT paths, unknown remote ports, timeout behavior (`-EAGAIN`), DMA cleanup on all error exits, and reply length/status consistency.
