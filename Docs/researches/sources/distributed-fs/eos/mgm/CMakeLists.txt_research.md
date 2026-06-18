# sources/distributed-fs/eos/mgm/CMakeLists.txt

## Purpose

This CMake file defines the EOS MGM build: protobuf generation, the HTTP plugin, the main XRootD MGM plugin object library/module, tape garbage collection sources, CTA utility integration, admin/user command sources, REST/gRPC/FUSE/server components, install rules, and support executables/static Linux build targets.

## Important APIs, Types, and Functions

Major targets are `EosMgmProto-Objects`, `EosMgmHttp-Objects`, `EosMgmHttp-${XRDPLUGIN_SOVERSION}`, `XrdEosMgm-Objects`, `XrdEosMgm-${XRDPLUGIN_SOVERSION}`, `testschedulingtree`, `eos-config-inspect`, and Linux-only `XrdEosMgm-Static`. It uses `PROTOBUF_GENERATE_CPP` for `fusex.proto`, `set_source_files_properties(... HEADER_FILE_ONLY TRUE)` for command include fragments, `MGM_TGC_SRC_FILES` for tape garbage collection and `CtaUtils.cc`, and target link/compile definitions for XRootD, protobuf, gRPC, JSON, prometheus, LDAP, ZMQ, sparsehash, xxhash, EOS common/ns libraries, and daemon uid/gid definitions.

## Control Flow

CMake first establishes include paths, generates protobuf sources, builds an object library for protocol code, builds HTTP object/module targets, defines common MGM tape-GC sources, marks command `.inc` files as header-only, builds the large `XrdEosMgm-Objects` object library from many subsystem sources plus generated fusex sources, wraps it in an XRootD module, installs modules and tools, and conditionally builds Linux static/test support.

## State and Persistence Behavior

The file controls build artifacts and install destinations. It does not define runtime persistence directly, but it chooses which runtime subsystems are compiled into the MGM plugin, including namespace, quota, recycle, CTA/tape, REST, gRPC, monitoring, bulk request, placement, and traffic shaping components.

## Dependencies and Integration Points

It is the central integration point for EOS MGM with XRootD plugin ABI, protobuf/gRPC generated code, EOS common/server/static libraries, CTA SSI protobuf objects, REST gateway objects, prometheus exporter, ZLIB, LDAP, ZMQ, JSONCPP, sparsehash, and Linux-specific static linking. `CtaUtils.cc` is included through `MGM_TGC_SRC_FILES`.

## Risks

The main object target has a very large source list, so missing files or stale renamed header-only implementations break configuration or linking. Generated protobuf sources are included in the object target and must be available before compile. Link dependencies differ between object, module, and static targets, so symbol availability can diverge. Compile definitions for daemon uid/gid are public and propagate. Linux-only static target may hide non-Linux build gaps. Manual include directories are broad and can mask include-order issues.

## Test Signals

Build tests should configure from a clean tree, verify protobuf generation, build `XrdEosMgm-Objects`, plugin modules, `eos-config-inspect`, `testschedulingtree`, and Linux static target, run install dry-runs, and check dependency closure after adding/removing MGM subsystem files. Runtime smoke tests should load the XRootD MGM module and exercise HTTP, REST, gRPC, CTA/tape, and config inspection paths.
