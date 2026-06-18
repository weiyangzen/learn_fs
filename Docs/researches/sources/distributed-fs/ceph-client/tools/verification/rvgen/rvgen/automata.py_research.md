# sources/distributed-fs/ceph-client/tools/verification/rvgen/rvgen/automata.py

Purpose: `automata.py` parses Graphviz DOT deterministic or hybrid automata into normalized Python state/event/transition data used by rvgen generators.

Important types and functions: `_StateConstraintKey` and `_EventConstraintKey` distinguish state invariants from edge guards/resets in the `constraints` dictionary. `AutomataError` reports validation failures. `Automata.__init__()` loads DOT lines, derives model name, states, initial/final states, events, environment variables, transition matrix, constraints, and start-event metadata. Parsing helpers find node/event regions, extract constraints using regexes, infer environment units/storage needs, build the matrix, and identify events that always return to initial state or only run from initial state.

Control flow and integration: `Dot2c` and `dot2k` subclass `Automata` to format C model data and kernel monitor skeletons. Hybrid automata use constraints of the form `env op value` and `reset(env)` on labels; state labels can carry invariants.

State and dependencies: state is per parser object. Dependencies are DOT formatting conventions from RV docs and Python regex/string parsing. Risks include fragile parsing based on token positions, only supporting limited constraint/reset counts, unescaped labels being converted directly into C identifiers, and no graph determinism conflict detection beyond matrix overwrite behavior. Test signals are successful parsing of valid `.dot`/`.gv`, expected `AutomataError` on malformed specs, correct states/events ordering, and generated matrix matching DOT transitions.
