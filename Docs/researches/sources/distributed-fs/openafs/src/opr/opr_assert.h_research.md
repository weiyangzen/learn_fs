# sources/distributed-fs/openafs/src/opr/opr_assert.h

Purpose: compatibility header that redefines the standard `assert` macro to use OpenAFS `opr_Assert`.

Important APIs/types/functions: includes `afs/opr.h` and defines `assert(ex)` as `opr_Assert(ex)`.

Control flow: no runtime logic beyond assertion macro expansion.

State and persistence: no state.

Dependencies/integration: used by code that wants standard-looking `assert` calls but OPR failure behavior and formatting.

Risks and test signals: it overrides `assert` regardless of prior definitions, so include order can matter. Compile and assertion-failure tests validate behavior.
