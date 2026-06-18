# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_gsc_fw.c

## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_gsc_fw.c

### Purpose
`intel_gsc_fw.c` manages GSC firmware status probing, binary metadata parsing, firmware copy/load submission, post-load compatibility query, and proxy-readiness status reporting.

### Important APIs, Types, And Functions
Exports are `intel_gsc_fw_get_binary_info()`, `intel_gsc_uc_fw_upload()`, `intel_gsc_uc_fw_init_done()`, `intel_gsc_uc_fw_proxy_init_done()`, and `intel_gsc_uc_fw_proxy_get_status()`. Important helpers include `gsc_is_in_reset()`, `gsc_uc_get_fw_status()`, `gsc_fw_load_prepare()`, `gsc_fw_load()`, `gsc_fw_wait()`, and `gsc_fw_query_compatibility_version()`. Local MKHI/GSC version message structs define the compatibility query payload.

### Control Flow
Binary parsing validates layout size, boot1 bounds, BPDT signature and entries, CPD marker and entries, finds `RBEP.man`, extracts release/security versions, and enforces MTL/ARL version rules. Upload skips if already initialized, sanitizes firmware state, requires GSC reset state, copies firmware into dedicated local memory, marks FLR-on-fini, submits `GSC_FW_LOAD`, waits for init complete, sends an MKHI compatibility query through HECI, verifies selected file version, and marks the firmware transferred pending proxy initialization.

### State, Persistence, Dependencies, Integration, Risks, And Test Signals
Persistent state is `gsc->fw`, `gsc->release`, `gsc->security_version`, file-selected compatibility version, `gsc->local`, and uncore FLR cleanup intent. Dependencies include GSC binary headers, stolen/local memory mapping, GSC engine command submission, HECI packet submit, GuC VMA allocation, runtime PM, and HECI status registers. Integration points are `intel_gsc_uc` workqueue loading, MEI proxy setup, HuC-by-GSC auth, debugfs status, and firmware core version selection. Risks include malformed image offsets, stale firmware already running with inconsistent driver state, load timeouts, GSC not in reset, too-old ARL firmware, and compatibility-query protocol errors. Test signals are FWSTS init/proxy states, logged release/cv/SVN, load failure status, and valid MKHI reply size.
