# sources/distributed-fs/eos/namespace/utils/RmrfHelper.hh

## Purpose
Implements a non-atomic recursive directory deletion helper for namespace paths. It is intended for controlled cleanup scenarios where all files and subcontainers under a path should be removed.

## Important APIs, types, and functions
`RmrfHelper::nukeDirectory(eos::IView* view, const std::string& path)` obtains the target container, removes every direct file through `IFileMDSvc::removeFile()`, collects child container paths with `ContainerMapIterator`, recursively deletes children, then removes the container itself through `view->removeContainer(path)`.

## Control flow
The function deletes files first, records subcontainer paths before recursing, recursively processes each child path, and finally removes the current directory. Child paths are built by appending a slash when needed and the child key.

## State and persistence
This mutates namespace metadata through file and container services. It is explicitly non-atomic: partial deletion is possible if an exception, service failure, or crash occurs mid-recursion.

## Dependencies and integration points
Depends on namespace metadata interfaces and container/file map iterators. It integrates with administrative cleanup paths and test utilities that need recursive deletion.

## Risks and test signals
Risks include deleting the wrong subtree, partial state after failure, deep recursion stack growth, races with concurrent creates, and unchecked null container lookups. Tests should cover empty directories, nested trees, paths with/without trailing slash, missing paths, service exceptions, and concurrent mutation policy.
