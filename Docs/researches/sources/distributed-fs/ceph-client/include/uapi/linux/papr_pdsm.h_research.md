# sources/distributed-fs/ceph-client/include/uapi/linux/papr_pdsm.h

Purpose: Defines PAPR SCM NVDIMM DSM payloads embedded in `ND_CMD_CALL` requests for libndctl and the powerpc papr_scm driver.

Important APIs/types/functions: Exports `ND_PDSM_PAYLOAD_MAX_SIZE`, `ND_PDSM_HDR_SIZE`, health status constants, extension flags, `struct nd_papr_pdsm_health`, SMART injection flags, `struct nd_papr_pdsm_smart_inject`, `enum papr_pdsm`, `union nd_pdsm_payload`, and packed `struct nd_pkg_pdsm`.

Control flow: Userspace constructs a generic `struct nd_cmd_pkg` with family `NVDIMM_FAMILY_PAPR_SCM`, command `PAPR_PDSM_HEALTH` or `PAPR_PDSM_SMART_INJECT`, and a following `nd_pkg_pdsm`. The libnvdimm layer routes it to papr_scm, which fills `cmd_status`, firmware status fields, and the selected payload union.

State and persistence behavior: Health payloads report persistent-memory durability risk: unarmed DIMM, bad shutdown/restore, scrubbed state, locked/encrypted state, health class, optional fuel gauge, and optional DSC. SMART injection is a test/debug mutation of reported firmware health state.

Dependencies and integration points: Depends on `<linux/types.h>` and `<linux/ndctl.h>`. Integrates with libndctl, ndctl health reporting, PAPR platform firmware calls, and powerpc NVDIMM drivers.

Risks: Packed layout and fixed 184-byte payload size are ABI-sensitive. Health flags affect operator decisions about persistent-memory reliability. SMART injection should be gated to debug/test paths. Reserved fields should be zeroed for future compatibility.

Test signals: Use ndctl/libndctl to issue health queries, validate payload size and `nd_fw_size`, test optional extension flags, inject fatal and bad-shutdown SMART states on supported platforms, and verify packed layout across 32/64-bit builds.
