# sources/distributed-fs/lizardfs/src/common/integer_sequence_unittest.cc

Purpose: tests custom integer and index sequence generation.

Important APIs/types/functions: helper overloads `convert_to_vector`; tests `make_integer_sequence<int,100>` and `make_index_sequence<101>`.

Control flow: expected vectors are filled with `std::iota`; generated type packs are expanded into result vectors and compared.

State and persistence: test-only vectors.

Dependencies and integration: includes `integer_sequence.h`, `numeric`, and `gtest`.

Risks: only moderate sizes are tested; no explicit zero/one case tests even though template specializations exist.

Test signals: verifies normal recursive sequence generation for both value and index aliases.
