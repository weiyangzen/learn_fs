# sources/compression/zlib/contrib/puff/puff.h

Purpose: This header defines the standalone public interface for the puff raw DEFLATE inflater and carries the zlib-style license for the puff component.

Important APIs, types, and functions: It defines `NIL` as `((unsigned char *)0)` when absent, enabling the sizing-only mode documented in `puff.c`. It declares `int puff(unsigned char *dest, unsigned long *destlen, const unsigned char *source, unsigned long *sourcelen)`.

Control flow: The header has no runtime control flow. Its include behavior is minimal: only `NIL` is guarded, and there is no conventional whole-header include guard because the declarations are idempotent.

State and persistence: No state is stored here. State ownership belongs to callers through source/destination buffers and length pointers passed into `puff()`.

Dependencies and integration points: Used by `puff.c`, `pufftest.c`, and CMake puff targets. Because it does not include system headers, consumers must provide compatible standard C types implicitly available from their compilation environment.

Risks: The absence of a full include guard is low risk for this simple declaration but differs from typical project style. `NIL` is a macro in the global namespace and could conflict with callers that use a different sentinel. The ABI fixes lengths as `unsigned long`.

Test signals: Build tests compile consumers against shared and static puff targets. Runtime tests indirectly validate that the declared prototype matches `puff.c`.
