<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/sound/sof/abi.h -->
# sources/distributed-fs/ceph-client/include/uapi/sound/sof/abi.h

Purpose: centralizes Sound Open Firmware ABI version constants, encoding/decoding helpers, compatibility tests, and magic numbers for IPC3 and IPC4 non-IPC data blobs.

Important APIs and types: `SOF_ABI_MAJOR`, `SOF_ABI_MINOR`, and `SOF_ABI_PATCH` define the current ABI version. `SOF_ABI_VER()`, `SOF_ABI_VERSION_MAJOR/MINOR/PATCH()`, and `SOF_ABI_VERSION_INCOMPATIBLE()` encode and compare the `MMmmmppp` 32-bit format. `SOF_ABI_MAGIC` and `SOF_IPC4_ABI_MAGIC` identify IPC3 and IPC4 data.

Control flow: topology and firmware blob parsers read an ABI/magic field, reject incompatible major versions, and use minor/patch to gate backward-compatible feature handling.

State and persistence: no runtime state. These constants are persisted in firmware, topology, and component private data.

Dependencies and integration points: depends on Linux types and is included by SOF topology and manifest headers, SOF drivers, and userspace tooling.

Risks and test signals: risks include incorrect version bumps for breaking changes, magic mixups between IPC3 and IPC4, and mask/shift errors. Test parsing old/new SOF topology blobs, incompatible major rejection, and tooling output matching kernel constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/sound/sof/abi.h -->
