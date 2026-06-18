# sources/distributed-fs/ceph/src/osd/ClassHandler.cc

## Purpose
`ClassHandler.cc` implements dynamic loading, registration, dependency resolution, execution, and shutdown for OSD object classes (`libcls_*`). Object classes provide methods and filters that can be invoked by OSD operations.

## Important APIs, Types, and Control Flow
`open_class()` locks the handler, checks configured permission via `_get_class()`, loads the class if needed, and returns its `ClassData`. `open_all_classes()` scans `osd_class_dir` for files matching `libcls_*` plus the platform shared-library suffix and opens permitted classes. `_get_class()` creates metadata and marks whether it is in the default allowed list. `_load_class()` calls `dlopen`, reads optional `class_deps`, recursively loads missing dependencies, invokes `__cls_init`, and marks the class open. Registration functions add methods and filters during initialization. `ClassMethod::exec()` handles both C++ and C object-class ABIs through a `std::variant`, claiming C ABI malloc output into a `bufferlist`.

## State and Persistence Behavior
State is process-local: the `classes` map stores class status, dlopen handle, method/filter maps, dependency sets, and allowed flag. `shutdown()` closes loaded handles and clears all class metadata. There is no durable persistence in this file.

## Dependencies and Integration Points
It depends on Ceph config (`osd_class_dir`, load/default lists), logging, `dlfcn` compatibility, object-class ABI definitions, and the global Ceph context. `ClassHandler::get_instance()` returns a singleton, with a Crimson-specific local context path.

## Risks and Test Signals
Risks include loading unpermitted classes, dependency recursion failures, class registration under the wrong name, ABI memory ownership mistakes, and iterator invalidation during shutdown/unregister. Tests should cover load allow/deny lists, missing `.so`, dlopen failure with existing file, dependency chains, registration and execution of C and C++ methods, filter registration, `open_all_classes()` directory scanning, and shutdown idempotence.
