<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/DisposalCleaner.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/DisposalCleaner.h

Purpose: Declares the disposal cleanup helper.

Important APIs/types: `DisposalCleaner::OnItemFn` callback receives node, entry name, and mirrored flag and returns a bool decision. Public `run` walks nodes with the callback, and static `unlinkFile` removes an item. Private `walkNode` implements per-node traversal.

Control flow/state/persistence: The class has no member state. It performs remote metadata operations during `run`.

Dependencies/integration: Depends on node handles and BeeGFS operation errors. Used by maintenance tools or services cleaning disposal directories.

Risks/test signals: Callback behavior defines deletion policy. Tests should validate callback invocation order, mirrored flag propagation, and error propagation from node walks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/DisposalCleaner.h -->
