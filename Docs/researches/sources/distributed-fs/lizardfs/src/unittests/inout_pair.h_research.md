# sources/distributed-fs/lizardfs/src/unittests/inout_pair.h

Purpose: Provides small macros for defining input/output variables and verifying serialization round trips in unit tests.

Important APIs/types/functions: `LIZARDFS_DEFINE_INOUT_PAIR`; `LIZARDFS_DEFINE_INOUT_VECTOR_PAIR`; `LIZARDFS_VERIFY_INOUT_PAIR`.

Control flow: Macro expansion creates `nameIn`/`nameOut` variables and emits `EXPECT_EQ` assertions with helpful labels.

State and persistence: Test local variables only.

Dependencies and integration: Used throughout protocol unit tests to reduce boilerplate.

Risks and test signals: Macros depend on naming convention and equality operators for tested types. They hide variable declarations, which can make failures harder to trace in complex tests.
