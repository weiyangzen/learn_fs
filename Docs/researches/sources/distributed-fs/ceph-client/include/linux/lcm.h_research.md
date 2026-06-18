# sources/distributed-fs/ceph-client/include/linux/lcm.h

Purpose: declares least-common-multiple helpers for unsigned long values.

Important APIs and types: `lcm()` computes the least common multiple, and `lcm_not_zero()` handles zero inputs with nonzero semantics; both are marked `__attribute_const__`.

Control flow: callers use these helpers in arithmetic sizing/timing paths where the implementation can be optimized as a pure function.

State and persistence: no state is kept.

Dependencies and integration points: depends only on compiler attributes and integrates with generic math consumers.

Risks and test signals: risks are overflow and zero-handling expectations. Test small values, coprime values, common-factor values, zero inputs, and architecture word-size behavior.
