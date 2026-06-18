<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/sound/sof/header.h -->
# sources/distributed-fs/ceph-client/include/uapi/sound/sof/header.h

Purpose: defines generic SOF ABI headers and manifest TLV containers for non-IPC component data and topology manifest metadata.

Important APIs and types: `sof_abi_hdr` carries magic, type/parameter ID, payload size, ABI version, reserved words, and flexible `data[]`. `sof_manifest_tlv` is a little-endian TLV item. `sof_manifest` records ABI major/minor/patch, TLV count, and flexible items. `SOF_MANIFEST_DATA_TYPE_NHLT` identifies NHLT data payloads.

Control flow: topology/firmware parsers validate magic and ABI, dispatch payloads by `type`, and walk variable-size TLV items in the manifest to extract optional data such as NHLT.

State and persistence: no state in the header; the structs are serialized into topology or firmware data and become runtime component private data only after parsing.

Dependencies and integration points: depends on Linux integer and endian types. It integrates with SOF IPC3/IPC4 component params, topology manifests, NHLT endpoint data, and userspace SOF topology tooling.

Risks and test signals: risks include flexible-array length overflow, missing reserved-zero validation, little-endian TLV parsing, and ABI/magic mismatches. Test malformed TLV counts/sizes, IPC3 vs IPC4 data, NHLT extraction, and 32/64-bit packed layout assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/sound/sof/header.h -->
