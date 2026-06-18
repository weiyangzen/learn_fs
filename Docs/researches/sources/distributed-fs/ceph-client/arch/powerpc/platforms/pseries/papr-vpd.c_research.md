# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/papr-vpd.c

Purpose: Exposes PAPR vital product data retrieval through `/dev/papr-vpd`, returning an fd-backed immutable blob for a requested location code.

Important APIs/types/functions: Defines `struct rtas_ibm_get_vpd_params`, `rtas_ibm_get_vpd()`, VPD sequence begin/end/work callbacks, `papr_vpd_create_handle()`, `papr_vpd_dev_ioctl()`, and miscdevice `papr-vpd`.

Control flow: Userspace submits `PAPR_VPD_IOC_CREATE_HANDLE` with a nul-terminated `papr_location_code`. The driver validates the location code, configures a `papr_rtas_sequence`, serializes RTAS `ibm,get-vpd` calls with `rtas_ibm_get_vpd_lock`, repeatedly fills a 4 KiB work area until sequence completion, and hands the completed data to the common fd/blob reader helpers.

State and persistence: The only long-lived user-visible state is the anonymous file/blob created by `papr_rtas_setup_file_interface()`. RTAS sequence state tracks current sequence number, last status, bytes written, static location code, and work area while the blob is generated.

Dependencies and integration points: Depends on RTAS `ibm,get-vpd`, `papr-rtas-common` blob/handle utilities, RTAS work areas, PAPR VPD UAPI, and pseries machine initcalls.

Risks: Firmware supports only one VPD sequence at a time, so serialization is required. Location-code termination, work-area write bounds, and sequence restart handling are key correctness points. A VPD change can force `-EAGAIN` and retry logic in the common sequence generator.

Test signals: Validate handle creation for valid and unterminated location codes, sequential read/seek/release behavior, RTAS sequence-more-data and sequence-complete paths, VPD-changed retry, missing RTAS token, and concurrent callers under lockdep.

Source read size: 275 lines, 8391 bytes.
