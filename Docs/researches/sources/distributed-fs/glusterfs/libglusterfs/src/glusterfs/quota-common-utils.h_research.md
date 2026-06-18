# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/quota-common-utils.h

Purpose: `quota-common-utils.h` defines packed quota limit/metadata formats and helpers for quota dictionaries and quota configuration files.

Important APIs and types: `GF_QUOTA_CONF_VERSION`, `QUOTA_CONF_HEADER`, and `QUOTA_CONF_HEADER_1_1` identify supported conf formats. `gf_quota_conf_type_t` distinguishes usage and object quota records. `quota_limits_t` stores hard/soft limits; `quota_meta_t` stores size, file count, and directory count. APIs convert `data_t` to metadata, get/set metadata in dictionaries, and read/skip quota conf headers, versions, and GFIDs.

Control flow and state: no inline logic. Functions operate on caller-provided dictionaries, buffers, file descriptors, and metadata structs. Persistent behavior centers on the quota conf file wire format.

Dependencies and integration: includes `iatt.h` for inode type information and depends on dict/data APIs. Translators and glusterd quota logic use these helpers to share a stable binary metadata representation.

Risks: packed structs are ABI/wire-format sensitive and need endian/alignment awareness. Version parsing uses floats, which can be fragile. File descriptor reads must handle short reads and corrupt headers.

Test signals: quota tests should cover v1.1/v1.2 headers, usage versus object entries, dictionary round trips for file and directory IA types, null metadata detection, malformed/truncated files, and cross-architecture packed-size checks.
