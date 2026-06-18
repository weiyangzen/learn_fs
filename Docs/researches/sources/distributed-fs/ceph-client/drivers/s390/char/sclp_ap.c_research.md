<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_ap.c -->
## sources/distributed-fs/ceph-client/drivers/s390/char/sclp_ap.c

**Purpose:** This file provides SCLP helpers to configure and deconfigure s390 AP crypto adapters.

**Important APIs and functions:** Exported functions are `sclp_ap_configure(u32 apid)` and `sclp_ap_deconfigure(u32 apid)`. Both call `do_ap_configure()` with command words `SCLP_CMDW_CONFIGURE_AP` or `SCLP_CMDW_DECONFIGURE_AP`. `struct ap_cfg_sccb` contains only the SCCB header.

**Control flow, state, and persistence:** The operation first checks `SCLP_HAS_AP_RECONFIG`, allocates one DMA-capable zero page for the SCCB, encodes the AP ID into bits 8..15 of the command word, and sends a synchronous SCLP request. Accepted response codes are `0x0020`, `0x0120`, `0x0440`, and `0x0450`; other responses become `-EIO`. No state is persisted after the request.

**Dependencies and integration:** It uses the SCLP core synchronous request API and exports symbols for AP bus or crypto reconfiguration code. It depends on the facility bits discovered in `sclp.facilities`.

**Risks and test signals:** Risks include AP IDs wider than 8 bits being truncated by `(apid & 0xff) << 8`, facility bit mismatch, and response-code changes not reflected in the accepted list. Test signals are configure/deconfigure success, unsupported facility returning `-EOPNOTSUPP`, simulated nonaccepted response warning, and memory allocation failure handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_ap.c -->
