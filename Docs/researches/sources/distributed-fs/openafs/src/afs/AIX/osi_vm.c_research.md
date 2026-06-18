# sources/distributed-fs/openafs/src/afs/AIX/osi_vm.c

Purpose: AIX VM/page-cache integration for OpenAFS vcache lifecycle, storeback, flush, smush, callback revocation, and truncate handling.

Important APIs and functions: `osi_VM_FlushVCache`, `osi_VM_StoreAllSegments`, `osi_VM_TryToSmush`, `osi_VM_FlushPages`, and `osi_VM_Truncate`.

Control flow: flush refuses busy vcaches, deletes any VM segment with `vms_delete`, releases credentials, and frees the AIX gnode. Storeback drops the vcache write lock and AFS global lock while calling `vm_writep` and `vms_iowait`, then reacquires locks and clears `CCore` fake-close state if present. Smush/flush/truncate call AIX VM page flush/release APIs across the file's segment range.

State and persistence: mutates `avc->segid`, `avc->vmh`, `avc->credp`, `avc->opens`, `avc->execsOrWriters`, `avc->linkData`, and vnode/gnode resources. Persistent data impact is indirect through page writeback or discarded dirty pages.

Dependencies and integration: called by common cache, flush, callback, and truncate paths; uses AIX VM APIs and `aix_gnode_rele`.

Risks and test signals: comments acknowledge consistency compromise around storeback to avoid AIX panics under load. Signals include no busy-vcache eviction, successful page writeback before store, and correct EOF truncation.
