# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/firmware.c

Purpose: Probes early pseries firmware capabilities from flat device-tree properties and sets `powerpc_firmware_features` bits for hypervisor calls and architecture vector features.

Important APIs/types/functions: Defines `struct hypertas_fw_feature`, `hypertas_fw_features_table`, `fw_hypertas_feature_init()`, `struct vec5_fw_feature`, `vec5_fw_features_table`, `fw_vec5_feature_init()`, `probe_fw_features()`, and `pseries_probe_fw_features()`.

Control flow: Early flat-DT scan visits depth-1 `rtas` and `chosen` nodes. The RTAS path reads `ibm,hypertas-functions`, marks LPAR, and matches NUL-separated hcall names, with optional wildcard suffix matching, to feature bits. The chosen path reads `ibm,architecture-vec-5` and maps option-vector bits to firmware features. Secure guests disable `FW_FEATURE_PUT_TCE_IND` after hypertas parsing.

State and persistence: Persistent state is the global firmware feature bitmask. The feature tables are `__initdata`, and static flags in `probe_fw_features()` terminate scanning once both relevant nodes are seen.

Dependencies and integration points: Depends on early flat device tree APIs, firmware feature flags, option-vector macros, pseries setup, and secure guest detection. Many pseries subsystems gate behavior on the bits set here.

Risks: Matching is string-table based and sensitive to firmware naming. Wildcard matching only supports trailing `*`. Secure guest feature masking must stay aligned with DMA/TCE security constraints. Missing early properties can disable downstream functionality.

Test signals: Early boot feature logs, `/proc/cpuinfo` or debug exposure of firmware features, LPAR/SPLPAR/VIO/PLPKS/PAPR SCM feature-dependent drivers probing, secure guest boot confirming TCE-indirect disable, and flat-DT unit tests are useful.

Source read size: 191 lines, 5222 bytes.
