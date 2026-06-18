# sources/distributed-fs/ceph-client/lib/zlib_inflate/inffast.h

Purpose: Internal declaration for the inflate fast decoder.

Important APIs:
- Declares `inflate_fast(z_streamp strm, unsigned start)`.

Control flow: No runtime logic. Included by `inflate.c` to call the optimized decode loop.

State and persistence: No state.

Dependencies and integration:
- Relies on zlib stream types already visible from including context.
- Not a public API; callers should use `<linux/zlib.h>`.

Risks:
- Signature must stay synchronized with `inffast.c` and `inflate.c` caller assumptions.

Test signals:
- Compile/link validation.
- Fast-path inflate coverage in `inflate.c` tests.
