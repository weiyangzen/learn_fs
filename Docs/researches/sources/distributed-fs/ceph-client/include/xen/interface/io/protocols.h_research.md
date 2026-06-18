# sources/distributed-fs/ceph-client/include/xen/interface/io/protocols.h

Purpose: declares string constants naming Xen IO protocol ABI layouts and selects a native ABI string for the compiling architecture.

Important APIs/types/functions: `XEN_IO_PROTO_ABI_X86_32`, `XEN_IO_PROTO_ABI_X86_64`, `XEN_IO_PROTO_ABI_POWERPC64`, `XEN_IO_PROTO_ABI_ARM`, and architecture-selected `XEN_IO_PROTO_ABI_NATIVE`.

Control flow: frontend and backend protocol setup code publishes or reads ABI strings, often in XenStore, to know how ring request/response structures are laid out. Preprocessor conditionals select the native string at compile time.

State and persistence: no runtime state is stored here. ABI strings may persist in XenStore device nodes for the connection lifetime.

Dependencies and integration points: included by protocols such as pvUSB that expose a `protocol` XenStore node. It integrates with build architecture macros and mixed frontend/backend ABI negotiation.

Risks: unsupported architectures hit `#error arch fixup needed here`. Native ABI is not always the peer ABI; backends must honor the negotiated string rather than assuming host native layout. String changes are ABI-breaking.

Test signals: compile tests for each supported architecture macro, XenStore protocol node validation, and cross-ABI frontend/backend tests where possible.
