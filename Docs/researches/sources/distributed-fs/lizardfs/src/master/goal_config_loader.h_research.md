# sources/distributed-fs/lizardfs/src/master/goal_config_loader.h

Purpose: declares the goal configuration parser API and compatibility default constant.

Important APIs/types/functions: `goal_config::kMaxCompatibleGoal` caps old-style default wildcard copies at five; `load(std::istream &)`, `load(std::istream &&)`, `parseLine()`, and `defaultGoal()` are the exposed parser helpers.

Control flow: callers load a stream or parse individual lines, then consume the returned id-to-`Goal` map.

State and persistence behavior: no state. Parsed goals become runtime configuration elsewhere.

Dependencies/integration: includes `common/goal.h` and standard containers/character helpers. Used by master config loading and chunk placement tests.

Risks and test signals: parser functions throw `ParseException`, so callers must surface configuration failures clearly. Tests should confirm rvalue/lvalue stream overload parity and default goal cap behavior.
