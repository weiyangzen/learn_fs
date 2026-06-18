# sources/distributed-fs/ceph/src/client/CMakeLists.txt

## Purpose
This CMake file defines Ceph's static `client` library target from core client-side source files and links it to required internal and external libraries.

## Important APIs, Types, And Functions
`libclient_srcs` lists client implementation sources: `Client.cc`, `Dentry.cc`, `Fh.cc`, `Inode.cc`, `MetaRequest.cc`, `ClientSnapRealm.cc`, `MetaSession.cc`, `Trace.cc`, `posix_acl.cc`, `Delegation.cc`, and `FSCrypt.cc`. `add_library(client STATIC ${libclient_srcs})` creates the target. `target_link_libraries(client ...)` links `legacy-option-headers`, `osdc`, `Boost::locale`, `ICU::uc`, and `ICU::i18n`.

## Control Flow And State
This is build graph state, not runtime logic. The file collects the implementation units that form the Ceph client library and declares link dependencies needed by downstream targets.

## Dependencies And Integration Points
The target integrates client metadata/session/inode/dentry/FH logic with OSD client code and localization/text dependencies from Boost.Locale and ICU. It is likely consumed by higher-level Ceph tools or libraries that need filesystem client behavior.

## Risks And Test Signals
Risks include missing source additions when new client features are introduced, dependency ordering or target visibility problems, and static library consumers failing to link ICU/Boost symbols. Test signals are clean CMake configure/generate, successful `client` target builds, and downstream link tests for binaries using client metadata, ACL, delegation, snapshot realm, and encryption code.
