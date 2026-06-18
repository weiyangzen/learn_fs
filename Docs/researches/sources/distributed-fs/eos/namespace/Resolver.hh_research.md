## sources/distributed-fs/eos/namespace/Resolver.hh

Purpose: Declares namespace resolver helpers for console protobuf container specs and file identifier strings.

Important APIs and types: aliases `ContainerSpecificationProto` to the console protobuf type and exposes static `Resolver::resolveContainer` and `Resolver::retrieveFileIdentifier`.

Control flow: header documents that container resolution requires the caller to hold the view mutex. String resolution recognizes explicit id prefixes.

State and persistence: no owned state.

Dependencies and integration: includes namespace macros, `MDException`, identifier types, `IView`, and `proto/Ns.pb.h`; forward-declares `XrdOucString`.

Risks: API returns shared metadata objects whose locking/lifetime rules are defined by the view/service implementation. Mutex precondition is external and easy to miss.

Test signals: compile with console protobuf definitions and behavior tests matching `Resolver.cc`.
