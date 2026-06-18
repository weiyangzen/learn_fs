<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/FuseServer/Namespace.hh -->
# sources/distributed-fs/eos/mgm/FuseServer/Namespace.hh

Purpose: Defines the namespace macros used by the MGM FUSE server headers/implementations so classes such as `FuseServer::Caps`, `Clients`, `Flush`, and `Lock` live under `eos::mgm`.

Important APIs/types/functions: `USE_EOSMGMNAMESPACE` expands to `using namespace eos::mgm;`. `EOSMGMNAMESPACE_BEGIN` opens `namespace eos { namespace mgm {`, and `EOSMGMNAMESPACE_END` closes it. Despite the path under `FuseServer`, this header defines the generic MGM namespace macros, not a distinct FUSE subnamespace.

Control flow: There is no runtime control flow. It is a preprocessor include with an include guard.

State and persistence behavior: No runtime state or persistence.

Dependencies and integration points: Included throughout MGM and FUSE server code to avoid spelling namespace blocks manually. The listed FUSE headers use `EOSFUSESERVERNAMESPACE_BEGIN`, which is resolved through namespace macro definitions elsewhere in the MGM include chain; this local header is the base MGM namespace helper.

Risks: Namespace macros hide the actual namespace structure from tools and can be confusing when combined with similarly named FUSE-server macros. `USE_EOSMGMNAMESPACE` introduces a broad using directive and should be avoided in headers that may leak it to consumers. Tests are compile-time only: include-order checks and namespace qualification builds are the practical signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/FuseServer/Namespace.hh -->
