# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_gsc_binary_headers.h

## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_gsc_binary_headers.h

### Purpose
`intel_gsc_binary_headers.h` defines packed structures used to parse Intel GSC firmware binaries and extract partition, directory, and manifest metadata.

### Important APIs, Types, And Functions
It defines `struct intel_gsc_version`, `struct intel_gsc_partition`, `struct intel_gsc_layout_pointers`, `struct intel_gsc_bpdt_header`, `struct intel_gsc_bpdt_entry`, `struct intel_gsc_cpd_header_v2`, `struct intel_gsc_cpd_entry`, and `struct intel_gsc_manifest_header`, plus BPDT, CPD, entry type, offset, and compression masks.

### Control Flow
No code executes here. The structures support walking layout pointers, boot partitions, BPDT entries, CPD entries, and the manifest header in `intel_gsc_fw_get_binary_info()`.

### State, Persistence, Dependencies, Integration, Risks, And Test Signals
The header owns no state and depends only on packed integer types and bit macros. Integration is with GSC firmware selection/version parsing. Risks are binary-format drift, wrong packed layout, unchecked offsets in users, and string matching CPD entry names. Test signals include successful extraction of release/security versions and rejection of malformed signatures or undersized images.
