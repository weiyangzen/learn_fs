# sources/distributed-fs/lizardfs/src/master/goal_config_loader_unittest.cc

Purpose: verifies default goal generation, old-format parsing, new-format typed parsing, and error detection for malformed goal configuration lines.

Important APIs/types/functions: `createSlice()` builds expected `Goal::Slice` values; `EXPECT_GOAL` checks size, name, and slice; `Defaults`, `OldFormat`, and `NewFormat` cover accepted syntax; `IncorrectLines` covers malformed structure, invalid ids/names/labels/types, bad erasure definitions, too many labels, and duplicates.

Control flow: tests load synthetic config strings through `goal_config::load()` and compare every significant parsed field, including default-filled goals.

State and persistence behavior: no persistent state; only in-memory parser outputs.

Dependencies/integration: depends on GoogleTest, `ParseException`, media labels, slice traits, and the parser API.

Risks and test signals: the suite is comprehensive for syntax but does not test `stream.bad()` I/O failures or localized character behavior of `std::isalnum`/`std::isspace`. It is the primary regression signal for config compatibility.
