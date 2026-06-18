# sources/cloud-native/overlaybd/src/overlaybd/tar/erofs/test/erofs_stress_base.h

Purpose: declarations for the EROFS stress-test model, generator interface, host-file wrapper, and base runner.

Important APIs/types/functions: constants define image size, sector size, maximum generated name lengths, and `.wh.` prefix. `NODE_TYPE` distinguishes directory, regular file, and whiteout model nodes. `StressNode` stores path, xattrs, content hash, type, and `stat`; `equal` performs detailed comparisons. `StressHostFile` owns a Photon file used during host generation. `in_mem_meta` carries generated uid/gid/mtime data. `StressGenInter` is the virtual contract for generating and verifying per-file/per-directory metadata and layout. `StressFsTree` owns expected nodes and exposes add/query/name/type helpers. `StressBase` owns the test workdir, host filesystem, layer count, expected tree, and `run`.

Control flow: derived stress cases implement `StressGenInter`; `StressBase` invokes those hooks while building layers and while verifying mounted EROFS files. `StressFsTree::query_delete_node` validates an observed node and removes it, making an empty tree the final success condition.

State and persistence: the header models in-memory expected state only; persistence is performed by `erofs_stress_base.cpp` through host files, tar layers, and LSMT sidecars. `StressHostFile` owns an open Photon file and closes/deletes it in its destructor.

Dependencies/integration: depends on C++ STL maps/strings, Photon filesystem/localfs APIs, Photon logging, gtest, LSMT file interfaces, and EROFS FS declarations. It is consumed by both the shared implementation and `erofs_stress.cpp`.

Risks: `StressHostFile::~StressHostFile` assumes `file` is non-null and will dereference null if construction failed. `StressNode(StressNode*)` does not copy `type` or `node_stat`, which would be hazardous if used for deep copies. `StressNode::equal` compares mtimes exactly, so host tar and EROFS extraction must preserve second-level times precisely. The `is_emtry` typo is part of the public helper interface.

Test signals: no standalone tests; all stress test coverage depends on the correctness of this model and interface.
