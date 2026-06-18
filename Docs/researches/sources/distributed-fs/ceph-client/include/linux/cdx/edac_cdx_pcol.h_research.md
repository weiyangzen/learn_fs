## sources/distributed-fs/ceph-client/include/linux/cdx/edac_cdx_pcol.h

**Purpose:** This header defines CDX MCDI protocol constants for EDAC DDR configuration queries.

**Important APIs/types/functions:** It includes CDX MCDI helpers and defines `MC_CMD_EDAC_GET_DDR_CONFIG`, input offset/length for `CONTROLLER_INDEX`, output word length, and DDR config register offset/length constants.

**Control flow, state, persistence:** There is no code. EDAC/CDX clients use these constants to encode MCDI requests and decode responses for DDR controller configuration. Returned configuration reflects hardware/firmware state.

**Dependencies/integration:** Depends on `linux/cdx/mcdi.h` and the CDX firmware command protocol. Integrated by EDAC drivers that query CDX-managed DDR controllers.

**Risks and test signals:** Risks are protocol-version drift, incorrect offset/length interpretation, and insufficient output buffer sizing. Test signals include successful `cdx_mcdi_rpc()` for DDR config, decoded EDAC topology, firmware negative responses, and buffer length validation.
