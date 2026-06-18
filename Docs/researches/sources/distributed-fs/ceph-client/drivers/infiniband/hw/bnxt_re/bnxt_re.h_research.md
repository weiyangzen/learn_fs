# sources/distributed-fs/ceph-client/drivers/infiniband/hw/bnxt_re/bnxt_re.h

Purpose: central private header for the Broadcom NetXtreme-C/E RoCE driver. It defines the main device object, resource limits, recovery flags, GSI state, notification queue bookkeeping, doorbell pacing state, debugfs pointers, and cross-file prototypes.

Important APIs and types: `struct bnxt_re_dev` embeds `struct ib_device` and links the RDMA device to `net_device`, auxiliary device, `bnxt_en_dev`, chip context, RCFW channel, qplib resources, device attributes, privileged DPI, CQs/QPs/SRQs hashes, GSI context, statistics, DCB workqueue, congestion-control and CQ-coalescing debugfs state, and RoCE mirror state. Supporting types include `bnxt_re_ring_attr`, `bnxt_re_gsi_context`, `bnxt_re_sqp_entries`, `bnxt_re_nq_record`, `bnxt_re_pacing`, and `bnxt_re_en_dev_info`.

Control flow and integration: executable logic is limited to small inline helpers. `bnxt_re_chip_gen_p7()` classifies chips, `rdev_to_dev()` returns a device pointer, `bnxt_re_set_pacing_dev_state()` mirrors error-detach state into pacing data, and `bnxt_re_read_context_allowed()` gates firmware context reads on chip generation and HWRM interface version. Function prototypes connect to `main`, HWRM VNIC setup, hardware counters, and pacing alert handling.

State and persistence: all state is runtime kernel memory. The main `bnxt_re_dev` structure is the persistence point across RDMA object lifetimes: flags track registration, channel/resource allocation, detach/error state, and stats availability; lists and hashes retain live objects; atomic counters track resource use; debugfs dentries expose selected fields while the device is registered.

Dependencies: includes RDMA uverbs definitions, `hw_counters.h`, Linux hashtable support, and Broadcom Ethernet/chip constants through transitive qplib headers. It is consumed by nearly every `bnxt_re` implementation file.

Risks: this header is a high-blast-radius coupling point. Incorrect flag use can break recovery or detach paths. Resource counters and hash/list updates must remain balanced with object create/destroy paths. Debugfs pointers require careful cleanup ordering. Chip-generation predicates affect context sizes, doorbell FIFO depth, and supported firmware operations.

Test signals: full driver build, probe/remove/recovery testing, resource create/destroy leak checks, debugfs add/remove under device detach, chip-generation matrix testing for P5/P7 versus older devices, and KASAN/lockdep around QP list, CQ/SRQ hashes, and pacing locks.
